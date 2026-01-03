import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Enable browser logging
options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

driver = webdriver.Chrome(
    service=Service("/usr/bin/chromedriver"),
    options=options
)

JS_HOOK = r"""
(function() {
    window.__m3u8_urls = [];

    function capture(url) {
        if (url && url.includes(".m3u8")) {
            window.__m3u8_urls.push(url);
        }
    }

    // Hook fetch
    const origFetch = window.fetch;
    window.fetch = function() {
        const url = arguments[0];
        if (typeof url === "string") capture(url);
        return origFetch.apply(this, arguments);
    };

    // Hook XHR
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        capture(url);
        return origOpen.apply(this, arguments);
    };

    // Hook MediaSource
    const origAddSourceBuffer = MediaSource.prototype.addSourceBuffer;
    MediaSource.prototype.addSourceBuffer = function(mime) {
        console.log("MediaSource MIME:", mime);
        return origAddSourceBuffer.call(this, mime);
    };

    console.log("M3U8 hook injected");
})();
"""

def get_m3u8(url):
    driver.get(url)
    time.sleep(5)

    # Inject hook BEFORE video loads
    driver.execute_script(JS_HOOK)

    # Let video play / load
    time.sleep(25)

    urls = driver.execute_script("""
        return Array.from(new Set(window.__m3u8_urls || []));
    """)

    return urls


if __name__ == "__main__":
    TARGET = "https://www.fancode.com/football/tour/a-league-2025-26-19245183/matches/brisbane-roar-vs-wellington-phoenix-138816/live-match-info"

    m3u8 = get_m3u8(TARGET)
    driver.quit()

    print(json.dumps(m3u8, indent=2))

    with open("m3u8.json", "w") as f:
        json.dump(m3u8, f, indent=2)
