"""Give a goal to the hosted Browser Use agent (API v4). No local browser needed."""

from browser_use_sdk.v4 import BrowserUse
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    with BrowserUse() as client:  # reads BROWSER_USE_API_KEY
        run = client.runs.create(
            "Open news.ycombinator.com and return the title and URL of the top post",
            max_cost_usd=0.50,  # spend limit, checked between steps (can overshoot slightly)
        )
        print(f"Run {run.id} started (session {run.session_id})")

        # Polls the status endpoint until the run completes, fails or is cancelled.
        try:
            result = client.runs.wait_for_completion(run.id)
        except BaseException:
            client.runs.cancel(run.id)  # stop paid work on Ctrl+C or a polling error
            raise
        print(f"Status: {result.status.value}")
        print(f"Cost: ${result.total_cost_usd}")
        if result.status.value != "completed":
            raise SystemExit(f"Run did not complete: {result.error}")
        print(f"Result: {result.result}")

        # Follow-up turns reuse the same session (and its browser, if still running):
        # client.runs.create("Now open the comments", session_id=run.session_id)


if __name__ == "__main__":
    main()
