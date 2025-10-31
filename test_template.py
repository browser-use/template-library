"""
Test Template

This is a test template to demonstrate dynamic template discovery.
When you see this in the list, dynamic discovery is working!
"""

import asyncio

from dotenv import load_dotenv

from browser_use import Agent, Browser, ChatBrowserUse

load_dotenv()


async def main():
	browser = Browser(use_cloud=False)
	llm = ChatBrowserUse()
	task = 'This is a test template - dynamic discovery works!'
	agent = Agent(
		browser=browser,
		task=task,
		llm=llm,
	)
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
