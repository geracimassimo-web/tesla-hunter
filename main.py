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

        # aspetta caricamento
        page.wait_for_timeout(6000)

        # 🔥 PRENDIAMO TUTTO IL TESTO DELLA PAGINA
        page_text = page.inner_text("body").lower().replace("\n", " ")

        browser.close()

    # 🔍 ANALISI TESTO
    if "model y" not in page_text:
        return "❌ Nessuna Model Y trovata"

    matches = []

    # spezzettiamo per non perdere info
    chunks = page_text.split("€")

    for chunk in chunks:
        if "model y" in chunk and ("long" in chunk and "range" in chunk):
            matches.append(chunk[:200])

    if not matches:
        return "❌ Nessuna Model Y Long Range trovata"

    msg = "🚗 TESLA MODEL Y LONG RANGE:\n\n"

    for m in matches[:5]:
        msg += m + "\n\n"

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
