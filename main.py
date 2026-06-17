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

        # scroll per caricare più annunci
        page.mouse.wheel(0, 10000)
        page.wait_for_timeout(3000)

        elements = page.query_selector_all("article")

        for el in elements:
            try:
                # ---------------- TITOLO ----------------
                title_el = el.query_selector("h2")
                if not title_el:
                    continue

                title = title_el.inner_text()
                t = title.lower()

                if "model y" not in t:
                    continue

                # ---------------- PREZZO ----------------
                price_el = el.query_selector("[data-testid='price']")
                if not price_el:
                    continue

                price_text = price_el.inner_text()

                prezzo_match = re.search(r'([\d\.]+)', price_text)
                if not prezzo_match:
                    continue

                prezzo = int(prezzo_match.group(1).replace(".", ""))

                # filtro prezzo
                if prezzo > 31500 or prezzo < 20000:
                    continue

                # ---------------- ANNO ----------------
                full_text = el.inner_text()

                anno = None
                for y in ["2026", "2025", "2024", "2023", "2022", "2021"]:
                    if y in full_text:
                        anno = int(y)
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
                results.append(f"€{prezzo} | {anno}\n{title}\n{link}")

            except:
                pass

        browser.close()

    # rimuove duplicati
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
