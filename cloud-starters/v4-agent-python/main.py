"""Give a goal to the hosted Browser Use agent (API v4). No local browser needed."""

from browser_use_sdk.v4 import BrowserUse
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    with BrowserUse() as client:  # reads BROWSER_USE_API_KEY
        run = client.runs.create(
            "Open news.ycombinator.com and return the title and URL of the top post",
            max_cost_usd=0.50,  # hard stop for this run
        )
        print(f"Run {run.id} started (session {run.session_id})")

        # Polls the status endpoint until the run completes, fails or is cancelled.
        result = client.runs.wait_for_completion(run.id)
        print(f"Status: {result.status.value}")
        print(f"Result: {result.result}")
        print(f"Cost: ${result.total_cost_usd}")

        # Follow-up turns reuse the same session (and its browser, if still running):
        # client.runs.create("Now open the comments", session_id=run.session_id)


if __name__ == "__main__":
    main()
