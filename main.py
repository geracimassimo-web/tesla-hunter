import os
import json
import time
from curl_cffi import requests

# Configurazione
CHAT_ID = "2022439793"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
FILE_VISTI = "visti.json"

MODELLO = "m3"
PREZZO_MASSIMO = 36000
KM_MASSIMI = 80000
ANNO_MINIMO = 2021

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "HTML"}
    # Per Telegram la richiesta base va bene
    requests.post(url, json=payload)

def analizza_inventario_tesla():
    visti = []
    if os.path.exists(FILE_VISTI):
        with open(FILE_VISTI, "r") as f:
            try: visti = json.load(f)
            except: visti = []

    # URL API pulito (senza proxy)
    url = "https://www.tesla.com/inventory/api/v1/inventory-results?query=%7B%22query%22%3A%7B%22model%22%3A%22m3%22%2C%22condition%22%3A%22used%22%2C%22arrangeby%22%3A%22Price%22%2C%22order%22%3A%22asc%22%2C%22market%22%3A%22IT%22%2C%22language%22%3A%22it%22%2C%22super_region%22%3A%22europe%22%7D%2C%22offset%22%3A0%2C%22count%22%3A80%7D"

    try:
        # La chiave è qui: impersonate="chrome" inganna i sistemi anti-bot
        response = requests.get(url, impersonate="chrome", timeout=20)
        response.raise_for_status()
        dati = response.json()
        
        nuovi_visti = list(visti)
        
        for auto in dati.get("results", []):
            vin = auto.get("VIN")
            prezzo = auto.get("Price", 0)
            
            if prezzo <= PREZZO_MASSIMO and auto.get("Odometer", 0) <= KM_MASSIMI:
                if vin not in visti:
                    # Notifica
                    invia_telegram(f"🚗 Nuova Tesla: {prezzo}€ - {auto.get('TrimName')}")
                    nuovi_visti.append(vin)
                    time.sleep(2)

        with open(FILE_VISTI, "w") as f:
            json.dump(nuovi_visti, f)

    except Exception as e:
        invia_telegram(f"Errore tecnico: {str(e)}")

if __name__ == "__main__":
    analizza_inventario_tesla()
