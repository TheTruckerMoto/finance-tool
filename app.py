import streamlit as st
import pandas as pd
import os
from matcher import laad_en_schoon_bankdata, pas_matching_toe

st.set_page_config(page_title="Finance Tool", layout="wide")

st.title("💰 Vereniging Finance Dashboard")

# --- SECTIE 1: ZOEKTERMEN BEHEER ---
st.header("⚙️ Instellingen & Zoektermen")
with st.expander("Klik hier om de trefwoordenlijst aan te passen"):
    # Lees de huidige lijst
    if os.path.exists("zoektermen.csv"):
        regels_df = pd.read_csv("zoektermen.csv", sep=';', encoding='latin1')
        st.write("Huidige lijst:")
        st.dataframe(regels_df, use_container_width=True)
    
    # Formulier voor toevoegen
    with st.form("nieuwe_term_form"):
        c1, c2, c3 = st.columns(3)
        term = c1.text_input("Nieuw Trefwoord")
        gb = c2.number_input("Grootboeknummer", step=1, value=2000)
        cat = c3.text_input("Categorie")
        
        submit = st.form_submit_button("Voeg toe aan lijst")
        
        if submit and term:
            nieuwe_regel = pd.DataFrame([[term, gb, cat]], columns=['Zoekterm', 'Grootboek', 'Categorie'])
            # Schrijf terug naar CSV (header=False want we voegen toe)
            nieuwe_regel.to_csv("zoektermen.csv", mode='a', index=False, header=False, sep=';', encoding='latin1')
            st.success(f"'{term}' toegevoegd!")
            st.rerun()

st.divider()

# --- SECTIE 2: BANKDATA VERWERKEN ---
st.header("📊 Bankmutaties Verwerken")
uploaded_file = st.file_uploader("Upload je bank-CSV", type="csv")

if uploaded_file is not None:
    temp_path = "temp_upload.csv"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    data = laad_en_schoon_bankdata(temp_path)
    resultaat = pas_matching_toe(data, 'zoektermen.csv')

    # Statistieken
    onbekend_count = len(resultaat[resultaat['Grootboek'] == 2000])
    st.metric("Nog te doen (Onbekend)", onbekend_count)

    tab1, tab2 = st.tabs(["✅ Alles", "⚠️ Alleen Onbekend"])
    with tab1:
        st.dataframe(resultaat, use_container_width=True)
    with tab2:
        st.dataframe(resultaat[resultaat['Grootboek'] == 2000], use_container_width=True)