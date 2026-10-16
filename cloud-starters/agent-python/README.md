# browser-use Agent on Browser Use Cloud

Run the open-source [browser-use](https://github.com/browser-use/browser-use) `Agent` on a hosted browser by passing `Browser(use_cloud=True)`. Same code as local, one argument changed.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-agent
cd cloud-agent
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `Browser(use_cloud=True)` starts a stealth cloud browser instead of local Chrome. For local runs use `Browser(headless=True)`.
- `ChatBrowserUse()` is the LLM. It uses the same `BROWSER_USE_API_KEY`; swap in `ChatOpenAI`, `ChatAnthropic` or `ChatGoogle` if you prefer.
- The agent stops the cloud browser when it finishes.
- Options: `Browser(use_cloud=True, cloud_proxy_country_code="de", cloud_profile_id="...")`.

## Next

Fully hosted agent with no local process: [`../v4-agent-python`](../v4-agent-python). Login with 2FA: [`../login-2fa-python`](../login-2fa-python).
