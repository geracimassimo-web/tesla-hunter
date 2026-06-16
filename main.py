import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = "8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc"
CHAT_ID = "022439793"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def main():
    link = "https://www.automobile.it/auto-usate/tesla/model-y/?prezzo_max=31500"

    msg = f"🚗 Controlla qui le Tesla disponibili:\n\n{link}"

    send(msg)

if __name__ == "__main__":
    main()
