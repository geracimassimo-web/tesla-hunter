import requests

TELEGRAM_TOKEN = "8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc"
CHAT_ID = "2022439793"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def main():
    links = [
        "https://www.autoscout24.it/lst/tesla/model-y?sort=price&desc=0&priceto=31500",
        "https://www.automobile.it/auto-usate/tesla/model-y/?prezzo_max=31500",
        "https://www.subito.it/annunci-italia/vendita/auto/?q=tesla%20model%20y"
    ]

    msg = "🚗 TESLA ALERT\n\nControlla qui le nuove occasioni:\n\n"

    for link in links:
        msg += link + "\n\n"

    send(msg)

if __name__ == "__main__":
    main()
