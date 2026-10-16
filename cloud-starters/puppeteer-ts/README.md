# Puppeteer (TypeScript) on Browser Use Cloud

Create a hosted browser with `browser-use-sdk`, connect Puppeteer to it with `puppeteer.connect({ browserURL: session.cdpUrl })`, and stop it when done.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
git clone --depth 1 https://github.com/browser-use/template-library
cd template-library/cloud-starters/puppeteer-ts
cp .env.example .env   # add BROWSER_USE_API_KEY
npm install
npm start
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- `client.browsers.create({ proxyCountryCode: "us", timeout: 10 })` starts a stealth Chromium behind a US residential proxy (`timeout: 10` minutes is a backstop if the process is killed before `stop`) and returns `cdpUrl` and `liveUrl`.
- `cdpUrl` is an `https://` address, so pass it as `browserURL`: Puppeteer reads the websocket URL from `/json/version`, the same way Playwright's `connectOverCDP` does.
- `puppeteer-core` is enough: the browser runs in the cloud, so no Chrome download.
- Use `browser.defaultBrowserContext()` so profile cookies and managed settings apply.
- `browser.disconnect()` releases the connection. `client.browsers.stop(session.id)` stops the cloud browser and its billing.
- Type-check with `npm run typecheck`.

## Next

Same flow with Playwright: [`../playwright-ts`](../playwright-ts).
