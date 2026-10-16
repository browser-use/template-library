# 50 parallel cloud browsers (Python, asyncio)

Run 50 jobs on Browser Use Cloud browsers with `AsyncBrowserUse` and Playwright, a bounded `asyncio.Semaphore`, and per-job error handling.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-parallel
cd cloud-parallel
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- Each job creates its own browser, connects over CDP, reads one random Wikipedia page (an HTTP error counts as a failure), and stops the browser in `finally`. `timeout=5` (minutes) makes the browser stop itself if the stop call fails.
- `CONCURRENCY` (default 10) caps browsers running at once. New projects get 10 concurrent browsers; the limit rises with spend (50 at $100, 250 at $1,000). Check yours with `GET /api/v2/billing/account` (`concurrentSessionLimit`).
- `proxy_country_code=None` turns off the residential proxy for sites that do not need it, which lowers traffic cost.
- `metadata={"job": ...}` labels each browser so you can find it in the dashboard.
- A failed job does not stop the others (`return_exceptions=True`).

## Next

Limits and retries: https://docs.browser-use.com/cloud/guides/concurrency
