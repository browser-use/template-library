import logging
import asyncio
import os
import re
from typing import Optional
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from browser_use import Agent, Browser, ChatBrowserUse, sandbox
from browser_use.sandbox.views import BrowserCreatedData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SlackService:
    def __init__(self, access_token: str):
        """Initialize SlackService with Slack access token.

        Note: BROWSER_USE_API_KEY is automatically loaded from environment.
        """
        self.access_token = access_token

    def format_for_slack(self, text: str) -> str:
        """Convert markdown-style text to Slack-friendly format"""
        # Replace escaped newlines with actual newlines
        text = text.replace('\\n', '\n')
        # Convert markdown bold (**text**) to Slack bold (*text*)
        text = text.replace('**', '*')
        return text

    async def send_message(
        self, channel: str, text: str, thread_ts: Optional[str] = None
    ):
        try:
            client = AsyncWebClient(token=self.access_token)
            response = await client.chat_postMessage(
                channel=channel, text=text, thread_ts=thread_ts
            )
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")

    async def update_message(self, channel: str, ts: str, text: str):
        try:
            client = AsyncWebClient(token=self.access_token)
            response = await client.chat_update(channel=channel, ts=ts, text=text)
            return response
        except SlackApiError as e:
            logger.error(f"Error updating message: {e.response['error']}")

    async def handle_event(self, event_data):
        try:
            event_id = event_data.get("event_id")
            logger.info(f"Received event id: {event_id}")
            if not event_id:
                logger.warning("Event ID missing in event data")
                return

            event = event_data.get("event")

            text = event.get("text")
            channel_id = event.get("channel")

            if text and channel_id:
                # Extract the task by taking only the part after the bot mention
                # The text format is: "anything before <@BOT_ID> task description"
                mention_pattern = r"<@[A-Z0-9]+>"
                match = re.search(mention_pattern, text)

                if match:
                    # Take everything after the bot mention
                    task = text[match.end() :].strip()
                else:
                    return

                # Only process if there's actually a task
                if not task:
                    await self.send_message(
                        channel_id,
                        "Specify a task to execute.",
                        thread_ts=event.get("ts"),
                    )
                    return

                # Start the async task to process the agent task
                asyncio.create_task(self.process_agent_task_async(task, channel_id))

        except Exception as e:
            logger.error(f"Error in handle_event: {str(e)}")

    async def process_agent_task_async(self, task: str, channel_id: str):
        """Async function to process the agent task"""
        try:
            # Send initial "starting" message and capture its timestamp
            response = await self.send_message(
                channel_id, "Starting browser task..."
            )
            if not response or not response.get("ok"):
                logger.error(f"Failed to send initial message: {response}")
                return

            message_ts = response.get("ts")
            if not message_ts:
                logger.error("No timestamp received from Slack API")
                return

            # Get profile_id from environment (optional)
            profile_id = os.getenv('BROWSER_USE_PROFILE_ID')

            # Callback to capture browser session info
            def on_browser_created(data: BrowserCreatedData):
                """Called when browser session is created"""
                logger.info(f"✅ Captured Session ID: {data.session_id}")
                logger.info(f"✅ Captured Live URL: {data.live_url}")

                # Send live URL to Slack immediately
                asyncio.create_task(
                    self.send_message(
                        channel_id,
                        f"📺 Live session: {data.live_url}"
                    )
                )

            # Create standalone function for sandbox decorator
            @sandbox(
                log_level='INFO',
                cloud_timeout=30,
                cloud_profile_id=profile_id,
                on_browser_created=on_browser_created
            )
            async def execute_task(browser: Browser, task_description: str):
                """Execute browser task in sandbox"""
                agent = Agent(browser=browser, task=task_description, llm=ChatBrowserUse())
                result = await agent.run()
                return result.final_result()

            # Execute task
            result = await execute_task(task_description=task)

            # Format result for Slack
            formatted_result = self.format_for_slack(result)

            # Send final result
            final_message = f"✅ Task completed!\n\n📝 Task: {task}\n\n🎯 Result:\n{formatted_result}"
            await self.update_message(channel_id, message_ts, final_message)

        except Exception as e:
            error_message = f"Error during task execution: {str(e)}"
            logger.error(f"Error in process_agent_task_async: {error_message}")

            # Send error message as a new message
            try:
                await self.send_message(
                    channel_id, f"❌ Error: {error_message}"
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {str(send_error)}")
