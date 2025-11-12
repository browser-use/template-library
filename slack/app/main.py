import os
import json
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from slack_sdk.signature import SignatureVerifier
from service import SlackService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()


@app.post("/slack/events")
async def slack_events(request: Request):
    try:
        signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        access_token = os.getenv("SLACK_ACCESS_TOKEN")
        if not signing_secret or not access_token:
            raise HTTPException(
                status_code=500, detail="Required environment variables not configured"
            )

        # Read body once and use it for both verification and parsing
        body = await request.body()

        if not SignatureVerifier(signing_secret).is_valid_request(
            body, dict(request.headers)
        ):
            logger.warning("Request verification failed")
            raise HTTPException(status_code=400, detail="Request verification failed")

        event_data = json.loads(body)
        if "challenge" in event_data:
            return {"challenge": event_data["challenge"]}

        slack_bot = SlackService(access_token)
        if "event" in event_data:
            try:
                await slack_bot.handle_event(event_data)
            except Exception as e:
                logger.error(f"Error handling event: {str(e)}")

        return {}
    except HTTPException:
        raise
    except Exception as e:
        import traceback

        logger.error(f"Error in slack_events: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to process Slack event")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
