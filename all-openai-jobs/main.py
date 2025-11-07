import asyncio

from browser_use import CodeAgent, ChatBrowserUse
from browser_use.code_use import export_to_ipynb

company_ashby_slug = "openai"
url = f"https://jobs.ashbyhq.com/{company_ashby_slug}"

task = f"""
Please go to {url} and extract all the jobs from the page. Make sure to extract the data, and don't return empty array unless there are no openings.
"""

initial_actions = [{"navigate": {"url": url, "new_tab": False}}]

agent = CodeAgent(
    task=task,
    llm=ChatBrowserUse(),  # requires our special LLM
    initial_actions=initial_actions,
)


async def main():
    session = await agent.run()

    # script
    script = export_to_ipynb(agent, "script.ipynb")


if __name__ == "__main__":
    asyncio.run(main())
