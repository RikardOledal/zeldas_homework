import pdfplumber
import pandas as pd
import re
from pathlib import Path

def extrahera_glosor(pdf_sökväg, excel_sökväg):
    data = []
    kategori = 1
    senaste_id = 0
    
    with pdfplumber.open(pdf_sökväg) as pdf:
        for sida in pdf.pages:
            text = sida.extract_text(layout=True) 
            
            if not text:
                continue
                
            for rad in text.split('\n'):
                match = re.search(r'(\d+)\.\s+(.*)', rad.strip())
                
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

    df = pd.DataFrame(data)
    df.insert(0, 'Unikt_ID', range(1, len(df) + 1))
    
    # KONTROLL: Se till att utdata-mappen faktiskt existerar innan vi sparar
    excel_sökväg.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(excel_sökväg, index=False, sheet_name="Veckans_Glosor")
    print(f"✅ Klar! Extraherade {len(df)} ord/fraser till {excel_sökväg}")


# 1. Definiera var PDF-filen hämtas (behålls relativt till skriptet)
skript_mapp = Path(__file__).parent
pdf_sökväg = skript_mapp / "Homeworkfile" / "Engerskav45.pdf"

# 2. Definiera var Excel-filen ska dumpas (absolut sökväg)
# Notera r:et framför strängen. Det säger åt Python att läsa backslash (\) som vanlig text.
utdata_mapp = Path(r"C:\Users\user\Documents\Zelda_homework\data")
excel_sökväg = utdata_mapp / "Veckans_Glosor.xlsx"

# Kör funktionen
extrahera_glosor(pdf_sökväg, excel_sökväg)