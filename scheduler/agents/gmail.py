"""
Browser-use agent with cloud sandbox configuration for Gmail.

This script demonstrates browser automation using browser-use with cloud
features including:
- Persistent authentication via cloud profile
- Proxy routing through specified country (US)
- Configurable session timeout

The agent is configured to navigate to Gmail and retrieve recent emails.

Configuration is loaded from environment variables via .env file:
- BROWSER_USE_API_KEY: API key for browser-use cloud service
- CLOUD_PROFILE_ID: Saved cookies/authentication profile ID
  (Get yours from: https://cloud.browser-use.com/#settings/profiles)
- CLOUD_PROXY_COUNTRY_CODE: Country code for proxy routing
- CLOUD_TIMEOUT: Maximum browser session time in minutes
"""

from browser_use import Agent, Browser, ChatBrowserUse, sandbox
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

@sandbox(
	cloud_profile_id=os.getenv("CLOUD_PROFILE_ID"),
	cloud_proxy_country_code=os.getenv("CLOUD_PROXY_COUNTRY_CODE"),
	cloud_timeout=int(os.getenv("CLOUD_TIMEOUT", 60)),
)
async def main(browser: Browser):
	llm = ChatBrowserUse()

	task = (
		"Go to https://mail.google.com/mail/u/0/#inbox and extract "
		"the top 5 most recent emails from my inbox including sender name, "
		"subject, preview text, and timestamp. "
		"Provide a brief summary of what these emails are about."
	)

	agent = Agent(
		browser=browser,
		task=task,
		llm=llm,
	)

	history = await agent.run()

	# Extract final result BEFORE returning (while still in sandbox)
	return {"result": history.final_result() or "No result from agent"}

async def run():
	"""Wrapper function that calls main and writes results to file."""
	output_file = Path("/tmp") / "gmail.py_result.json"

	try:
		# Call the sandbox-decorated function (returns dict from sandbox)
		result = await main()

		result_data = {
			"script": "gmail.py",
			"success": bool(result and result.get("result")),
			"result": result.get("result") if result else "No result returned from agent"
		}

		with open(output_file, 'w') as f:
			json.dump(result_data, f, indent=2)

	except Exception as e:
		# Write error result
		import traceback
		error_data = {
			"script": "gmail.py",
			"success": False,
			"result": f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
		}
		with open(output_file, 'w') as f:
			json.dump(error_data, f, indent=2)

if __name__ == "__main__":
	import asyncio
	asyncio.run(run())
