# Agent Buys Live Data Mid-Task (x402)

A browser-use agent that pays for the data it needs, per call, while it works.

Most agents are stuck with whatever the model already knows plus whatever a page
happens to show. This template gives the agent a wallet and three tools, so when
a task needs a fact the model cannot know (is this token a honeypot, is this
flight owed compensation, has this product been recalled) the agent finds the
right endpoint, checks the price, pays a few cents in USDC on Base, and keeps
going.

There is no signup, no API key and no account. The wallet is the identity.

## The Tools

| Tool | Cost | What it does |
| --- | --- | --- |
| `pulse_catalog` | free | Searches 950+ pay-per-call endpoints. Returns each match as a complete URL with its price and its query parameters. |
| `pulse_price` | free | Reads the exact price of one endpoint from its 402 challenge. Settles nothing. |
| `pulse_buy` | the endpoint price | Pays one call with USDC on Base and returns the JSON. |

Typical prices run from $0.005 to $0.35 per call. The demo task costs about
$0.015.

## Spending Controls

The limits are in the code, not in the prompt, so the agent cannot be talked
past them by a web page or by its own reasoning:

- **Host allowlist.** `pulse_buy` refuses any URL outside PulseNetwork.
- **Per-call cap and session budget.** Enforced as an x402 payment policy, which
  inspects the 402 challenge that is actually being signed. A price that changes
  between the quote and the payment cannot slip through, because the quote is
  not what authorizes the spend.
- **A lock around the buy path**, so two concurrent tool calls cannot both spend
  the last of the budget.
- **The key never reaches the model.** It is read from the environment inside the
  tool. The agent passes a URL and gets JSON back.

## Setup

### 1. Navigate to the project directory

```bash
cd pulsenetwork-data
```

### 2. Create a wallet and fund it

Generate a throwaway key and send it a few dollars of USDC on Base. Do not use a
wallet that holds anything you care about. A dollar or two is enough for
hundreds of calls.

### 3. Configure the environment

```bash
cp .env.example .env
```

Edit `.env` and set `PULSE_WALLET_KEY` and your model key. You can also lower
`PULSE_MAX_PER_CALL_USD` and `PULSE_SESSION_BUDGET_USD` from their defaults of
$0.50 and $2.00.

### 4. Install dependencies

```bash
uv sync
```

This installs `browser-use`, the official `x402` Python SDK with its httpx and
EVM extras, and `eth-account`.

### 5. Run it

```bash
uv run main.py
```

The demo task scans a real token on Robinhood Chain for rug and honeypot risk
before anyone buys it, and reports the verdict with its red and green flags.

## Using It In Your Own Agent

Import the `tools` object and hand it to any `Agent`:

```python
from main import tools

agent = Agent(task="...", llm=ChatOpenAI(model="gpt-4.1-mini"), tools=tools)
```

The tools compose with browser-use's own actions, so an agent can read a page,
buy a fact that the page does not contain, and act on both.

## Troubleshooting

| What you see | What it means |
| --- | --- |
| `Refused: PULSE_WALLET_KEY is not set` | No `.env`, or the key line is still the placeholder. |
| `Refused, nothing was paid: the endpoint asked for $X` | The price is above your remaining allowance. Raise the cap or pick a cheaper endpoint. |
| `Refused: the session budget is spent` | Restart the process, or raise `PULSE_SESSION_BUDGET_USD`. |
| `The payment did not complete` | Usually an unfunded wallet. Check the USDC balance on Base. |
| `Endpoint answered 400` | A missing or malformed parameter. `pulse_catalog` lists what each endpoint takes. |

## Links

- Catalog and docs: https://pulse.theaslangroupllc.com/llms.txt
- Machine-readable search: https://pulse.theaslangroupllc.com/api/catalog?q=token+safety
- x402 protocol: https://x402.org

## Disclosure

PulseNetwork is operated by The Aslan Group LLC, who wrote this template. The
tools only pay PulseNetwork endpoints, which is a deliberate safety limit rather
than a claim that nothing else is worth buying. The pattern itself is generic:
any x402 seller can be reached the same way by changing the host allowlist and
the catalog URL.
