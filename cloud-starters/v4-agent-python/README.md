# Hosted Browser Use agent (API v4)

Send a task to the hosted Browser Use agent with `client.runs.create(...)` and wait for the result. The agent and its browser both run in Browser Use Cloud.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-v4-agent
cd cloud-v4-agent
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `client.runs.create(task, max_cost_usd=0.50)` starts a run in a new session with a spend limit (checked between steps, so it can overshoot slightly).
- `client.runs.wait_for_completion(run.id)` polls the status endpoint and returns the result, status and `total_cost_usd`. Ctrl+C or a polling error cancels the run.
- Follow-up turns: `client.runs.create("...", session_id=run.session_id)`.
- Options: `browser_settings={"proxyCountryCode": "de", "profileId": "..."}`, `model=...`, `secret_bindings=[...]`.

## Next

Runs also bill model tokens. Docs: https://docs.browser-use.com/cloud/agent/quickstart
