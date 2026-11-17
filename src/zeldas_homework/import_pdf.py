import pdfplumber
import pandas as pd
import re
from pathlib import Path

def extrahera_glosor(pdf_sökväg, excel_sökväg):
    data = []
    grammatik_data = [] # Ny lista för att samla grammatikraderna
    kategori = 1
    senaste_id = 0
    läser_grammatik = False # Vår strömbrytare
    
    with pdfplumber.open(pdf_sökväg) as pdf:
        for sida in pdf.pages:
            text = sida.extract_text(layout=True) 
            
            if not text:
                continue
                
            for rad in text.split('\n'):
                ren_rad = rad.strip()
                if not ren_rad:
                    continue
                
                # 1. Känn av om vi har kommit till grammatik-delen
                if ren_rad == "Grammatik" or ren_rad.startswith("Grammatik"):
                    läser_grammatik = True
                    continue # Hoppa till nästa rad så vi inte får med rubriken som data
                
                # 2. Om strömbrytaren är på, spara bara hela raden som den är
                if läser_grammatik:
                    grammatik_data.append({"Regler och Exempel": ren_rad})
                    continue
                
                # 3. Annars letar vi efter glosor och fraser precis som förut
                match = re.search(r'(\d+)\.\s+(.*)', ren_rad)
                
                if match:
                    id_nummer = int(match.group(1))
                    
                    if id_nummer < senaste_id:
                        kategori = 2
                    
                    senaste_id = id_nummer
                    resten_av_raden = match.group(2).strip()
                    
                    delar = re.split(r'\s{2,}|\s+\|\s+|(?<=[.!?])\s+(?=[A-ZÅÄÖ])', resten_av_raden)
                    
                    engelska = delar[0].strip() if len(delar) > 0 else ""
                    svenska = delar[1].strip() if len(delar) > 1 else ""
                    
                    data.append({
                        "Kategori": kategori,
                        "Engelska": engelska,
                        "Svenska": svenska
                    })

    # Skapa DataFrame för glosorna
    df_glosor = pd.DataFrame(data)
    df_glosor.insert(0, 'Unikt_ID', range(1, len(df_glosor) + 1))
    
    # KONTROLL: Se till att utdata-mappen faktiskt existerar
    excel_sökväg.parent.mkdir(parents=True, exist_ok=True)
    
    # För att skriva till flera flikar använder vi pd.ExcelWriter
    with pd.ExcelWriter(excel_sökväg, engine='openpyxl') as writer:
        # Skriv glosorna till den första fliken
        df_glosor.to_excel(writer, index=False, sheet_name="Veckans_Glosor")
        
        # Om vi hittade grammatik, skapa en egen flik för det
        if grammatik_data:
            df_grammatik = pd.DataFrame(grammatik_data)
            df_grammatik.to_excel(writer, index=False, sheet_name="Grammatik")
            
    print(f"✅ Klar! Extraherade {len(df_glosor)} ord/fraser till fliken 'Veckans_Glosor'.")
    if grammatik_data:
        print(f"📚 Extraherade även {len(grammatik_data)} rader grammatik till fliken 'Grammatik'.")


# 1. Definiera var PDF-filen hämtas
skript_mapp = Path(__file__).parent
pdf_sökväg = skript_mapp / "Homeworkfile" / "Engerskav47.pdf"

# 2. Definiera var Excel-filen ska dumpas (absolut sökväg)
utdata_mapp = Path(r"C:\Users\user\Documents\Zelda_homework\data")
excel_sökväg = utdata_mapp / "Veckans_Glosor.xlsx"

# Kör funktionen
extrahera_glosor(pdf_sökväg, excel_sökväg)