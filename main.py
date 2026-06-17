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

        page.wait_for_selector("article", timeout=15000)

        # scroll
        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(3000)

        elements = page.query_selector_all("article")

        for el in elements:
            try:
                full_text = el.inner_text().lower()

                if "model y" not in full_text:
                    continue

                # ---------------- PREZZO ----------------
                price_el = el.query_selector("span[class*='PriceInfo_price']")
                if not price_el:
                    continue

                price_text = price_el.inner_text()

                prezzo_match = re.search(r'([\d\.]+)', price_text)
                if not prezzo_match:
                    continue

                prezzo = int(prezzo_match.group(1).replace(".", ""))

                if prezzo > 31500 or prezzo < 20000:
                    continue

                # ---------------- ANNO ----------------
                anno = None

                date_elements = el.query_selector_all("div[class*='VehicleOverview_itemText']")

                for d in date_elements:
                    txt = d.inner_text()
                    match = re.search(r'(\d{2})/(\d{4})', txt)
                    if match:
                        anno = int(match.group(2))
                        break

                if not anno or anno < 2022:
                    continue

                # ---------------- LINK ----------------
                link_el = el.query_selector("a[href*='/annunci/']")
                if not link_el:
                    continue

                href = link_el.get_attribute("href")
                if not href:
                    continue

                link = "https://www.autoscout24.it" + href

                # ---------------- OUTPUT ----------------
                results.append(f"€{prezzo} | {anno}\n{link}")

            except:
                pass

        browser.close()

    results = list(set(results))

    if not results:
        return "❌ Nessuna Tesla valida trovata"

    msg = "🚗 TESLA MODEL Y (MATCH):\n\n"

    for r in results[:10]:
        msg += r + "\n\n"

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
