# MoeMail Template

Test a sign-up flow end to end: a Browser-Use agent fills in your registration form with a
disposable [MoeMail](https://moemail.app) address, waits for the verification email, and follows
its link or enters its code.

## What This Does

The agent will:

1. Create a disposable inbox via the MoeMail API (it lives for one hour)
2. Open your sign-up page (`SIGNUP_URL`) and fill in the form with that address
3. Wait for the verification email and read it
4. Follow the verification link or enter the code
5. Report whether verification succeeded, then delete the inbox

Point it at a site you own or are allowed to test, such as your app's staging environment.

## Setup

### 1. Get Your API Keys

#### MoeMail API Key
1. Sign up at [https://moemail.app](https://moemail.app) (the free plan is enough)
2. Open Profile → API Keys and create a key

MoeMail is open source, so you can also run it yourself and set `MOEMAIL_API_URL` to your deployment.

#### Browser-Use API Key
For the ChatBrowserUse LLM: get a key at [https://browser-use.com/](https://browser-use.com/).

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
MOEMAIL_API_KEY=your-key-here
BROWSER_USE_API_KEY=your-key-here
SIGNUP_URL=http://localhost:3000/signup
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

```bash
uv run main.py
```

Edit the `TASK` in `main.py` to match your sign-up flow (extra fields, onboarding steps after
verification, and so on).

## How It Works

`MoeMailTools` (in `email_tools.py`) gives the agent two actions:

- **`get_email_address()`** creates the inbox on first use (`POST /api/emails/generate`) and returns its address.
- **`wait_for_email()`** long-polls `GET /api/emails/{id}/wait` for up to 50 seconds and returns the
  sender, subject and text of the newest email. The first call passes `since=0`, so an email that
  arrived while the agent was still submitting the form is returned at once; later calls pass the
  returned `cursor`, so each call only reports newer mail.

`cleanup()` deletes the inbox when the run ends. The tools talk to the plain REST API with `httpx`,
so there is no SDK to install.

## Troubleshooting

- **No email arrives**: check that your app actually sends the email, and that it does not reject
  the MoeMail domain. Call `wait_for_email` again; each call waits up to 50 seconds.
- **401 errors**: check `MOEMAIL_API_KEY` in `.env`, and that the key has not expired.
- **Self-hosted MoeMail**: set `MOEMAIL_API_URL` to your deployment's base URL.
