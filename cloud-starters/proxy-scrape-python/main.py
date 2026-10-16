"""Scrape through residential proxies in several countries, or your own proxy."""

import json
import os

from browser_use_sdk.v4 import BrowserUse, CustomProxy
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

COUNTRIES = os.getenv("PROXY_COUNTRIES", "us,de,jp").split(",")
URL = "https://ipinfo.io/json"  # shows the IP and country the website sees


def proxy_settings(country: str) -> dict:
    """Managed residential proxy by default, or your own proxy if PROXY_HOST is set."""
    if os.getenv("PROXY_HOST"):
        return {
            "custom_proxy": CustomProxy.model_validate(
                {
                    "host": os.environ["PROXY_HOST"],
                    "port": int(os.environ["PROXY_PORT"]),
                    "username": os.getenv("PROXY_USERNAME") or None,
                    "password": os.getenv("PROXY_PASSWORD") or None,
                }
            )
        }
    return {"proxy_country_code": country}


def scrape(client: BrowserUse, country: str) -> dict:
    session = client.browsers.create(**proxy_settings(country))
    try:
        if not session.cdp_url:
            raise RuntimeError("The browser did not return a CDP URL")
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.cdp_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL)
            return json.loads(page.inner_text("body"))
    finally:
        client.browsers.stop(session.id)


def main() -> None:
    with BrowserUse() as client:  # reads BROWSER_USE_API_KEY
        for country in COUNTRIES:
            info = scrape(client, country.strip())
            print(
                f"asked {country}: site saw {info.get('ip')} in {info.get('country')}"
            )


if __name__ == "__main__":
    main()
