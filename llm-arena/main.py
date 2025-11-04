"""
LLM comparison tool - runs the same task across multiple LLMs in parallel
"""

from browser_use import Agent, Browser, ChatBrowserUse, ChatGoogle, ChatAnthropic, ChatOpenAI, sandbox
from browser_use.llm.base import BaseChatModel
from dotenv import load_dotenv
import asyncio
import time
import os

load_dotenv()

@sandbox()
async def execute_task(browser: Browser, task: str, llm: BaseChatModel, llm_name: str):
    """Execute a task with a fresh browser session."""
    start_time = time.time()

    agent = Agent(
        browser=browser,
        task=task,
        llm=llm,
    )

    print(f"\n🤖 {llm_name} - Starting task...")
    result = await agent.run()
    elapsed = time.time() - start_time

    print(f"\n✅ {llm_name} - Completed in {elapsed:.2f}s")
    print(f"📊 {llm_name} - Result: {result}")

    return {
        'llm': llm_name,
        'result': result,
        'time': elapsed
    }


async def main():
    """Run the same task across multiple LLMs in parallel."""

    print("🚀 LLM Comparison Tool")
    print("=" * 50)
    print("Enter a task to run across multiple LLMs in parallel.")
    print("Examples:")
    print("  - 'Find the number of stars of the browser-use repo on GitHub'")
    print("  - 'Go to amazon.com and find the price of the cheapest laptop'")
    print("  - 'Visit reddit.com and find the top post about AI'\n")

    try:
        # Get task description
        task_description = input("\n📋 Enter task: ").strip()

        if not task_description:
            print("⚠️  Task cannot be empty")
            return

        # Define LLMs to compare
        llms = [
            ("Browser Use (bu-0-1)", ChatBrowserUse()),
            ("Google Gemini (gemini-flash-latest)", ChatGoogle(model="gemini-flash-latest", api_key=os.getenv("GOOGLE_API_KEY"))),
            ("OpenAI ChatGPT (gpt-4.1-mini)", ChatOpenAI(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))),
            ("Anthropic Claude (claude-sonnet-4-0)", ChatAnthropic(model="claude-sonnet-4-0", api_key=os.getenv("ANTHROPIC_API_KEY"))),
        ]

        print(f"\n🏁 Starting race with {len(llms)} LLMs...")
        print("=" * 50)

        # Create tasks for all LLMs
        tasks = [
            asyncio.create_task(
                execute_task(task=task_description, llm=llm, llm_name=name)
            )
            for name, llm in llms
        ]

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Show summary
        print("\n" + "=" * 50)
        print("🏆 RESULTS SUMMARY")
        print("=" * 50)

        valid_results = [r for r in results if isinstance(r, dict)]
        if valid_results:
            sorted_results = sorted(valid_results, key=lambda x: x['time'])
            for i, result in enumerate(sorted_results, 1):
                print(f"{i}. {result['llm']} - {result['time']:.2f}s")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted!")
        print("🛑 Shutdown complete")


if __name__ == '__main__':
    asyncio.run(main())
