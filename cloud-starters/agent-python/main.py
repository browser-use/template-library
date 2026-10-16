"""Run an open-source browser-use Agent on a Browser Use Cloud browser."""

import asyncio

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    # use_cloud=True starts a hosted browser instead of local Chrome.
    # It reads BROWSER_USE_API_KEY and stops the cloud browser when the agent finishes.
    browser = Browser(use_cloud=True)

    agent = Agent(
        task="Open news.ycombinator.com and return the title and URL of the top post",
        llm=ChatBrowserUse(),  # uses the same BROWSER_USE_API_KEY
        browser=browser,
    )
    history = await agent.run()
    if not history.is_successful():
        raise SystemExit(f"Agent did not succeed: {history.final_result()}")
    print(history.final_result())


if __name__ == "__main__":
    asyncio.run(main())
