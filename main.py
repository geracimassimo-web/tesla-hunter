import requests

TELEGRAM_TOKEN = "8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc"
CHAT_ID = "2022439793"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def get_tesla():
    url = "https://www.tesla.com/it_IT/inventory/used/my?arrangeby=plh&zip=20100&range=0"

    r = requests.get(url)

    cars = []

    if "Model Y" in r.text:
        cars.append("🚗 Tesla usate disponibili (controlla subito):\n" + url)

    return cars


def main():
    results = []

    results += get_tesla()

    if not results:
        send("❌ Nessuna Tesla interessante trovata")
        return

    msg = "🚗 TESLA TROVATE:\n\n"

    for r in results:
        msg += r + "\n\n"

    send(msg)


if __name__ == "__main__":
    main()
