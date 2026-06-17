import requests
import os
import re
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = "2022439793"


def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


def extract_details(page, url):
    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        text = page.inner_text("body").lower()

        # PREZZO
        prezzo_match = re.search(r'€\s*([\d\.]+)', text)
        if not prezzo_match:
            return None

        prezzo = int(prezzo_match.group(1).replace(".", ""))

        # ANNO (formato 03/2022)
        anno_match = re.search(r'(\d{2})/(\d{4})', text)
        if not anno_match:
            return None

        anno = int(anno_match.group(2))

        return prezzo, anno

    except:
        return None


def get_autoscout():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")

        page.goto("https://www.autoscout24.it/lst/tesla/model-y", timeout=60000)
        page.wait_for_timeout(5000)

        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(3000)

        links = page.query_selector_all("a[href*='/annunci/']")

        urls = []
        for el in links:
            href = el.get_attribute("href")
            if href and "/annunci/" in href:
                urls.append("https://www.autoscout24.it" + href)

        urls = list(set(urls))[:10]  # max 10 annunci per non rallentare

        for url in urls:
            details = extract_details(page, url)
            if not details:
                continue

            prezzo, anno = details

            if prezzo > 31500 or prezzo < 20000:
                continue

            if anno < 2022:
                continue

            results.append(f"€{prezzo} | {anno}\n{url}")

        browser.close()

    if not results:
        return "❌ Nessuna Tesla valida trovata"

    msg = "🚗 TESLA MODEL Y (MATCH REALI):\n\n"
    for r in results:
        msg += r + "\n\n"

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
