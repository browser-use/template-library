# Browser-Use Cloud Sandbox Template

Browser automation using the `@sandbox` decorator for cloud-based browser sessions with persistent authentication, proxy routing, and configurable timeouts.

## What is the @sandbox decorator?

The `@sandbox` decorator is a convenience wrapper that automatically configures browser-use to run in the cloud with custom settings:

- **Persistent Authentication**: Use saved cloud profiles to maintain login sessions across runs
- **Proxy Routing**: Route browser traffic through specific countries
- **Session Timeout**: Control how long the browser session stays active
- **Simplified Setup**: Automatically handles cloud configuration

## Features

- Cloud-based browser execution
- Persistent authentication via cloud profiles
- Country-specific proxy routing
- Configurable session timeouts
- Environment variable configuration

## Prerequisites

- Python 3.11 or higher
- Browser-Use API key from [cloud.browser-use.com](https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new)
- (Optional) Cloud Profile ID for persistent authentication

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

3. Get your Browser-Use API key:
   - Visit [https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new](https://cloud.browser-use.com/dashboard/settings?tab=api-keys&new)
   - Create a new API key
   - Add it to `.env` as `BROWSER_USE_API_KEY`

4. (Optional) Create a cloud profile for persistent authentication:
   - Visit [https://cloud.browser-use.com/#settings/profiles](https://cloud.browser-use.com/#settings/profiles)
   - Create a new profile and log in to your target website
   - Copy the Profile ID
   - Add it to `.env` as `CLOUD_PROFILE_ID`

## Configuration

The template uses environment variables loaded from `.env`:

```bash
# Required
BROWSER_USE_API_KEY=your-key-here

# Optional
CLOUD_PROFILE_ID=your-profile-id-here  # For persistent authentication
CLOUD_PROXY_COUNTRY_CODE=us            # Two-letter ISO country code (default: us)
CLOUD_TIMEOUT=60                       # Session timeout in minutes (default: 60)
```

## Usage

Run the script:
```bash
uv run main.py
```

The example task navigates to X.com and retrieves the most recent post from your timeline (requires authentication via cloud profile).

## Customization

### Change the task

Edit the `task` variable in `main.py`:
```python
task = "Your custom task here"
```

### Modify cloud settings

Update the `@sandbox` decorator parameters:
```python
@sandbox(
    cloud_profile_id=os.getenv('CLOUD_PROFILE_ID'),
    cloud_proxy_country_code='uk',  # Change country (two-letter ISO code)
    cloud_timeout=30,                # Change timeout (minutes)
)
```

### Available proxy countries

Use standard two-letter ISO country codes (e.g., `us`, `uk`, `de`, `jp`, `au`, `fr`, `ca`, etc.). See [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the complete list of country codes.

## How it works

1. The `@sandbox` decorator automatically configures `Browser(use_cloud=True)`
2. The browser parameter is injected into your `main()` function
3. You can use it like any other browser instance with the Agent
4. All browser operations run in the cloud with your specified settings

## Troubleshooting

### Authentication not working

- Make sure you've created a cloud profile at [cloud.browser-use.com/#settings/profiles](https://cloud.browser-use.com/#settings/profiles)
- Verify the `CLOUD_PROFILE_ID` is correctly set in `.env`
- Log in to the target website using the cloud profile UI first

### Session timeout too short

- Increase `CLOUD_TIMEOUT` in `.env` (value in minutes)
- Note: Longer sessions may incur higher costs

### Proxy not working

- Verify the country code is a valid two-letter ISO code
- Check your Browser-Use plan supports proxy features

## Learn More

- [Browser-Use Documentation](https://docs.browser-use.com)
- [Cloud Sandbox Guide](https://docs.browser-use.com/cloud/sandbox)
- [Cloud Profiles](https://docs.browser-use.com/cloud/profiles)

## License

Same as [browser-use](https://github.com/browser-use/browser-use)
