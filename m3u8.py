from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--mute-audio")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options,
    desired_capabilities=desired_capabilities
)

def get_m3u8_urls(url):
    driver.get(url)
    time.sleep(20)

    logs = driver.get_log("performance")
    urls = []

    for log in logs:
        message = json.loads(log["message"])["message"]
        if message["method"].startswith("Network."):
            req = message.get("params", {}).get("request", {})
            u = req.get("url", "")
            if ".m3u8" in u and "blob:" not in u:
                if u not in urls:
                    urls.append(u)

    driver.quit()
    return urls

if __name__ == "__main__":
    target_url = "https://dilzcreation.pages.dev/?id=ios"
    result = get_m3u8_urls(target_url)

    print(json.dumps(result, indent=2))

    # save output
    with open("m3u8.json", "w") as f:
        json.dump(result, f, indent=2)
