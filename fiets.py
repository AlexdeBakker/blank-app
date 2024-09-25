import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Laad de data
df = pd.read_csv('players_19.csv')

# Categorieën voor posities
aanval_posities = ['ST', 'CF', 'LW', 'RW', 'LF', 'RF']
middenveld_posities = ['CAM', 'CM', 'LM', 'RM', 'CDM', 'LAM', 'RAM', 'LCM', 'RCM']
verdediging_posities = ['CB', 'LB', 'RB', 'LWB', 'RWB', 'LCB', 'RCB', 'LDM', 'RDM']
keeper_posities = ['GK']

# Voeg de optie voor alle posities toe
positie_categorieen = ['Alle posities', 'Aanval', 'Middenveld', 'Verdediging', 'Keeper']

# Titel van de applicatie
st.title("FIFA 19 Spelerstatistieken - Ontdek de Beste Spelers")

# Dropdown-menu voor positie categorie
positie_categorie = st.selectbox('Kies een categorie', options=positie_categorieen)

# Filter de data op basis van de geselecteerde categorie
if positie_categorie == 'Aanval':
    filtered_df = df[df['player_positions'].apply(lambda x: any(pos in x for pos in aanval_posities))]
elif positie_categorie == 'Middenveld':
    filtered_df = df[df['player_positions'].apply(lambda x: any(pos in x for pos in middenveld_posities))]
elif positie_categorie == 'Verdediging':
    filtered_df = df[df['player_positions'].apply(lambda x: any(pos in x for pos in verdediging_posities))]
elif positie_categorie == 'Keeper':
    filtered_df = df[df['player_positions'].isin(keeper_posities)]
else:
    filtered_df = df  # Voor 'Alle posities', gebruik de volledige dataset

# Maak een kopie van de gefilterde DataFrame
filtered_df = filtered_df.copy()

# Slider voor algemene beoordeling
overall = st.slider('Selecteer een minimale algemene beoordeling (Overall)', min_value=50, max_value=99, value=75)
filtered_df = filtered_df[filtered_df['overall'] >= overall]

# Dropdown-menu voor clubs
club = st.selectbox('Selecteer een club om spelers te zien', options=['Alle clubs'] + list(df['club'].unique()))
if club != 'Alle clubs':
    filtered_df = filtered_df[filtered_df['club'] == club]

# Checkbox voor aanvallende statistieken
if st.checkbox('Toon aanvallende statistieken'):
    st.write(filtered_df[['short_name', 'shooting', 'passing', 'dribbling']])

# Checkbox voor verdedigende statistieken
if st.checkbox('Toon verdedigende statistieken'):
    st.write(filtered_df[['short_name', 'defending', 'physic']])


# Toevoegen van de kolom voor waarde per leeftijd, afgerond op hele getallen
filtered_df['waarde_per_leeftijd'] = (filtered_df['value_eur'] / filtered_df['age']).round(0)


# Lijst met gefilterde spelers weergeven
st.dataframe(filtered_df[['short_name', 'club', 'overall', 'potential', 'age', 'value_eur', 'waarde_per_leeftijd']])

# Spelers Vergelijker
st.title("Spelers Vergelijker")

# Aanvallers en verdedigers filteren op basis van de gedefinieerde posities
attackers = df[df['player_positions'].apply(lambda x: any(pos in x for pos in aanval_posities))]
defenders = df[df['player_positions'].apply(lambda x: any(pos in x for pos in verdediging_posities))]

# Zoekbalk voor aanvaller
st.subheader("Zoek een aanvaller:")
attacker_search = st.text_input("Voer een naam van een aanvaller in:")
if attacker_search:
    attacker_filtered = attackers[attackers['short_name'].str.contains(attacker_search, case=False)]
    attacker_names = attacker_filtered['short_name'].tolist()
else:
    attacker_names = []

# Dropdown voor aanvaller
attacker_name = st.selectbox("Selecteer een aanvaller:", attacker_names)

# Zoekbalk voor verdediger
st.subheader("Zoek een verdediger:")
defender_search = st.text_input("Voer een naam van een verdediger in:")
if defender_search:
    defender_filtered = defenders[defenders['short_name'].str.contains(defender_search, case=False)]
    defender_names = defender_filtered['short_name'].tolist()
else:
    defender_names = []

# Dropdown voor verdediger
defender_name = st.selectbox("Selecteer een verdediger:", defender_names)

# Controleren of de spelers zijn geselecteerd
if attacker_name and defender_name:
    attacker = attacker_filtered[attacker_filtered['short_name'] == attacker_name].iloc[0]
    defender = defender_filtered[defender_filtered['short_name'] == defender_name].iloc[0]

    # Berekenen van scores
    attacker_final_score = (attacker['shooting'] + attacker['pace'] + attacker['dribbling']) / 3
    defender_final_score = (defender['defending'] + defender['physic']) / 2  # Fysieke waarde van de verdediger

    # Vergelijking tussen uiteindelijke scores
    if attacker_final_score > defender_final_score:
        overall_result = f"{attacker_name} wint met een uiteindelijke score van {attacker_final_score:.2f} tegen {defender_final_score:.2f}."
    else:
        overall_result = f"{defender_name} wint met een uiteindelijke score van {defender_final_score:.2f} tegen {attacker_final_score:.2f}."

    st.markdown(f"*Uiteindelijke Score Vergelijking:* {overall_result}")  

    # Creëren van de gestapelde barplot
    fig = go.Figure()

    # Voeg de aanvaller toe aan de figuur
    fig.add_trace(go.Bar(
        x=['Aanvaller'],
        y=[attacker_final_score],
        name=attacker_name,
        marker_color='blue',
        hovertemplate=(
            f'Shooting: {attacker["shooting"]}<br>'
            f'Pace: {attacker["pace"]}<br>'
            f'Dribbling: {attacker["dribbling"]}<br>'  
            f'Totaal: {attacker_final_score:.2f}<extra></extra>'
        ),
    ))

    # Voeg de verdediger toe aan de figuur
    fig.add_trace(go.Bar(
        x=['Verdediger'],
        y=[defender_final_score],
        name=defender_name,
        marker_color='orange',
        hovertemplate=(
            f'Defending: {defender["defending"]}<br>'
            f'Physical: {defender["physic"]}<br>'
            f'Totaal: {defender_final_score:.2f}<extra></extra>'
        ),
    ))

    # Update layout voor de gestapelde barplot
    fig.update_layout(
        title='Uiteindelijke Score Vergelijking',
        barmode='stack',
        xaxis_title='Spelers',
        yaxis_title='Uiteindelijke Score',
        legend_title='Spelers',
    )

    # Plot de figuur in Streamlit
    st.plotly_chart(fig)
else:
    st.warning("Selecteer een aanvaller en verdediger om te vergelijken.")

# Optionele informatie in de sidebar
st.sidebar.header('Hulp en Informatie')
st.sidebar.info("""
    Gebruik de dropdown-menu's om spelers te filteren op basis van positie en club. 
    Je kunt ook de minimale algemene beoordeling aanpassen om spelers te vinden die aan jouw criteria voldoen.
""")
