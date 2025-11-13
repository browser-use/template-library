"""
Browser-use agent with cloud sandbox configuration.

This script demonstrates browser automation using browser-use with cloud
features including:
- Persistent authentication via cloud profile
- Proxy routing through specified country (US)
- Configurable session timeout

The agent is configured to navigate to X.com and retrieve the most recent
post from the authenticated user's timeline.

Configuration is loaded from environment variables via .env file:
- BROWSER_USE_API_KEY: API key for browser-use cloud service
- CLOUD_PROFILE_ID: Saved cookies/authentication profile ID
  (Get yours from: https://cloud.browser-use.com/#settings/profiles)
- CLOUD_PROXY_COUNTRY_CODE: Country code for proxy routing
- CLOUD_TIMEOUT: Maximum browser session time in minutes
"""

from browser_use import Agent, Browser, ChatBrowserUse, sandbox
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

@sandbox(
    cloud_profile_id=os.getenv('CLOUD_PROFILE_ID'),
    cloud_proxy_country_code=os.getenv('CLOUD_PROXY_COUNTRY_CODE'),
    cloud_timeout=int(os.getenv('CLOUD_TIMEOUT', 60)),
)
async def main(browser: Browser):
    llm = ChatBrowserUse()

    task = "Go to x.com and get the most recent post on my timeline"

    agent = Agent(
        browser=browser,
        task=task,
        llm=llm,
    )

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
