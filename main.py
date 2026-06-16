import requests

TELEGRAM_TOKEN = 8573311691:AAE5g32_JSYEHk-eiGiTs1OoupQfeUK0-Uc
CHAT_ID = 2022439793

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def main():
    send("🚀 Tesla Hunter attivo!")

if __name__ == "__main__":
    main()
