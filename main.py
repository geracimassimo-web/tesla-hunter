import requests
import re

TELEGRAM_TOKEN = "8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc"
CHAT_ID = "2022439793"

MAX_PRICE = 31500
MIN_YEAR = 2022


def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


# ---------------- FILTRO ----------------

def is_valid(title, price):
    title = title.lower()

    if price and price > MAX_PRICE:
        return False

    if "model y" not in title:
        return False

    if "long range" not in title and "performance" not in title:
        return False

    return True


# ---------------- TESLA ----------------

def get_tesla():
    url = "https://www.tesla.com/it_IT/inventory/used/my?arrangeby=plh&zip=20100"

    r = requests.get(url)

    results = []

    if "Model Y" in r.text:
        results.append("TESLA UFFICIALE:\n" + url)

    return results


# ---------------- SUBITO ----------------

def get_subito():
    url = "https://www.subito.it/annunci-italia/vendita/auto/?q=tesla%20model%20y"

    r = requests.get(url)

    results = []

    matches = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text)

    for link, title in matches:
        if "tesla" in title.lower():
            if is_valid(title, None):
                results.append("SUBITO:\nhttps://www.subito.it" + link)

    return results[:3]


# ---------------- AUTOMOBILE ----------------

def get_automobile():
    url = "https://www.automobile.it/auto-usate/tesla/model-y/"

    r = requests.get(url)

    results = []

    if "Model Y" in r.text:
        results.append("AUTOMOBILE.IT:\n" + url)

    return results


# ---------------- SPOTICAR ----------------

def get_spoticar():
    url = "https://www.spoticar.it/auto-usate/tesla/model-y"

    r = requests.get(url)

    results = []

    if "Model Y" in r.text:
        results.append("SPOTICAR:\n" + url)

    return results


# ---------------- ARIELCAR ----------------

def get_arielcar():
    url = "https://www.arielcar.it/auto-usate"

    r = requests.get(url)

    results = []

    if "tesla" in r.text.lower():
        results.append("ARIELCAR:\n" + url)

    return results


# ---------------- MAIN ----------------

def main():
    results = []

    results += get_tesla()
    results += get_subito()
    results += get_automobile()
    results += get_spoticar()
    results += get_arielcar()

    if not results:
        send("❌ Nessuna Tesla valida trovata")
        return

    msg = "🚗 TESLA TROVATE (FILTRATE):\n\n"

    for r in results:
        msg += r + "\n\n"

    send(msg)


if __name__ == "__main__":
    main()
