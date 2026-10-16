// Connect Puppeteer to a Browser Use Cloud browser over CDP.
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";
import puppeteer from "puppeteer-core";

const client = new BrowserUse(); // reads BROWSER_USE_API_KEY
const session = await client.browsers.create({ proxyCountryCode: "us" });
console.log(`Live view: ${session.liveUrl}`);

try {
  if (!session.cdpUrl) throw new Error("The browser did not return a CDP URL");
  const browser = await puppeteer.connect({ browserWSEndpoint: session.cdpUrl });
  try {
    // Reuse the existing context so profile cookies and managed settings apply.
    const context = browser.defaultBrowserContext();
    const page = (await context.pages())[0] ?? (await context.newPage());
    await page.goto("https://news.ycombinator.com");
    console.log(await page.title());
  } finally {
    await browser.disconnect(); // releases the CDP connection only
  }
} finally {
  await client.browsers.stop(session.id); // stops the cloud browser and its billing
}
