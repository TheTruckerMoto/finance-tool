import pandas as pd

def laad_en_schoon_bankdata(bestandsnaam):
    # We lezen de 34 kolommen in. 
    # Let op: de 'sep' (separator) moet vaak ';' zijn bij Nederlandse banken.
    # We voegen 'encoding' toe om die vervelende 0xeb fout te voorkomen
    # 'latin1' of 'ISO-8859-1' werkt meestal voor NL bankbestanden
    df = pd.read_csv(bestandsnaam, sep=';', encoding='latin1')

    # De 4 kolommen die we écht nodig hebben (exacte namen uit jouw lijst)
    relevante_kolommen = [
        'Datum', 
        'Bedrag', 
        'Naam tegenpartij', 
        'Omschrijving - 1'
    ]

    # We maken een nieuwe 'subset' van de data
    df_gefilterd = df[relevante_kolommen].copy()

    # Bonus: Bedrag omzetten naar een echt getal (Python rekent niet met tekst)
    # Soms staat er een komma in de CSV, die maken we een punt voor de computer
    if df_gefilterd['Bedrag'].dtype == 'object':
        df_gefilterd['Bedrag'] = df_gefilterd['Bedrag'].str.replace(',', '.').astype(float)

    return df_gefilterd

def pas_matching_toe(bank_df, zoektermen_bestandsnaam):
    # 1. Laad je trefwoordenlijst
    regels_df = pd.read_csv(zoektermen_bestandsnaam, sep=';')
    
    # We maken een nieuwe kolom 'Grootboek' en zetten die standaard op 2000 (Vraagposten)
    bank_df['Grootboek'] = 2000
    bank_df['Categorie'] = "Onbekend"

    # 2. De Loop: We gaan elke bankregel langs
    for i, bank_regel in bank_df.iterrows():
        omschrijving = str(bank_regel['Omschrijving - 1']).lower()
        tegenpartij = str(bank_regel['Naam tegenpartij']).lower()
        
        # Check elke zoekterm uit je lijst
        for j, zoek_regel in regels_df.iterrows():
            term = str(zoek_regel['Zoekterm']).lower()
            
            # Als de term in de omschrijving OF in de naam staat: match!
            if term in omschrijving or term in tegenpartij:
                bank_df.at[i, 'Grootboek'] = zoek_regel['Grootboek']
                bank_df.at[i, 'Categorie'] = zoek_regel['Categorie']
                break # Stop met zoeken als we een match hebben gevonden
                
    return bank_df

# Update je test-gedeelte onderaan:
if __name__ == "__main__":
    try:
        data = laad_en_schoon_bankdata('anonieme_bank.csv')
        # NIEUW: Match de data
        gematched_data = pas_matching_toe(data, 'zoektermen.csv')
        
        print("\n✅ Matching voltooid! Resultaat:")
        print(gematched_data[['Datum', 'Bedrag', 'Omschrijving - 1', 'Grootboek', 'Categorie']].head())
    except Exception as e:
        print(f"❌ Fout bij matching: {e}")