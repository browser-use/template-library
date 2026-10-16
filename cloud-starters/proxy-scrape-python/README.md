# Scraping through proxies on Browser Use Cloud

Open the same page through residential proxies in several countries, or through your own proxy, and print what IP and country the site sees.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-proxy-scrape
cd cloud-proxy-scrape
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `client.browsers.create(proxy_country_code="de")` routes the browser through a German residential IP. A US proxy is the default.
- Set `PROXY_HOST` / `PROXY_PORT` (and optional user and password) to use your own proxy via `custom_proxy` instead.
- `proxy_country_code=None` connects directly with no proxy.
- Each browser is stopped in `finally`, so a failed page does not leave it running.

## Next

Managed proxy traffic is billed separately from browser time ($5/GB; $0.20/GB direct or your own proxy).
