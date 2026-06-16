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

def get_links():
    links = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.autoscout24.it/lst/tesla/model-y?sort=price&desc=0&priceto=31500")

        # aspetta che gli annunci siano caricati
        page.wait_for_selector("article")

        elements = page.query_selector_all("article a")

        for el in elements:
            href = el.get_attribute("href")
            if href and "/annunci/" in href:
                full_link = "https://www.autoscout24.it" + href
                links.append(full_link)

        browser.close()

    return list(set(links))


def main():
    links = get_links()

    if not links:
        send("❌ Nessuna Tesla trovata")
        return

    msg = "🚗 TESLA TROVATE:\n\n"

    for link in links[:5]:
        msg += link + "\n\n"

    send(msg)


if __name__ == "__main__":
    main()
