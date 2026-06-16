import requests
import re

TELEGRAM_TOKEN = "8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc"
CHAT_ID = "022439793"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def get_autoscout():
    url = "https://www.autoscout24.it/lst/tesla/model-y?sort=price&desc=0&ustate=N%2CU&atype=C&cy=I&pricefrom=20000&priceto=31500"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    return r.text


def extract_links(html):
    links = re.findall(r'https://www.autoscout24.it/annunci/[^"]+', html)
    return list(set(links))


def main():
    html = get_autoscout()
    links = extract_links(html)

    if not links:
        send("❌ Nessuna Tesla trovata")
        return

    msg = "🚗 TESLA TROVATE:\n\n"

    for link in links[:5]:  # primi 5 annunci
        msg += link + "\n\n"

    send(msg)


if __name__ == "__main__":
    main()
