import requests
import os
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = "2022439793"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def get_autoscout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.autoscout24.it/lst/tesla/model-y")

        page.wait_for_timeout(5000)

        elements = page.query_selector_all("a")

        msg = "DEBUG AUTOSCOUT:\n\n"

        for el in elements[:20]:
            try:
                text = el.inner_text()
                msg += text + "\n\n"
            except:
                pass

        send(msg)

        browser.close()

    return []
   

def main():
    results = get_autoscout()

    if not results:
        send("❌ Nessuna Model Y Long Range trovata")
        return

    msg = "🚗 MODEL Y LONG RANGE:\n\n"

    for r in results:
        msg += r + "\n\n"

    send(msg)


if __name__ == "__main__":
    main()
