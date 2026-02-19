import streamlit as st
import pandas as pd
import os
import datetime
import qrcode
from reportlab.pdfgen import canvas
from matcher import laad_en_schoon_bankdata, pas_matching_toe

# --- 1. CONFIGURATIE & MASTER DATA ---
st.set_page_config(page_title="Finance Tool DOA", layout="wide")

LEDEN_CSV = "ledenlijst.csv"
ZOEKTERMEN_CSV = "zoektermen.csv"
FACTUUR_MAP = "facturen_output"

# Het Rekeningschema is de 'Source of Truth' voor de categorieën
REKENINGSCHEMA = {
    1200: "Kruisposten", 2000: "Vraagposten", 4100: "Algemene kosten",
    4335: "Verzekering", 4600: "Bankkosten", 7000: "Bouw",
    7001: "AUC", 7002: "Kleding", 7003: "Grime", 7004: "Kinderoptocht",
    7005: "Investering", 7006: "Sponsorkosten", 7007: "AC",
    8000: "Kerstbomenactie", 8001: "Sponsoring", 8002: "Bouwshirts",
    8003: "Consumptiemunten", 8004: "Vrienden van DOA", 8005: "Contributie",
    8006: "Vest/Hoodie", 8010: "Supporttickets", 8015: "Bijdrage stichting"
}

if not os.path.exists(FACTUUR_MAP):
    os.makedirs(FACTUUR_MAP)

# --- 2. FUNCTIES ---

def bereken_tarief_logic(row, t_j, t_v, t_g, t_i):
    peildatum = datetime.datetime(2024, 1, 1)
    if str(row['Is_Gezin']).strip().upper() == "JA":
        return t_g, "Gezin"
    try:
        geb_datum = pd.to_datetime(row['Geboortedatum'], dayfirst=True)
        leeftijd = peildatum.year - geb_datum.year - ((peildatum.month, peildatum.day) < (geb_datum.month, geb_datum.day))
        return (t_j, "Jeugdlid") if leeftijd < 18 else (t_v, "Volwassen lid")
    except:
        return t_v, "Lidmaatschap"

# --- 3. UI & SIDEBAR ---
st.sidebar.title("⚙️ Instellingen")
t_jeugd = st.sidebar.number_input("Jeugdlid", value=15.00)
t_volwas = st.sidebar.number_input("Volwassen lid", value=25.00)
t_gezin = st.sidebar.number_input("Gezin", value=65.00)
t_inschr = st.sidebar.number_input("Inschrijfgeld", value=5.00)

st.title("💰 Finance Dashboard - De Oude Ambachten")
tab_bank, tab_leden, tab_zoektermen = st.tabs(["📊 Bankmutaties", "👥 Leden & Facturatie", "⚙️ Zoektermen"])

# --- TAB 1: BANKMUTATIES (DE FIX) ---
with tab_bank:
    uploaded_file = st.file_uploader("Upload Rabobank CSV", type="csv")
    
    if uploaded_file:
        # Stap 1: Bestand opslaan en verwerken
        temp_path = "temp_bank.csv"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Alleen inladen als het nog niet in de sessie staat om verspringen te voorkomen
        if 'bank_df' not in st.session_state:
            bank_data = laad_en_schoon_bankdata(temp_path)
            df = pas_matching_toe(bank_data, ZOEKTERMEN_CSV)
            df['Grootboek'] = df['Grootboek'].fillna(2000).astype(int)
            # Zet de eerste keer de categorieën goed
            df['Categorie'] = df['Grootboek'].map(REKENINGSCHEMA).fillna("Onbekend")
            st.session_state.bank_df = df

        # Stap 2: Dynamische dropdown opties
        gb_opties = sorted(list(set(list(REKENINGSCHEMA.keys()))))
        if os.path.exists(ZOEKTERMEN_CSV):
            z_df = pd.read_csv(ZOEKTERMEN_CSV, sep=';', encoding='utf-8-sig')
            extra_nrs = z_df['Grootboek'].dropna().unique().tolist()
            gb_opties = sorted(list(set(gb_opties + [int(n) for n in extra_nrs])))

        st.info("💡 Pas een Grootboeknummer aan en klik ergens buiten de cel. De categorie wordt direct bijgewerkt.")

        # Stap 3: De Data Editor met directe verwerking
        edited_df = st.data_editor(
            st.session_state.bank_df,
            column_config={
                "Grootboek": st.column_config.SelectboxColumn(
                    "Grootboek", 
                    options=gb_opties,
                    required=True
                ),
                "Categorie": st.column_config.TextColumn("Categorie (Systeem)", disabled=True)
            },
            disabled=["Datum", "Bedrag", "Naam tegenpartij", "Omschrijving"],
            width=1200,
            key="bank_editor"
        )

        # Stap 4: DE TRIGGER. We controleren of er wijzigingen zijn en voeren de map uit.
        # Dit zorgt ervoor dat de categorie-kolom ALTIJD de grootboek-kolom volgt.
        if not edited_df.equals(st.session_state.bank_df):
            edited_df['Categorie'] = edited_df['Grootboek'].map(REKENINGSCHEMA).fillna("Handmatig/Zoekterm")
            st.session_state.bank_df = edited_df
            st.rerun()

        if st.button("💾 Definitief opslaan naar CSV"):
            st.session_state.bank_df.to_csv("bank_verwerkt.csv", index=False, sep=';', encoding='utf-8-sig')
            st.success("Bestand 'bank_verwerkt.csv' is opgeslagen met de juiste categorieën!")

# --- TAB 3: ZOEKTERMEN ---
with tab_zoektermen:
    st.header("Beheer Zoektermen")
    if os.path.exists(ZOEKTERMEN_CSV):
        z_df = pd.read_csv(ZOEKTERMEN_CSV, sep=';', encoding='utf-8-sig')
        # Ook hier dynamisch toevoegen toestaan
        ed_z_df = st.data_editor(z_df, width=1000, num_rows="dynamic", key="z_editor")
        if st.button("💾 Zoektermen Opslaan"):
            ed_z_df.to_csv(ZOEKTERMEN_CSV, index=False, sep=';', encoding='utf-8-sig')
            st.success("Opgeslagen! De nieuwe nummers zijn nu ook beschikbaar bij de Bankmutaties.")
            st.rerun()

# Voeg "W&V" toe aan je tabs
tab_bank, tab_leden, tab_zoektermen, tab_wv = st.tabs(["📊 Bankmutaties", "👥 Leden & Facturatie", "⚙️ Zoektermen", "📈 W&V"])

with tab_wv:
    st.header("Winst & Verliesrekening 2024")
    
    if 'bank_df' in st.session_state:
        wv_df = st.session_state.bank_df.copy()
        
        # 1. Groeperen en omschrijvingen toevoegen
        totaal_per_gb = wv_df.groupby('Grootboek')['Bedrag'].sum().reset_index()
        totaal_per_gb['Omschrijving'] = totaal_per_gb['Grootboek'].map(REKENINGSCHEMA).fillna("Overige posten")
        
        # 2. Opsplitsen in Inkomsten en Uitgaven voor de visuals
        inkomsten = totaal_per_gb[totaal_per_gb['Bedrag'] > 0]
        uitgaven = totaal_per_gb[totaal_per_gb['Bedrag'] < 0]
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.subheader("Cijfers")
            display_wv = totaal_per_gb[['Omschrijving', 'Bedrag']].sort_values(by='Bedrag', ascending=False)
            st.dataframe(display_wv.style.format({'Bedrag': '€ {:.2f}'}), height=400)
            
            eind_saldo = totaal_per_gb['Bedrag'].sum()
            st.metric("Eindsaldo 2024", f"€ {eind_saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), delta=f"{eind_saldo:,.2f}")

        with col2:
            st.subheader("Visualisatie per Categorie")
            # We maken een chart die inkomsten (groen) en uitgaven (rood) laat zien
            st.bar_chart(data=totaal_per_gb, x='Omschrijving', y='Bedrag', color=None)

        # 3. Extra inzicht: Top 3 kostenposten
        st.divider()
        st.subheader("💡 Belangrijkste inzichten")
        if not uitgaven.empty:
            grootste_kosten = uitgaven.sort_values(by='Bedrag').iloc[0]
            st.write(f"De grootste kostenpost dit jaar is **{grootste_kosten['Omschrijving']}** met een totaal van **€ {abs(grootste_kosten['Bedrag']):,.2f}**.")
    else:
        st.warning("Upload eerst bankgegevens in de tab 'Bankmutaties'.")