import requests
import json
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = "2022439793"

MAX_PRICE = 31500
MIN_YEAR = 2022

SEEN_FILE = "seen.json"


def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


# ---------------- ANTI DUPLICATI ----------------

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


# ---------------- FILTRO ----------------

def is_valid(title, price, year):
    t = title.lower()

    if "model y" not in t:
        return False

    valid_keywords = [
        "long range",
        "performance",
        "dual motor",
        "awd"
    ]

    if not any(k in t for k in valid_keywords):
        return False

    if price and price > MAX_PRICE:
        return False

    if year and year < MIN_YEAR:
        return False

    return True


# ---------------- SUBITO (API REALE) ----------------

def get_subito():
    url = "https://api.subito.it/search"

    params = {
        "q": "tesla model y",
        "lim": 10
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    results = []

    try:
        r = requests.get(url, params=params, headers=headers)

        print("STATUS:", r.status_code)
        print("TEXT:", r.text[:500])  # primi 500 caratteri

        data = r.json()

        for item in data.get("items", []):
            title = item.get("subject", "")
            price = item.get("price", {}).get("value")
            link = item.get("url")

            results.append(f"{title} - {price}€\n{link}")

    except Exception as e:
        return [f"ERRORE SUBITO: {e}"]

    return results[:5]


# ---------------- TESLA API (CORRETTA) ----------------

def get_tesla():
    url = "https://www.tesla.com/inventory/api/v4/inventory-results"

    payload = {
        "query": {
            "model": "my",
            "condition": "used",
            "arrangeby": "Price",
            "order": "asc",
            "market": "IT",
            "language": "it",
            "super_region": "europe"
        },
        "offset": 0,
        "count": 50
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    results = []

    try:
        r = requests.post(url, json=payload, headers=headers)
        data = r.json()

        for car in data.get("results", []):
            price = car.get("InventoryPrice", 0)
            year = car.get("Year", 0)
            trim = car.get("TrimName", "")
            vin = car.get("VIN", "")

            title = f"Tesla Model Y {trim}"

            if not is_valid(title, price, year):
                continue

            link = f"https://www.tesla.com/it_IT/myorder/{vin}"

            results.append({
                "id": vin,
                "title": title,
                "price": price,
                "link": link,
                "source": "Tesla"
            })

    except:
        pass

    return results


# ---------------- MAIN ----------------

def main():
    seen = load_seen()

    all_results = []
    all_results += get_subito()
    all_results += get_tesla()

    new_results = [r for r in all_results if r["id"] not in seen]

    if not new_results:
        send("🔍 Nessuna nuova Tesla valida trovata")
        return

    msg = "🚗 TESLA NUOVE TROVATE:\n\n"

    for r in new_results:
        msg += f"{r['title']}\n"
        msg += f"💰 {r['price']}€\n"
        msg += f"🔗 {r['link']}\n"
        msg += f"📍 {r['source']}\n\n"

        seen.add(r["id"])

    save_seen(seen)
    send(msg)


if __name__ == "__main__":
    main()
