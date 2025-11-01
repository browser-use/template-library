# AgentMail Template

Automate account creation with 2FA email verification using Browser-Use and AgentMail for temporary email inbox management.

## What This Does

This template demonstrates automated account creation with email-based 2FA verification. The agent will:

1. Create a temporary email inbox via AgentMail
2. Navigate to a registration page (default: Reddit)
3. Fill out the registration form with the temporary email
4. Retrieve 2FA verification codes from incoming emails
5. Complete email verification
6. Perform authenticated actions (e.g., like a post)

The template uses custom email tools that integrate AgentMail's temporary inbox API with Browser-Use's agent capabilities, enabling fully automated workflows that require email verification.

## Setup

### 1. Get Your API Keys

You'll need two API keys:

#### AgentMail API Key
For creating temporary email inboxes:
1. Go to [https://docs.agentmail.to/api-reference/api-keys/create](https://docs.agentmail.to/api-reference/api-keys/create)
2. Sign up for an account
3. Create your API key
4. Copy the key

#### Browser-Use API Key
For the ChatBrowserUse LLM:
1. Go to [https://browser-use.com/](https://browser-use.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Copy the key

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add both API keys:
```bash
AGENTMAIL_API_KEY=your-key-here
BROWSER_USE_API_KEY=your-key-here
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

### Basic Usage (Reddit Account Creation)

```bash
uv run main.py
```

This will:
- Create a temporary email inbox
- Navigate to reddit.com
- Create a new account using the temporary email
- Verify the email with 2FA code
- Like the latest post on r/elon

### Customizing the Task

Edit the `TASK` variable in `main.py` to automate different workflows:

```python
TASK = """
Go to example.com, create a new account using get_email_address,
verify the email with get_latest_email, and complete the onboarding.
"""
```

### Browser Configuration

By default, the template uses Chrome. Update the browser path in `main.py` if needed:

```python
# For macOS
browser = Browser(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

# For Linux
browser = Browser(executable_path='/usr/bin/google-chrome')

# For Windows
browser = Browser(executable_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
```

## How It Works

### EmailTools Class

The `EmailTools` class (in `email_tools.py`) provides two main actions that the Browser-Use agent can call:

#### 1. `get_email_address()`
- Creates or retrieves a temporary email inbox
- Returns the email address for the agent to use in forms
- Example: `user123@agentmail.to`

#### 2. `get_latest_email(max_age_minutes=5)`
- Checks for unread emails from the last N minutes
- If none found, waits up to 30 seconds for new emails via WebSocket
- Returns the email content including 2FA codes
- Automatically marks emails as read

### Workflow Example

1. **Agent starts**: Creates temporary inbox with `get_email_address()`
2. **Fill form**: Uses the email address in registration form
3. **Wait for verification**: Calls `get_latest_email()` to retrieve verification code
4. **Extract code**: Agent reads the email content and finds the 2FA code
5. **Complete verification**: Enters code and continues the workflow

### HTML Email Handling

The EmailTools class automatically converts HTML emails to plain text for easier parsing by the LLM, extracting 2FA codes and verification links.

## Customization

### For Different Services

To adapt this template for other account creation flows:

1. **Update the URL**: Change the service URL in `main.py`:
   ```python
   TASK = """
   Go to yourservice.com, create a new account (use get_email_address)...
   """
   ```

2. **Adjust the task steps**: Update instructions to match the service's registration flow

3. **Configure email timeout**: If verification emails are slow, increase the timeout:
   ```python
   tools = EmailTools(email_client=email_client, inbox=inbox, email_timeout=60)
   ```

### Using Different LLMs

The template uses `ChatBrowserUse()` by default. You can switch to other models:

```python
from langchain_openai import ChatOpenAI

# Use OpenAI GPT-4
llm = ChatOpenAI(model='gpt-4o')

# Use OpenAI o3 for complex multi-step tasks
llm = ChatOpenAI(model='o3')
```

### Multiple Inboxes

For parallel account creation, create separate inboxes:

```python
# Create multiple inboxes
inbox1 = await email_client.inboxes.create()
inbox2 = await email_client.inboxes.create()

# Use different tools for each agent
tools1 = EmailTools(email_client=email_client, inbox=inbox1)
tools2 = EmailTools(email_client=email_client, inbox=inbox2)
```

## Troubleshooting

### Email Not Received

- **Check spam/delivery**: Some services may not send to temporary email addresses
- **Increase timeout**: Set `email_timeout=60` or higher in EmailTools
- **Check AgentMail status**: Verify your API key and account status at agentmail.to
- **Manual test**: Create an inbox manually at agentmail.to to test email delivery

### 2FA Code Not Found

- **Email format**: The agent parses both plain text and HTML emails
- **Check email content**: Add logging to see what the agent receives
- **Update task prompt**: Give the agent specific instructions on where to find the code:
  ```python
  TASK = """
  ...retrieve the 6-digit verification code from the email subject line...
  """
  ```

### API Key Issues

- **Key not loaded**: Check that `.env` file exists and contains `AGENTMAIL_API_KEY`
- **Invalid key**: Verify the key at [https://agentmail.to/](https://agentmail.to/)
- **Rate limits**: Free tier has limits on inbox creation - check your dashboard

### Browser Path Errors

If you see browser launch errors:
- Verify the browser executable path is correct for your system
- Try using the system default: `Browser()` without specifying a path
- Install Chrome if not already installed

## Advanced Usage

### Batch Account Creation

Create multiple accounts programmatically:

```python
async def create_accounts(count: int):
    email_client = AsyncAgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))

    for i in range(count):
        inbox = await email_client.inboxes.create()
        tools = EmailTools(email_client=email_client, inbox=inbox)

        llm = ChatBrowserUse()
        browser = Browser()
        agent = Agent(task=TASK, tools=tools, llm=llm, browser=browser)

        await agent.run()
        await asyncio.sleep(10)  # Rate limiting
```

### Custom Email Actions

Extend EmailTools with custom actions:

```python
class CustomEmailTools(EmailTools):
    def register_email_tools(self):
        super().register_email_tools()

        @self.action('Search for emails with specific subject')
        async def search_emails(subject_keyword: str) -> str:
            inbox = await self.get_or_create_inbox_client()
            emails = await self.email_client.inboxes.messages.list(
                inbox_id=inbox.inbox_id
            )
            # Filter by subject keyword
            matching = [e for e in emails.messages if subject_keyword in e.subject]
            return f"Found {len(matching)} emails matching '{subject_keyword}'"
```

### Integration with Password Managers

Store credentials after account creation:

```python
import json

async def save_credentials(email: str, password: str, service: str):
    with open('credentials.json', 'a') as f:
        json.dump({
            'service': service,
            'email': email,
            'password': password,
            'created_at': datetime.now().isoformat()
        }, f)
        f.write('\n')
```

## Privacy & Ethics

**Important considerations**:

- Only create accounts for legitimate purposes
- Respect service terms of service (some prohibit automated account creation)
- Do not use for spam, fraud, or malicious activities
- Be mindful of rate limits and server load
- Temporary emails may be rejected by some services
- Some services track and ban temporary email domains
- Use for testing, development, and authorized automation only

## Service Compatibility

This template works best with services that:
- Accept temporary email addresses
- Send plain text or HTML emails (not image-based codes)
- Have simple registration flows
- Don't require phone verification

May not work with:
- Banking or financial services (stricter verification)
- Services that block temporary email domains
- Services requiring phone or ID verification
- Services with aggressive bot detection

## Support

For issues specific to:
- **Browser-Use**: [https://docs.browser-use.com](https://docs.browser-use.com)
- **AgentMail**: [https://agentmail.to/](https://agentmail.to/)
- **This template**: Check the browser-use/template-library repository

## Example Use Cases

- **Testing**: Automated testing of registration flows
- **Development**: Creating test accounts for development environments
- **QA**: Validating email verification systems
- **Demos**: Setting up demo accounts for presentations
- **Research**: Studying account creation patterns across services
