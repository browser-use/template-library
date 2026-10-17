# Playwright (Python) on Browser Use Cloud

Create a hosted browser with `browser-use-sdk`, connect Playwright to it with `connect_over_cdp(session.cdp_url)`, and stop it when done.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-playwright
cd cloud-playwright
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `client.browsers.create(proxy_country_code="us")` starts a stealth Chromium behind a US residential proxy and returns `cdp_url` and `live_url`.
- No `playwright install` needed: the browser runs in the cloud.
- Use `browser.contexts[0]`, not `new_context()`, so profile cookies and managed settings apply.
- Closing Playwright only drops the CDP connection. `client.browsers.stop(session.id)` stops the cloud browser and its billing.

## Next

Many browsers at once: [`../parallel-python`](../parallel-python). Proxies by country: [`../proxy-scrape-python`](../proxy-scrape-python).
