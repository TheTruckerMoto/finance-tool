from fpdf import FPDF

def maak_factuur(klant_naam, bedrag, factuur_nummer):
    # 1. Setup PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 2. Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=10, txt="OFFICIËLE FACTUUR", ln=1, align="C")
    
    # 3. Inhoud
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(w=0, h=10, txt=f"Ontvanger: {klant_naam}", ln=1)
    pdf.cell(w=0, h=10, txt=f"Factuurnummer: {factuur_nummer}", ln=1)
    
    # 4. Bedrag
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(w=0, h=10, txt=f"Totaalbedrag: EUR {bedrag:.2f}", ln=1)
    
    # 5. Opslaan
    pdf.output(f"Factuur_{factuur_nummer}.pdf")
    print(f"Bestand Factuur_{factuur_nummer}.pdf is aangemaakt!")

if __name__ == "__main__":
    # Test run
    maak_factuur("Bodhie Test", 99.95, "2024001")