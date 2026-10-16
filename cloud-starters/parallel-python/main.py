"""Run 50 jobs on Browser Use Cloud browsers in parallel with asyncio."""

import asyncio
import os

from browser_use_sdk.v4 import AsyncBrowserUse
from dotenv import load_dotenv
from playwright.async_api import Playwright, async_playwright

load_dotenv()

JOBS = 50
# New projects can run 10 browsers at once; the limit rises with spend (50 at $100).
CONCURRENCY = int(os.getenv("CONCURRENCY", "10"))
URL = "https://en.wikipedia.org/wiki/Special:Random"


async def run_job(
    client: AsyncBrowserUse, pw: Playwright, slots: asyncio.Semaphore, job: int
) -> str:
    async with slots:
        # Wikipedia needs no residential proxy; turning it off lowers traffic cost.
        # timeout (minutes) is a backstop: the browser stops itself even if stop() fails.
        session = await client.browsers.create(
            proxy_country_code=None, timeout=5, metadata={"job": str(job)}
        )
        try:
            if not session.cdp_url:
                raise RuntimeError("The browser did not return a CDP URL")
            browser = await pw.chromium.connect_over_cdp(session.cdp_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            response = await page.goto(URL)
            if response is None or not response.ok:
                raise RuntimeError(
                    f"HTTP {response.status if response else 'no response'}"
                )
            return await page.title()
        finally:
            await client.browsers.stop(session.id)


async def main() -> None:
    slots = asyncio.Semaphore(CONCURRENCY)
    async with AsyncBrowserUse() as client, async_playwright() as pw:
        results = await asyncio.gather(
            *(run_job(client, pw, slots, i) for i in range(JOBS)),
            return_exceptions=True,
        )

    failed = 0
    for i, result in enumerate(results):
        if isinstance(result, BaseException):
            failed += 1
            print(f"job {i:2}: FAILED {result!r}")
        else:
            print(f"job {i:2}: {result}")
    print(f"\n{JOBS - failed}/{JOBS} jobs succeeded")


if __name__ == "__main__":
    asyncio.run(main())
