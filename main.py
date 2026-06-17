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
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent="Mozilla/5.0"
        )

        page.goto("https://www.autoscout24.it/lst/tesla/model-y", timeout=60000)

        page.wait_for_timeout(5000)

        # scroll per caricare più annunci
        page.mouse.wheel(0, 8000)
        page.wait_for_timeout(3000)

        # 🔥 PRENDIAMO DIRETTAMENTE I LINK ANNUNCI
        links = page.query_selector_all("a[href*='/annunci/']")

        for link_el in links:
            try:
                href = link_el.get_attribute("href")
                text = link_el.inner_text()

                if not href or not text:
                    continue

                t = text.lower().replace("\n", " ")

                # 🔥 filtro più realistico
                if "model y" in t:

                    # NON filtriamo troppo → vediamo tutto
                    full_link = "https://www.autoscout24.it" + href

                    results.append(f"{text[:100]}\n{full_link}")

            except:
                pass

        browser.close()

    # rimuovi duplicati
    results = list(set(results))

    if not results:
        return "❌ Nessuna Model Y trovata (strano!)"

    msg = "🚗 TESLA MODEL Y (GREZZO):\n\n"

    for r in results[:10]:
        msg += r + "\n\n"

    return msg


def main():
    msg = get_autoscout()
    send(msg)


if __name__ == "__main__":
    main()
