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


def get_autoscout():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")

        page.goto("https://www.autoscout24.it/lst/tesla/model-y", timeout=60000)

        page.wait_for_timeout(5000)

        # scroll forte
        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(3000)

        links = page.query_selector_all("a[href*='/annunci/']")

        for link_el in links:
            try:
                href = link_el.get_attribute("href")
                text = link_el.inner_text()

                if not href or not text:
                    continue

                t = text.lower().replace("\n", " ")

                if "model y" not in t:
                    continue

                # -------- PREZZO --------
                prezzo_match = re.search(r'€\s*([\d\.]+)', text)
                if not prezzo_match:
                    continue

                prezzo = int(prezzo_match.group(1).replace(".", ""))

                if prezzo > 31500 or prezzo < 20000:
                    continue

                # -------- ANNO --------
                anno = None
                for y in ["2026","2025","2024","2023","2022","2021"]:
                    if y in text:
                        anno = int(y)
                        break

                if not anno or anno < 2022:
                    continue

                link = "https://www.autoscout24.it" + href

                results.append(f"€{prezzo} | {anno}\n{text[:100]}\n{link}")

            except:
                pass

        browser.close()

    results = list(set(results))

    if not results:
        return "❌ Nessuna Tesla valida trovata (ma ora è realistico)"

    msg = "🚗 TESLA MODEL Y (MATCH):\n\n"

    for r in results[:10]:
        msg += r + "\n\n"

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
