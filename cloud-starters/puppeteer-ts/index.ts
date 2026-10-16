// Connect Puppeteer to a Browser Use Cloud browser over CDP.
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";
import puppeteer from "puppeteer-core";

const client = new BrowserUse(); // reads BROWSER_USE_API_KEY
// timeout (minutes) is a backstop: the browser stops itself even if this process is killed.
const session = await client.browsers.create({ proxyCountryCode: "us", timeout: 10 });
try {
  console.log(`Live view: ${session.liveUrl}`);
  if (!session.cdpUrl) throw new Error("The browser did not return a CDP URL");
  // cdpUrl is an https:// address; browserURL resolves its websocket via /json/version.
  const browser = await puppeteer.connect({ browserURL: session.cdpUrl });
  try {
    // Reuse the existing context so profile cookies and managed settings apply.
    const context = browser.defaultBrowserContext();
    const page = (await context.pages())[0] ?? (await context.newPage());
    const response = await page.goto("https://news.ycombinator.com");
    if (!response?.ok()) throw new Error(`HTTP ${response?.status() ?? "none"}`);
    console.log(await page.title());
  } finally {
    await browser.disconnect(); // releases the CDP connection only
  }
} finally {
  await client.browsers.stop(session.id); // stops the cloud browser and its billing
}
