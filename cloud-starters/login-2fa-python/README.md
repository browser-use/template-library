# Login with password + TOTP 2FA on a cloud browser

A browser-use `Agent` on a cloud browser logs in with a username, password and a TOTP 2FA code, then keeps the login in a cloud profile so later runs skip it.

Browser Use Cloud browsers cost **$0.02 per browser-hour, billed per second**.

## Run

```bash
uvx browser-use init --template cloud-login-2fa
cd cloud-login-2fa
cp .env.example .env   # add BROWSER_USE_API_KEY
uv sync
uv run main.py
```

Get an API key at https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new

## How it works

- Set `LOGIN_DOMAIN`, `LOGIN_URL`, `SITE_USERNAME`, `SITE_PASSWORD` and `SITE_TOTP_SECRET` (the base32 secret behind the 2FA QR code) in `.env`.
- `sensitive_data` maps placeholder names to values. The task refers to `site_username`, `site_password` and `site_bu_2fa_code`; real values are filled in only when typed, and only on matching domains. Typed values can still appear in page content, so use a dedicated account.
- A placeholder ending in `bu_2fa_code` holds a TOTP secret, and the agent types the current 6-digit code.
- `allowed_domains=["*.<domain>"]` keeps the agent's navigation on that site.
- With `CLOUD_PROFILE_ID` set, cookies are saved to the profile when the browser stops, so the next run starts logged in. Create one under Dashboard > Profiles (https://cloud.browser-use.com/settings?tab=profiles).

## Next

SMS or email codes instead of TOTP: see https://docs.browser-use.com/cloud/guides/2fa
