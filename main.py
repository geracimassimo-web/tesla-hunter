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

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )

        page.goto("https://www.autoscout24.it/lst/tesla/model-y", timeout=60000)

        # aspetta che compaiano gli annunci veri
        page.wait_for_selector("article", timeout=15000)

        elements = page.query_selector_all("article")

        msg = "DEBUG ANNUNCI:\n\n"

        for el in elements[:10]:
            try:
                text = el.inner_text()
                msg += text[:200] + "\n\n"
            except:
                pass

        browser.close()

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
