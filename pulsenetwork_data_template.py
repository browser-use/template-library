"""PulseNetwork data tools: your agent buys live data mid-task with x402.

Adds three tools to any browser-use agent:
  - pulse_catalog: free search across 950+ pay-per-call data endpoints
  - pulse_price:   free price check for any PulseNetwork endpoint (a bare 402 quote)
  - pulse_buy:     pay one endpoint with USDC on Base and return its JSON

Payments use the official x402 Python SDK. No API keys, no accounts: the wallet
is the identity. The private key stays in an env var; the LLM never sees it.
Per-call and per-session budget caps are enforced in code, and the buy tool
refuses any host outside PulseNetwork, so the agent cannot be talked into
paying somewhere else.

Setup:
  pip install browser-use "x402[httpx,evm]" httpx
  export PULSE_WALLET_KEY=0x...   # a throwaway wallet holding a few USDC on Base
  export OPENAI_API_KEY=sk-...    # or use any browser-use supported model

Catalog and docs: https://pulse.theaslangroupllc.com/llms.txt
"""

import asyncio
import os

import httpx
from browser_use import ActionResult, Agent, ChatOpenAI, Tools
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import x402HttpxClient
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.evm.signers import EthAccountSigner

CATALOG_URL = "https://pulse.theaslangroupllc.com/llms-full.txt"
ALLOWED_HOST_SUFFIX = ".theaslangroupllc.com"
MAX_PER_CALL_USD = float(os.getenv("PULSE_MAX_PER_CALL_USD", "0.50"))
SESSION_BUDGET_USD = float(os.getenv("PULSE_SESSION_BUDGET_USD", "2.00"))

tools = Tools()
_spent = {"usd": 0.0}
_catalog_cache = {"text": None}


def _quote_usd(url: str) -> float | None:
    """Ask the endpoint what it costs. A bare 402 quote is free and settles nothing."""
    r = httpx.get(url, timeout=30)
    if r.status_code != 402:
        return None
    for accept in r.json().get("accepts", []):
        if accept.get("network") == "eip155:8453":
            return int(accept["amount"]) / 1e6
    return None


@tools.action(
    description=(
        "Search the PulseNetwork catalog of 950+ pay-per-call data endpoints: "
        "crypto token safety, market scans, travel rights, sports, climate, "
        "compliance and more. Free. Returns matching lines with URLs and prices."
    )
)
async def pulse_catalog(query: str) -> ActionResult:
    if _catalog_cache["text"] is None:
        async with httpx.AsyncClient(timeout=30) as c:
            _catalog_cache["text"] = (await c.get(CATALOG_URL)).text
    q = query.lower()
    hits = [ln for ln in _catalog_cache["text"].splitlines() if q in ln.lower()][:20]
    return ActionResult(
        extracted_content="\n".join(hits) or "No matches. Try a broader term."
    )


@tools.action(
    description="Check the exact USD price of a PulseNetwork endpoint before buying. Free."
)
async def pulse_price(url: str) -> ActionResult:
    price = await asyncio.to_thread(_quote_usd, url)
    if price is None:
        return ActionResult(extracted_content="No Base x402 quote at that URL.")
    return ActionResult(extracted_content=f"{url} costs ${price:.3f} per call.")


@tools.action(
    description=(
        "Buy one PulseNetwork data call with USDC on Base and return its JSON. "
        "Use pulse_catalog first to find the endpoint URL and its query params."
    )
)
async def pulse_buy(url: str) -> ActionResult:
    host = httpx.URL(url).host or ""
    if not host.endswith(ALLOWED_HOST_SUFFIX):
        return ActionResult(
            extracted_content="Refused: this tool only pays PulseNetwork endpoints."
        )
    price = await asyncio.to_thread(_quote_usd, url)
    if price is None:
        return ActionResult(
            extracted_content="No Base x402 quote at that URL; nothing was paid."
        )
    if price > MAX_PER_CALL_USD:
        return ActionResult(
            extracted_content=f"Refused: ${price:.2f} exceeds the ${MAX_PER_CALL_USD:.2f} per-call cap."
        )
    if _spent["usd"] + price > SESSION_BUDGET_USD:
        return ActionResult(
            extracted_content=f"Refused: the ${SESSION_BUDGET_USD:.2f} session budget would be exceeded."
        )
    payer = x402Client()
    payer.register(
        "eip155:*",
        ExactEvmScheme(
            signer=EthAccountSigner(Account.from_key(os.environ["PULSE_WALLET_KEY"]))
        ),
    )
    async with x402HttpxClient(payer, timeout=90) as http:
        r = await http.get(url)
    if r.status_code != 200:
        return ActionResult(
            extracted_content=(
                f"Endpoint answered {r.status_code}, nothing useful was bought. "
                f"Check params via pulse_price. Body: {r.text[:300]}"
            )
        )
    _spent["usd"] += price
    return ActionResult(extracted_content=r.text[:6000])


async def main():
    agent = Agent(
        task=(
            "Someone on a forum is hyping the token CLAWSTR at address "
            "0xdca76ddec78cEd6449A70BD5Df5180ACa4a55386 on Robinhood Chain. "
            "Before anyone buys it: use pulse_catalog to find the token safety "
            "scanner, check its price with pulse_price, buy one scan for that "
            "address with chain=robinhood using pulse_buy, and summarize the "
            "verdict with its red and green flags."
        ),
        llm=ChatOpenAI(model="gpt-4.1-mini"),
        tools=tools,
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
