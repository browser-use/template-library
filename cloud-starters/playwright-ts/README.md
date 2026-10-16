# Playwright (TypeScript) on Browser Use Cloud

Create a hosted browser with `browser-use-sdk`, connect Playwright to it with `chromium.connectOverCDP(session.cdpUrl)`, and stop it when done.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
git clone --depth 1 https://github.com/browser-use/template-library
cd template-library/cloud-starters/playwright-ts
cp .env.example .env   # add BROWSER_USE_API_KEY
npm install
npm start
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `client.browsers.create({ proxyCountryCode: "us" })` starts a stealth Chromium behind a US residential proxy and returns `cdpUrl` and `liveUrl` (watch it live in your browser).
- `playwright-core` is enough: the browser runs in the cloud, so nothing is downloaded locally.
- Use `browser.contexts()[0]`, not `newContext()`, so profile cookies and managed settings apply.
- `browser.close()` only drops the CDP connection. `client.browsers.stop(session.id)` stops the cloud browser and its billing.
- Type-check with `npm run typecheck`.

## Next

Same flow with Puppeteer: [`../puppeteer-ts`](../puppeteer-ts). Python: [`../playwright-python`](../playwright-python).
