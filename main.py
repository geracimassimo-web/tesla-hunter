import os
import json
import urllib.parse
import time
import requests 

# ==========================================
# 🛠️ CONFIGURAZIONE FILTRI & CREDENZIALI
# ==========================================
CHAT_ID = "2022439793"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY") # La tua nuova chiave proxy

MODELLO = "m3"            
PREZZO_MASSIMO = 36000    
KM_MASSIMI = 80000        
ANNO_MINIMO = 2021        
FILE_VISTI = "visti.json"
# ==========================================

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def carica_auto_viste():
    if os.path.exists(FILE_VISTI):
        with open(FILE_VISTI, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salva_auto_viste(lista_viste):
    with open(FILE_VISTI, "w") as f:
        json.dump(lista_viste, f, indent=4)

def analizza_inventario_tesla():
    visti = carica_auto_viste()
    nuovi_visti = list(visti)
    
    query_struttura = {
        "query": {
            "model": MODELLO,
            "condition": "used",
            "options": {},
            "arrangeby": "Price",
            "order": "asc",
            "market": "IT",
            "language": "it",
            "super_region": "europe"
        },
        "offset": 0,
        "count": 80
    }
    
    query_iniziale = urllib.parse.quote(json.dumps(query_struttura))
    url_api_tesla = f"https://www.tesla.com/inventory/api/v1/inventory-results?query={query_iniziale}"
    
    # Creiamo l'URL "Ponte" per far fare la chiamata dal proxy
    url_scraper_api = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={urllib.parse.quote(url_api_tesla)}"
    
    count_totale_filtrate = 0
    count_vecchie = 0
    count_nuove = 0

    try:
        # Aumentiamo il timeout a 60 secondi perché il proxy ci mette un po' di più a instradare la chiamata
        response = requests.get(url_scraper_api, timeout=60)
        response.raise_for_status()
        dati = response.json()
        
        if not dati.get("results"):
            invia_telegram("ℹ️ Nessuna Tesla usata disponibile nell'inventario generale.")
            return

        for auto in dati["results"]:
            vin = auto.get("VIN")
            prezzo = auto.get("Price", 0)
            chilometri = auto.get("Odometer", 0)
            anno = int(auto.get("Year", 0))
            allestimento = auto.get("TrimName", "Standard")
            colore = auto.get("Paint", "N/D")
            
            if prezzo > PREZZO_MASSIMO or chilometri > KM_MASSIMI or anno < ANNO_MINIMO:
                continue 
            
            count_totale_filtrate += 1
            
            if vin in visti:
                count_vecchie += 1
                continue 
            
            count_nuove += 1
            nuovi_visti.append(vin)
            
            link_auto = f"https://www.tesla.com/it_IT/inventory/used/{MODELLO}?id={vin}"
            
            messaggio_auto = (
                f"🚗 <b>NUOVA TESLA INVENTARIO!</b>\n\n"
                f"• <b>Modello:</b> Model {MODELLO.upper()} {allestimento}\n"
                f"• <b>Prezzo:</b> {prezzo:,} €\n"
                f"• <b>KM:</b> {chilometri:,} km\n"
                f"• <b>Anno:</b> {anno}\n"
                f"• <b>Colore:</b> {colore}\n\n"
                f"🔗 <a href='{link_auto}'>Apri Annuncio Ufficiale</a>"
            )
            invia_telegram(messaggio_auto)
            time.sleep(2) 

        resoconto = (
            f"📊 <b>Resoconto Giornaliero Tesla</b>\n"
            f"• Auto totali corrispondenti ai tuoi filtri: <b>{count_totale_filtrate}</b>\n"
            f"• Già viste in precedenza (scartate): <b>{count_vecchie}</b>\n"
            f"• Nuove opportunità inviate oggi: <b>{count_nuove}</b>"
        )
        invia_telegram(resoconto)
        
        salva_auto_viste(nuovi_visti)

    except Exception as e:
        invia_telegram(f"⚠️ Errore durante lo screening dell'inventario: {e}")

if __name__ == "__main__":
    analizza_inventario_tesla()
