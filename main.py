import csv
from factuur_maker import maak_factuur

# --- CONFIGURATIE: HET REKENINGSCHEMA ---
# Dit is de ruggengraat van je boekhouding.
# Als penningmeester bepaal je hier welke potjes er zijn.
GROOTBOEK = {
    # OPBRENGSTEN (8xxx)
    "8000": "Omzet Contributie",
    "8010": "Omzet Bar/Kantine",
    
    # KOSTEN (4xxx)
    "4500": "Kosten Huisvesting (Zaalhuur)",
    "4600": "Kantoorkosten",
    "4700": "Kosten Activiteiten (Boodschappen)",
    
    # BALANS (1xxx) - Voor later
    "1100": "Bankrekening"
}

# --- DE HERSENEN (De Functie) ---
# Hier definiëren we de logica. Dit blokje code doet NIETS totdat we het aanroepen.
def bepaal_grootboekrekening(omschrijving):
    tekst = omschrijving.lower()

    if "albert heijn" in tekst or "jumbo" in tekst:
        return "4700"  # Kosten Activiteiten
        
    elif "zaalhuur" in tekst or "sporthal" in tekst:
        return "4500"  # Huisvesting

    # --- NIEUWE REGELS ---
    elif "shell" in tekst or "tankstation" in tekst:
        return "4600"  # Vervoer / Kantoorkosten (even als voorbeeld)
        
    elif "salaris" in tekst:
        return "8000"  # Omzet / Inkomen
    # ---------------------
        
    elif "contributie" in tekst:
        return "8000"  # Omzet
        
    else:
        return "9999"  # Onbekend
    
# --- Calculator ---
def maak_rapport(transacties):
    print("\n--- GROOTBOEK OVERZICHT ---")
    
    # We sorteren op nummer, dat leest makkelijker voor een boekhouder
    totalen = {}

    for regel in transacties:
        gb_nummer = regel['Grootboek']
        
        # --- HET VEILIGHEIDSNET ---
        try:
            # Probeer tekst naar getal te doen
            bedrag = float(regel['Bedrag'])
        except ValueError:
            # Als het mislukt (bijv. "Tientje"), doe dan dit:
            print(f"LET OP: Fout bedrag bij '{regel['Omschrijving']}'. Ik reken €0.00.")
            bedrag = 0.0
        # --- DE RICHTING BEPALEN (Bij/Af) ---
        type_boeking = regel['Type'] # We kijken in de kolom 'Type'
        
        # Als het 'Af' is, maken we het getal negatief (keer -1)
        if type_boeking == "Af":
            bedrag = bedrag * -1
        # --------------------------

        if gb_nummer in totalen:
            totalen[gb_nummer] += bedrag
        else:
            totalen[gb_nummer] = bedrag

    # Nu gaan we printen, maar we zoeken de NAAM erbij in onze GROOTBOEK config
    # We sorteren de sleutels (4500, 4700, 8000) zodat het netjes op volgorde staat
    for nummer in sorted(totalen.keys()):
        
        # Haal de naam op uit de config bovenaan. 
        # .get(nummer, "Onbekend") betekent: als nummer niet bestaat, zeg "Onbekend"
        rekening_naam = GROOTBOEK.get(nummer, "Onbekende Rekening")
        
        bedrag = totalen[nummer]
        
        # De f-string met opmaak:
        # {nummer:<5} betekent: reserveer 5 tekens ruimte voor het nummer (uitlijning)
        print(f"{nummer:<5} {rekening_naam}: €{bedrag:.2f}")

    return totalen

# --- DE MOTOR (De Loop) ---
def laad_data(bestandsnaam):
    print(f"Start met lezen van {bestandsnaam}...")
    transacties = []

    with open(bestandsnaam, mode='r') as f:
        lezer = csv.DictReader(f)

        # Hier gebeurt de magie: regel voor regel
        for regel in lezer:
            # LET OP: Vanaf hier alles een stukje naar rechts! (TAB)
            
            # Oude code: nieuwe_categorie = bepaal_categorie(...)
            # NIEUWE CODE:
            gb_nummer = bepaal_grootboekrekening(regel['Omschrijving'])
            
            # We slaan het op onder de kolom 'Grootboek'
            regel['Grootboek'] = gb_nummer
            
            transacties.append(regel)
            
    return transacties

# --- Genereer factuur leden functie ---
def genereer_contributie_facturen(bestandsnaam):
    print(f"\n--- Facturen genereren op basis van {bestandsnaam} ---")
    
    with open(bestandsnaam, mode='r') as f:
        lezer = csv.DictReader(f)
        for regel in lezer:
            naam = regel['Naam']
            bedrag = float(regel['Bedrag'])
            nummer = regel['Factuurnummer']
            
            # Hier gebruiken we weer onze vertrouwde factuur_maker!
            maak_factuur(naam, bedrag, nummer)
            print(f"Factuur aangemaakt voor {naam}")


# --- STARTKNOP ---
if __name__ == "__main__":
    print("1. Bankgegevens analyseren (dummy.csv)")
    print("2. Contributiefacturen maken (leden.csv)")
    
    keuze = input("Wat wil je doen? (1/2): ")

    if keuze == "1":
        mijn_data = laad_data("dummy.csv")
        maak_rapport(mijn_data)
    elif keuze == "2":
        genereer_contributie_facturen("leden.csv")
    else:
        print("Ongeldige keuze.")