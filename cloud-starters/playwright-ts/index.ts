// Connect Playwright to a Browser Use Cloud browser over CDP.
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";
import { chromium } from "playwright-core";

const client = new BrowserUse(); // reads BROWSER_USE_API_KEY
// timeout (minutes) is a backstop: the browser stops itself even if this process is killed.
const session = await client.browsers.create({ proxyCountryCode: "us", timeout: 10 });
console.log(`Live view: ${session.liveUrl}`);

try {
  if (!session.cdpUrl) throw new Error("The browser did not return a CDP URL");
  const browser = await chromium.connectOverCDP(session.cdpUrl);
  try {
    // Reuse the existing context so profile cookies and managed settings apply.
    const context = browser.contexts()[0];
    const page = context.pages()[0] ?? (await context.newPage());
    await page.goto("https://news.ycombinator.com");
    console.log(await page.title());
  } finally {
    await browser.close(); // closes the CDP connection only
  }
} finally {
  await client.browsers.stop(session.id); // stops the cloud browser and its billing
}
