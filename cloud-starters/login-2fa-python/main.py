"""Cloud browser login with password + TOTP 2FA, saved to a profile for reuse."""

import asyncio
import os

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.environ["LOGIN_DOMAIN"]  # e.g. github.com
LOGIN_URL = os.environ["LOGIN_URL"]  # e.g. https://github.com/login


async def main() -> None:
    browser = Browser(
        use_cloud=True,
        # A cloud profile saves cookies when the browser stops,
        # so the next run starts logged in.
        cloud_profile_id=os.getenv("CLOUD_PROFILE_ID") or None,
        # Only let the agent navigate this site (and its subdomains).
        allowed_domains=[f"*.{DOMAIN}"],
    )

    # The task uses placeholder names; real values are filled in only when typed.
    # A placeholder ending in bu_2fa_code holds a TOTP secret:
    # the agent types the current 6-digit code.
    sensitive_data: dict[str, str | dict[str, str]] = {
        f"*.{DOMAIN}": {
            "site_username": os.environ["SITE_USERNAME"],
            "site_password": os.environ["SITE_PASSWORD"],
            "site_bu_2fa_code": os.environ["SITE_TOTP_SECRET"],
        }
    }

    agent = Agent(
        task=(
            f"Go to {LOGIN_URL}. If you are already logged in, skip to the last step. "
            "Otherwise log in with site_username and site_password. "
            "If the site asks for an authentication code, enter site_bu_2fa_code. "
            "Last step: return the name of the logged-in account."
        ),
        llm=ChatBrowserUse(),
        browser=browser,
        sensitive_data=sensitive_data,
        use_vision=False,  # keep typed secrets out of screenshots sent to the LLM
    )
    history = await agent.run()
    if not history.is_successful():
        raise SystemExit(f"Agent did not succeed: {history.final_result()}")
    print(history.final_result())


if __name__ == "__main__":
    asyncio.run(main())
