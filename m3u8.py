import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# -----------------------------
# Chrome options (Selenium 4)
# -----------------------------
options = webdriver.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--mute-audio")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")

options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
)

# performance logging
options.set_capability(
    "goog:loggingPrefs",
    {"performance": "ALL"}
)


# -----------------------------
# Use SYSTEM chromedriver
# -----------------------------
service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(
    service=service,
    options=options
)


def get_m3u8_urls(page_url: str):
    print(f"[+] Opening: {page_url}")
    driver.get(page_url)

    time.sleep(25)

    logs = driver.get_log("performance")
    found = []

    for log in logs:
        try:
            msg = json.loads(log["message"])["message"]

            if not msg["method"].startswith("Network."):
                continue

            params = msg.get("params", {})
            request = params.get("request", {})
            url = request.get("url", "")

            if ".m3u8" in url and "blob:" not in url:
                if url not in found:
                    found.append(url)

        except Exception:
            pass

    return found


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    TARGET_URL = "https://www.fancode.com/football/tour/a-league-2025-26-19245183/matches/brisbane-roar-vs-wellington-phoenix-138816/live-match-info"

    m3u8_links = get_m3u8_urls(TARGET_URL)

    driver.quit()

    print(json.dumps(m3u8_links, indent=2))

    with open("m3u8.json", "w") as f:
        json.dump(m3u8_links, f, indent=2)

    print("[✓] Saved m3u8.json")
