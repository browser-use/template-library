"""Connect Playwright (Python) to a Browser Use Cloud browser over CDP."""

from browser_use_sdk.v4 import BrowserUse
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


def main() -> None:
    with BrowserUse() as client:  # reads BROWSER_USE_API_KEY
        session = client.browsers.create(proxy_country_code="us")
        try:
            print(f"Live view: {session.live_url}")
            if not session.cdp_url:
                raise RuntimeError("The browser did not return a CDP URL")
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(session.cdp_url)
                # Reuse the existing context so profile cookies and settings apply.
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                response = page.goto("https://news.ycombinator.com")
                if response is None or not response.ok:
                    raise RuntimeError(
                        f"HTTP {response.status if response else 'none'}"
                    )
                print(page.title())
        finally:
            # Closing Playwright only drops the CDP connection.
            # This stops the cloud browser and its billing.
            client.browsers.stop(session.id)


if __name__ == "__main__":
    main()
