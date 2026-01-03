import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# -----------------------------
# Chrome options (Selenium 4)
# -----------------------------
options = webdriver.ChromeOptions()

# Headless + CI safe flags
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

# ✅ SET performance logging capability (Selenium 4 way)
options.set_capability(
    "goog:loggingPrefs",
    {"performance": "ALL"}
)


# -----------------------------
# Create Chrome driver
# -----------------------------
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


def get_m3u8_urls(page_url: str):
    print(f"[+] Opening: {page_url}")
    driver.get(page_url)

    # wait for video/network activity
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
    TARGET_URL = "https://dilzcreation.pages.dev/?id=ios"

    m3u8_links = get_m3u8_urls(TARGET_URL)

    driver.quit()

    print("\n[+] Found M3U8 URLs:")
    print(json.dumps(m3u8_links, indent=2))

    # Save to JSON
    with open("m3u8.json", "w") as f:
        json.dump(m3u8_links, f, indent=2)

    print("\n[✓] Saved to m3u8.json")
