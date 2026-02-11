import csv

# --- DE HERSENEN (De Functie) ---
# Hier definiëren we de logica. Dit blokje code doet NIETS totdat we het aanroepen.
def bepaal_categorie(omschrijving):
    # Alles naar kleine letters, anders is "Shell" niet gelijk aan "shell"
    tekst = omschrijving.lower()

    # De wat-als logica
    if "albert heijn" in tekst or "jumbo" in tekst:
        return "Boodschappen"
    elif "shell" in tekst:
        return "Vervoer"
    elif "salaris" in tekst:
        return "Inkomen"
    else:
        # Alles wat we niet kennen
        return "Overig"

# --- DE MOTOR (De Loop) ---
def laad_data(bestandsnaam):
    print(f"Start met lezen van {bestandsnaam}...")
    transacties = []

    with open(bestandsnaam, mode='r') as f:
        lezer = csv.DictReader(f)

        # Hier gebeurt de magie: regel voor regel
        for regel in lezer:
            
            # STAP A: Haal de omschrijving op uit de huidige regel
            huidige_omschrijving = regel['Omschrijving']
            
            # STAP B: Roep je functie aan (de hersenen)
            nieuwe_categorie = bepaal_categorie(huidige_omschrijving)

            # STAP C: Maak een NIEUWE kolom aan in het geheugen
            # We voegen de key 'Categorie' toe aan de dictionary van deze regel
            regel['Categorie'] = nieuwe_categorie

            # STAP D: Voeg de complete regel (nu mét categorie) toe aan de lijst
            transacties.append(regel)

    return transacties

# --- STARTKNOP ---
if __name__ == "__main__":
    mijn_data = laad_data("dummy.csv")
    
    # We printen de eerste regel om te bewijzen dat 'Categorie' nu bestaat
    print("Eerste regel met categorie:", mijn_data[0])