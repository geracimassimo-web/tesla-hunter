import os
import json
import requests
import urllib.parse
import time

# ==========================================
# 🛠️ CONFIGURAZIONE FILTRI & CREDENZIALI
# ==========================================
CHAT_ID = "2022439793"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

MODELLO = "m3"            # "m3" per Model 3, "my" per Model Y
PREZZO_MASSIMO = 36000    # Imposta il tuo budget massimo in Euro
KM_MASSIMI = 80000        # Chilometri massimi desiderati
ANNO_MINIMO = 2021        # Anno minimo di immatricolazione
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
        json.dump(lista_vistes, f, indent=4)

def analizza_inventario_tesla():
    visti = carica_auto_viste()
    nuovi_visti = list(visti)
    
    # Costruiamo la richiesta ufficiale per l'API di Tesla Italia
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
    url_api = f"https://www.tesla.com/inventory/api/v1/inventory-results?query={query_iniziale}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    count_totale_filtrate = 0
    count_vecchie = 0
    count_nuove = 0

    try:
        response = requests.get(url_api, headers=headers, timeout=15)
        response.raise_for_status()
        dati = response.json()
        
        # Se non ci sono risultati nell'inventario
        if not dati.get("results"):
            invia_telegram("ℹ️ Nessuna Tesla usata disponibile nell'inventario generale.")
            return

        for auto in dati["results"]:
            # Estrazione dati sicura dall'API di Tesla
            vin = auto.get("VIN")
            prezzo = auto.get("Price", 0)
            chilometri = auto.get("Odometer", 0)
            anno = int(auto.get("Year", 0))
            allestimento = auto.get("TrimName", "Standard")
            colore = auto.get("Paint", "N/D")
            
            # 1. APPLICAZIONE FILTRI
            if prezzo > PREZZO_MASSIMO or chilometri > KM_MASSIMI or anno < ANNO_MINIMO:
                continue # Salta questa auto perché non rispetta i tuoi filtri
            
            count_totale_filtrate += 1
            
            # 2. CONTROLLO DUPLICATI VIA VIN
            if vin in visti:
                count_vecchie += 1
                continue # Salta la notifica perché l'avevi già vista nei giorni scorsi
            
            # Se arriva qui, l'auto è NUOVA
            count_nuove += 1
            nuovi_visti.append(vin)
            
            # Generazione del link diretto dell'auto
            link_auto = f"https://www.tesla.com/it_IT/inventory/used/{MODELLO}?id={vin}"
            
            # Messaggio di notifica per la nuova auto
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
            time.sleep(2) # Evita il ban per spam da Telegram

        # 3. INVIO RESOCONTO GIORNALIERO
        resoconto = (
            f"📊 <b>Resoconto Giornaliero Tesla</b>\n"
            f"• Auto totali corrispondenti ai tuoi filtri: <b>{count_totale_filtrate}</b>\n"
            f"• Già viste in precedenza (scartate): <b>{count_vecchie}</b>\n"
            f"• Nuove opportunità inviate oggi: <b>{count_nuove}</b>"
        )
        invia_telegram(resoconto)
        
        # Salviamo la nuova lista aggiornata per domani
        salva_auto_viste(nuovi_visti)

    except Exception as e:
        invia_telegram(f"⚠️ Errore durante lo screening dell'inventario: {e}")

if __name__ == "__main__":
    analizza_inventario_tesla()
