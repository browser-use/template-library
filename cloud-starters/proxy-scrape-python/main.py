"""Scrape through residential proxies in several countries, or your own proxy."""

import os

from browser_use_sdk.v4 import BrowserUse, CustomProxy
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

COUNTRIES = os.getenv("PROXY_COUNTRIES", "us,de,jp").split(",")
URL = "https://ipinfo.io/json"  # shows the IP and country the website sees


def custom_proxy() -> CustomProxy | None:
    """Your own proxy if PROXY_HOST is set, otherwise None (managed proxy)."""
    if not os.getenv("PROXY_HOST"):
        return None
    return CustomProxy.model_validate(
        {
            "host": os.environ["PROXY_HOST"],
            "port": int(os.environ["PROXY_PORT"]),
            "username": os.getenv("PROXY_USERNAME") or None,
            "password": os.getenv("PROXY_PASSWORD") or None,
        }
    )


def scrape(client: BrowserUse, settings: dict) -> dict:
    session = client.browsers.create(**settings)
    try:
        if not session.cdp_url:
            raise RuntimeError("The browser did not return a CDP URL")
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.cdp_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            response = page.goto(URL)
            if response is None or not response.ok:
                raise RuntimeError(
                    f"HTTP {response.status if response else 'no response'}"
                )
            return response.json()
    finally:
        client.browsers.stop(session.id)


def main() -> None:
    with BrowserUse() as client:  # reads BROWSER_USE_API_KEY
        proxy = custom_proxy()
        if proxy:
            info = scrape(client, {"custom_proxy": proxy})
            print(f"your proxy: site saw {info.get('ip')} in {info.get('country')}")
            return
        for country in (c.strip() for c in COUNTRIES):
            info = scrape(client, {"proxy_country_code": country})
            print(
                f"asked {country}: site saw {info.get('ip')} in {info.get('country')}"
            )


if __name__ == "__main__":
    main()
