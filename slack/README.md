# Browser-use Slack Bot

> **Official browser-use template** - Part of the [browser-use template library](https://github.com/browser-use/browser-use)

A Slack bot that performs browser automation tasks using the [browser-use](https://github.com/browser-use/browser-use) cloud sandbox. Mention the bot in any channel with a task, and it will execute browser actions and return results directly in Slack.

## Features

- Execute browser automation tasks via Slack mentions
- Real-time browser session URLs for live viewing
- Cloud-based execution using browser-use sandbox
- Optional authenticated browser profiles for persistent sessions
- Automatic result formatting for Slack

## Prerequisites

- **Python 3.11 or higher** (required by browser-use)
- **uv** package manager - [Install uv](https://github.com/astral-sh/uv)
- **ngrok** - For local development HTTPS tunnel - [Install ngrok](https://ngrok.com/)
- **Slack workspace** with admin permissions
- **Browser-use API key** - [Get your API key here](https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new)

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `BROWSER_USE_API_KEY` | Your browser-use cloud API key | Yes | `bu-xxxxx...` |
| `SLACK_ACCESS_TOKEN` | Slack Bot User OAuth Token (starts with `xoxb-`) | Yes | `xoxb-123...` |
| `SLACK_SIGNING_SECRET` | Slack app signing secret for request verification | Yes | `abc123...` |
| `BROWSER_USE_PROFILE_ID` | Optional browser profile ID for authenticated sessions | No | `7ba0f2cf-...` |

See `.env.example` for a template.

## Installation

### 1. Clone and Install Dependencies

```bash
cd /path/to/slack
uv sync
```

This will create a virtual environment and install all required dependencies.

### 2. Create Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name your app (e.g., "Browser-use Bot")
4. Select your workspace

### 3. Configure OAuth Scopes

Navigate to **"OAuth & Permissions"** and add these Bot Token Scopes:

- `app_mentions:read` - View messages that directly mention the bot
- `channels:read` - View basic information about public channels
- `chat:write` - Send messages as the bot

### 4. Install App to Workspace

1. Click **"Install to Workspace"**
2. Authorize the requested permissions
3. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)
4. Add it to your `.env` file as `SLACK_ACCESS_TOKEN`

### 5. Get Signing Secret

1. Navigate to **"Basic Information"**
2. Under **"App Credentials"**, find **"Signing Secret"**
3. Click **"Show"** and copy the value
4. Add it to your `.env` file as `SLACK_SIGNING_SECRET`

### 6. Setup ngrok (for local development)

Start ngrok to create an HTTPS tunnel to your local server:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

> Note: The free ngrok URL changes each time you restart ngrok. You'll need to update your Slack app's Request URL whenever this happens.

### 7. Configure Event Subscriptions

1. In your Slack app settings, go to **"Event Subscriptions"**
2. Toggle **"Enable Events"** to **On**
3. Set **Request URL**: `https://your-ngrok-url.ngrok-free.app/slack/events`
4. Wait for the green checkmark (verification successful)
5. Under **"Subscribe to bot events"**, add:
   - `app_mention` - When someone mentions the bot
6. Click **"Save Changes"**

> Important: Slack will send a challenge request to verify your endpoint. Make sure your server is running before setting the Request URL.

### 8. Run the Application

```bash
uv run app/main.py
```

The server will start on `http://0.0.0.0:8000`

## Usage

### Invite the Bot

First, invite the bot to a channel:

```
/invite @YourBotName
```

### Execute a Task

Mention the bot with a task description:

```
@YourBotName search for Python tutorials on YouTube
```

```
@YourBotName go to amazon.com and find the best-selling laptop
```

### What Happens

1. Bot responds: "Starting browser task..."
2. Bot sends a live browser session URL (you can watch in real-time)
3. Bot executes the task using browser-use agent
4. Bot updates the message with the final result

## Architecture

### How It Works

```
Slack Event → FastAPI Webhook → Signature Verification
                                        ↓
                                 Extract Task
                                        ↓
                              Create Async Task
                                        ↓
                     Browser-use Cloud Sandbox (@sandbox)
                                        ↓
                         on_browser_created callback
                           (sends live URL)
                                        ↓
                            Agent Execution
                                        ↓
                          Format for Slack
                                        ↓
                        Update Message with Result
```

### Key Components

- **FastAPI**: Handles Slack webhook endpoint
- **SlackService**: Manages bot logic and Slack API calls
- **browser-use @sandbox**: Cloud-based browser automation
- **ChatBrowserUse LLM**: Powers the browser agent
- **Async processing**: Prevents Slack event timeouts

### Browser Profiles (Optional)

Browser profiles allow you to use authenticated sessions with persistent cookies and settings. This is useful for:
- Maintaining logged-in sessions across bot tasks
- Accessing authenticated content (Gmail, LinkedIn, etc.)
- Preserving custom browser settings and preferences

#### Setting Up a Browser Profile

1. **Go to the Browser-use Cloud dashboard**:
   - Visit [https://cloud.browser-use.com/#settings/profiles](https://cloud.browser-use.com/#settings/profiles)

2. **Import your local profile**:
   - Click **"Import local profile"** button
   - A command will appear on screen

3. **Run the sync command**:
   - Copy the command shown
   - Paste it into your terminal
   - Follow the terminal prompts to sync your browser profile
   - This will upload your local browser cookies and settings to the cloud

4. **Get your profile ID**:
   - Return to the cloud dashboard
   - Find your newly added profile in the list
   - Copy the **profile_id**

5. **Add to your `.env` file**:
   ```
   BROWSER_USE_PROFILE_ID=your-profile-id-here
   ```

6. **Restart the server** to apply the profile

Now your bot will use this authenticated profile for all browser tasks!

## Troubleshooting

### "Request URL responded with HTTP 500"

- Check your `.env` file has all required variables
- Ensure the server is running before setting the Request URL
- Check server logs for detailed error messages

### "Request verification failed"

- Verify your `SLACK_SIGNING_SECRET` is correct
- Check that ngrok URL matches the one in Slack Event Subscriptions

### Bot doesn't respond to mentions

- Ensure the bot is invited to the channel (`/invite @BotName`)
- Check Event Subscriptions includes `app_mention`
- Verify OAuth scopes are correctly set

### Python version error

- This project requires Python 3.11 or higher
- Check version: `python --version`
- Install 3.11+: `uv python install 3.11`

### ngrok URL expired

- Free ngrok URLs change on each restart
- Update the Request URL in Slack Event Subscriptions
- Consider ngrok paid plan for static URLs in production

## Development

### Project Structure

```
slack/
├── app/
│   ├── main.py       # FastAPI server & webhook endpoint
│   └── service.py    # SlackService & browser automation logic
├── .env              # Environment variables (not in git)
├── .env.example      # Environment template
├── pyproject.toml    # Project dependencies
└── README.md         # This file
```

### Running Tests

```bash
# No tests currently implemented
# TODO: Add pytest and test coverage
```

## Production Deployment

For production use:

1. Deploy to a cloud platform (Heroku, Railway, AWS, etc.)
2. Use a static HTTPS URL (no ngrok needed)
3. Update Slack Event Subscriptions Request URL to your production URL
4. Set environment variables in your hosting platform
5. Consider using browser profiles for authenticated sessions

## Links

- [browser-use Documentation](https://github.com/browser-use/browser-use)
- [Slack API Documentation](https://api.slack.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This template is provided as-is for use with browser-use. Feel free to modify and use it in your projects.
