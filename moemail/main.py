import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent, Browser, ChatBrowserUse
from email_tools import MoeMailTools

# Point this at a sign-up page you own (your app's staging environment, for example).
SIGNUP_URL = os.getenv("SIGNUP_URL", "http://localhost:3000/signup")

TASK = f"""
Open {SIGNUP_URL} and create a new account. Use get_email_address for the email field and make up
the other details. After submitting, call wait_for_email until the verification email arrives,
then follow its link or enter its code to verify the account. Report whether verification succeeded.
"""


async def main():
    tools = MoeMailTools()
    try:
        agent = Agent(task=TASK, tools=tools, llm=ChatBrowserUse(), browser=Browser())
        await agent.run()
    finally:
        await tools.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
