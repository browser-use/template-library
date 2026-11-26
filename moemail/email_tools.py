"""Disposable inbox tools for a browser-use agent, backed by MoeMail (https://moemail.app)."""

import os
import re

import httpx
from browser_use import Tools

API_URL = os.getenv("MOEMAIL_API_URL", "https://moemail.app").rstrip("/")


class MoeMailTools(Tools):
    def __init__(self, api_key: str | None = None, expiry_ms: int = 3_600_000):
        super().__init__()
        self.http = httpx.AsyncClient(
            base_url=API_URL,
            headers={"X-API-Key": api_key or os.environ["MOEMAIL_API_KEY"]},
            timeout=70,
        )
        self.expiry_ms = expiry_ms  # 1 hour; 600000, 86400000 and 259200000 also work
        self.mailbox: dict | None = None
        self.cursor: str | None = None

        @self.action("Get the email address to use in a sign-up form. Creates a disposable inbox on first use.")
        async def get_email_address() -> str:
            return (await self.ensure_mailbox())["email"]

        @self.action("Wait up to 50 seconds for the next email in the inbox and return its sender, subject and text.")
        async def wait_for_email() -> str:
            box = await self.ensure_mailbox()
            # A fresh mailbox: since=0 also returns mail that arrived before this call.
            params = {"timeout": 50, "since": self.cursor or "0"}
            r = await self.http.get(f"/api/emails/{box['id']}/wait", params=params)
            r.raise_for_status()
            data = r.json()
            self.cursor = data["cursor"]
            if not data["messages"]:
                return "No email yet. Call wait_for_email again."
            m = data["messages"][-1]
            body = m["content"] or re.sub(r"<[^>]+>", " ", m["html"] or "")
            return f"From: {m['from_address']}\nSubject: {m['subject']}\n\n{body[:4000]}"

    async def ensure_mailbox(self) -> dict:
        if self.mailbox:
            return self.mailbox
        config = (await self.http.get("/api/config")).raise_for_status().json()
        domain = config["emailDomains"].split(",")[0].strip()
        r = await self.http.post("/api/emails/generate", json={"expiryTime": self.expiry_ms, "domain": domain})
        r.raise_for_status()
        self.mailbox = r.json()  # {"id": ..., "email": ...}
        return self.mailbox

    async def cleanup(self) -> None:
        if self.mailbox:
            await self.http.delete(f"/api/emails/{self.mailbox['id']}")
        await self.http.aclose()
