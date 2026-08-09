"""PulseNetwork data tools: your agent buys live data mid-task with x402.

Adds three tools to any browser-use agent:
  - pulse_catalog: free search across 950+ pay-per-call data endpoints
  - pulse_price:   free price check for one endpoint (a bare 402 quote)
  - pulse_buy:     pay one endpoint with USDC on Base and return its JSON

Payments use the official x402 Python SDK. No API keys, no accounts: the wallet
is the identity. The private key stays in an env var; the LLM never sees it.

Three controls live in code, not in the prompt, so the agent cannot talk its way
past them:
  - host allowlist: every tool that makes an outbound request refuses any URL
    that is not an https PulseNetwork endpoint, the free ones included
  - per-call cap and session budget: enforced as an x402 payment policy, so the
    caps are checked against the 402 challenge that is actually signed, and
    against USDC on Base specifically, since that is the unit they count in
  - a lock around the buy path, so two concurrent calls cannot both spend the
    last of the budget

Docs: https://pulse.theaslangroupllc.com/llms.txt
"""

import asyncio
import os

import httpx
from browser_use import ActionResult, Agent, ChatOpenAI, Tools
from dotenv import load_dotenv
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import x402HttpxClient
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.evm.signers import EthAccountSigner

load_dotenv()

CATALOG_URL = "https://pulse.theaslangroupllc.com/api/catalog"
ALLOWED_HOST_SUFFIX = ".theaslangroupllc.com"
BASE_NETWORK = "eip155:8453"
# The caps are counted in USDC's 6 decimals, so the asset has to be pinned too.
# The same number of atomic units in an 8-decimal or 18-decimal token would be a
# completely different amount of money, and the cap would not notice.
BASE_USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
USDC_UNITS = 10**6

# Must match the placeholder shipped in .env.example.template.
PLACEHOLDER_KEY_PREFIX = "0xyour"

MAX_PER_CALL_USD = float(os.getenv("PULSE_MAX_PER_CALL_USD", "0.50"))
SESSION_BUDGET_USD = float(os.getenv("PULSE_SESSION_BUDGET_USD", "2.00"))

tools = Tools()
_spent = {"usd": 0.0}
_buy_lock = asyncio.Lock()


class _PaymentGuard:
    """Binds the budget caps to the challenge the SDK actually signs.

    Quoting the price and then paying are two separate HTTP requests, so a quote
    taken beforehand proves nothing about what the second request will be asked
    to sign. This runs as an x402 payment policy instead: it sees the real 402
    challenge inside the paid request and drops anything that is not USDC on
    Base within budget. If nothing survives, the SDK raises and no payload is
    ever created, so nothing is signed and nothing settles.
    """

    def __init__(self, allowance_usd: float) -> None:
        self.allowance_usd = allowance_usd
        self._allowance_atomic = int(round(allowance_usd * USDC_UNITS))
        self.refusal: str | None = None
        self.signed_usd = 0.0

    def policy(self, _version: int, requirements: list) -> list:
        keep = []
        for req in requirements:
            if getattr(req, "network", None) != BASE_NETWORK:
                continue
            if str(getattr(req, "asset", "")).lower() != BASE_USDC:
                self.refusal = (
                    "the endpoint asked to be paid in a token other than USDC on Base, "
                    "which the budget caps cannot price"
                )
                continue
            amount = int(req.get_amount())
            if amount > self._allowance_atomic:
                self.refusal = (
                    f"the endpoint asked for ${amount / USDC_UNITS:.3f}, more than the "
                    f"${self.allowance_usd:.3f} left under the per-call cap and session budget"
                )
                continue
            keep.append(req)
        if not keep and self.refusal is None:
            self.refusal = "the endpoint offered no USDC-on-Base payment option"
        return keep

    def record(self, ctx) -> None:
        # Fires once per created payload, before it is sent. Accumulates rather
        # than overwrites: if the SDK retries with a fresh payload, count both.
        # Over-counting only shrinks the budget; under-counting would overspend.
        self.signed_usd += int(ctx.selected_requirements.get_amount()) / USDC_UNITS


MAX_PARAMS_SHOWN = 6


def _describe(entry: dict) -> str:
    """One endpoint as the agent needs it: full URL, price, and its parameters."""
    price = entry.get("price_usd")
    tag = "FREE" if not price else f"${price:.3f}"
    lines = [
        f"{tag}  {entry.get('method', 'GET')} {entry['url']}",
        f"      {entry.get('description', '')}",
    ]
    params = list((entry.get("params") or {}).items())
    # Required parameters first: a call fails without them, and some endpoints
    # carry a dozen optional ones that would swamp the model's context.
    params.sort(key=lambda kv: not kv[1].get("required"))
    for name, spec in params[:MAX_PARAMS_SHOWN]:
        need = "required" if spec.get("required") else "optional"
        example = spec.get("example")
        hint = f", e.g. {example}" if example is not None else ""
        lines.append(f"      - {name} ({need}): {spec.get('description', '')}{hint}")
    if len(params) > MAX_PARAMS_SHOWN:
        lines.append(f"      - plus {len(params) - MAX_PARAMS_SHOWN} more optional parameters")
    return "\n".join(lines)


def _reject_url(url: str) -> str | None:
    """Refusal message if this URL is not a PulseNetwork endpoint, else None.

    Every tool that makes an outbound request runs this, not just the paying one.
    The agent reads live web pages while it works, so a page can try to talk it
    into fetching an internal address; a free tool with no allowlist would still
    make that request on the agent's behalf.
    """
    try:
        parsed = httpx.URL(url)
    except Exception:
        return f"Refused: {url!r} is not a usable URL."
    if parsed.scheme != "https":
        return "Refused: only https PulseNetwork URLs are allowed."
    if not (parsed.host or "").endswith(ALLOWED_HOST_SUFFIX):
        return "Refused: these tools only reach PulseNetwork endpoints."
    return None


async def _quote_usd(url: str) -> float | None:
    """Ask an endpoint what it costs. A bare 402 quote is free and settles nothing."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url)
        if r.status_code != 402:
            return None
        for accept in r.json().get("accepts", []):
            if accept.get("network") == BASE_NETWORK:
                return int(accept["amount"]) / USDC_UNITS
    except Exception:
        return None
    return None


@tools.action(
    description=(
        "Search the PulseNetwork catalog of 950+ pay-per-call data endpoints: "
        "crypto token safety, market scans, travel rights, sports, climate, "
        "compliance and more. Free. Returns each match as a complete URL with "
        "its price and its query parameters, ready to pass to pulse_buy."
    )
)
async def pulse_catalog(query: str) -> ActionResult:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(CATALOG_URL, params={"q": query, "limit": 6})
        r.raise_for_status()
        results = r.json().get("results") or []
    except Exception as exc:
        return ActionResult(
            extracted_content=f"The PulseNetwork catalog is unreachable right now ({exc}); nothing was searched."
        )
    if not results:
        return ActionResult(
            extracted_content=(
                f'No PulseNetwork endpoint matches "{query}". Try one broad noun instead, '
                'such as "token", "flight", "recall", "sanctions" or "weather".'
            )
        )
    body = "\n".join(_describe(e) for e in results)
    return ActionResult(
        extracted_content=(
            f"PulseNetwork endpoints matching '{query}' (append the parameters as a query string, "
            f"then call pulse_buy with the full URL):\n{body}"
        )
    )


@tools.action(
    description="Check the exact USD price of a PulseNetwork endpoint before buying. Free."
)
async def pulse_price(url: str) -> ActionResult:
    refusal = _reject_url(url)
    if refusal:
        return ActionResult(extracted_content=refusal)
    price = await _quote_usd(url)
    if price is None:
        return ActionResult(extracted_content="No USDC-on-Base x402 quote at that URL.")
    return ActionResult(
        extracted_content=(
            f"{url} costs ${price:.3f} per call. "
            f"${SESSION_BUDGET_USD - _spent['usd']:.2f} of the session budget is left."
        )
    )


@tools.action(
    description=(
        "Buy one PulseNetwork data call with USDC on Base and return its JSON. "
        "Use pulse_catalog first to get the full endpoint URL and its parameters."
    )
)
async def pulse_buy(url: str) -> ActionResult:
    refusal = _reject_url(url)
    if refusal:
        return ActionResult(extracted_content=refusal)

    key = (os.getenv("PULSE_WALLET_KEY") or "").strip()
    # The shipped .env.example carries a placeholder, so an unedited copy has to
    # read as "not configured" rather than as a broken key.
    if not key or key.lower().startswith(PLACEHOLDER_KEY_PREFIX):
        return ActionResult(
            extracted_content=(
                "Refused: PULSE_WALLET_KEY is not set, so no payment is possible. "
                "Copy .env.example to .env and replace the placeholder with a funded "
                "throwaway wallet key."
            )
        )
    try:
        signer = EthAccountSigner(Account.from_key(key))
    except Exception:
        return ActionResult(
            extracted_content=(
                "Refused: PULSE_WALLET_KEY is not a valid private key "
                "(expected 0x followed by 64 hex characters)."
            )
        )

    async with _buy_lock:
        allowance = min(MAX_PER_CALL_USD, SESSION_BUDGET_USD - _spent["usd"])
        if allowance <= 0:
            return ActionResult(
                extracted_content=f"Refused: the ${SESSION_BUDGET_USD:.2f} session budget is spent."
            )

        guard = _PaymentGuard(allowance)
        payer = x402Client()
        payer.register(BASE_NETWORK, ExactEvmScheme(signer=signer))
        payer.register_policy(guard.policy)
        payer.on_after_payment_creation(guard.record)

        try:
            async with x402HttpxClient(payer, timeout=90) as http:
                r = await http.get(url)
        except Exception as exc:
            _spent["usd"] += guard.signed_usd
            if guard.refusal and not guard.signed_usd:
                return ActionResult(
                    extracted_content=f"Refused, nothing was paid: {guard.refusal}."
                )
            return ActionResult(extracted_content=f"The payment did not complete: {exc}")

        _spent["usd"] += guard.signed_usd

    if r.status_code != 200:
        return ActionResult(
            extracted_content=(
                f"Endpoint answered {r.status_code}, nothing useful was bought. "
                f"Check the parameters against pulse_catalog. Body: {r.text[:300]}"
            )
        )
    return ActionResult(extracted_content=r.text[:6000])


async def main():
    agent = Agent(
        task=(
            "Someone on a forum is hyping the token CLAWSTR at address "
            "0xdca76ddec78cEd6449A70BD5Df5180ACa4a55386 on Robinhood Chain. "
            "Before anyone buys it: use pulse_catalog to find the PulseNetwork "
            "endpoint that scans an EVM token for safety, then call pulse_buy with "
            "that endpoint plus address and chain=robinhood, and summarize the "
            "verdict with its red and green flags."
        ),
        llm=ChatOpenAI(model="gpt-4.1-mini"),
        tools=tools,
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
