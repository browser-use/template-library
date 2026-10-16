# Browser Use Cloud starters

Small, runnable examples that use [Browser Use Cloud](https://browser-use.com) hosted browsers. Each one needs only `BROWSER_USE_API_KEY` (get one at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new).

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**. Every browser has stealth, residential proxies and a live view.

| Starter | What it shows | Init template |
|---|---|---|
| [`playwright-ts`](playwright-ts) | TypeScript Playwright `connectOverCDP` | (clone the folder) |
| [`puppeteer-ts`](puppeteer-ts) | TypeScript Puppeteer `connect` | (clone the folder) |
| [`playwright-python`](playwright-python) | Python Playwright `connect_over_cdp` | `cloud-playwright` |
| [`agent-python`](agent-python) | browser-use `Agent` with `Browser(use_cloud=True)` | `cloud-agent` |
| [`v4-agent-python`](v4-agent-python) | Hosted agent, API v4 `client.runs.create` | `cloud-v4-agent` |
| [`parallel-python`](parallel-python) | 50 parallel browsers with asyncio | `cloud-parallel` |
| [`login-2fa-python`](login-2fa-python) | Password + TOTP 2FA login saved to a profile | `cloud-login-2fa` |
| [`proxy-scrape-python`](proxy-scrape-python) | Residential proxies by country, or your own proxy | `cloud-proxy-scrape` |

Python starters install with `uvx browser-use init --template <name>`. The TypeScript starters are plain npm projects: copy the folder, `npm install`, `npm start`.

The pattern in every direct-browser starter:

```python
from browser_use_sdk.v4 import BrowserUse

client = BrowserUse()  # reads BROWSER_USE_API_KEY
session = client.browsers.create(proxy_country_code="us")
try:
    ...  # connect Playwright or Puppeteer to session.cdp_url
finally:
    client.browsers.stop(session.id)  # closing CDP alone does not stop the browser
```

Docs: https://docs.browser-use.com/cloud/browser/quickstart
