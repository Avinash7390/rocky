"""Gmail tools exposed to the orchestrator, per TRD §11.

Search is auto-approved by the permission gate; send is a write action and
blocks on confirmation — see .claude/hooks/permission_gate.py. The Google
API client is synchronous, so each call runs in a thread rather than
blocking the event loop.
"""

import asyncio
import base64
from email.mime.text import MIMEText
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import google_auth


def _search_sync(query: str, max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("gmail", "v1")
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    summaries = []
    for msg in results.get("messages", []):
        detail = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append(
            {
                "id": msg["id"],
                "from": headers.get("From"),
                "subject": headers.get("Subject"),
                "date": headers.get("Date"),
                "snippet": detail.get("snippet"),
            }
        )
    return summaries


def _send_sync(to: str, subject: str, body: str) -> str:
    service = google_auth.get_service("gmail", "v1")
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent["id"]


@tool(
    "gmail_search",
    "Search Gmail messages using Gmail search syntax (e.g. 'is:unread from:x@y.com'). "
    "Returns id/from/subject/date/snippet for each match.",
    {"query": str, "max_results": int},
)
async def gmail_search(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(
        _search_sync, args["query"], int(args.get("max_results") or 10)
    )
    return {"content": [{"type": "text", "text": str(results)}]}


@tool(
    "gmail_send",
    "Send an email from the authenticated Gmail account.",
    {"to": str, "subject": str, "body": str},
)
async def gmail_send(args: dict[str, Any]) -> dict[str, Any]:
    message_id = await asyncio.to_thread(_send_sync, args["to"], args["subject"], args["body"])
    return {"content": [{"type": "text", "text": f"Sent (message id: {message_id})"}]}


gmail_server = create_sdk_mcp_server("gmail", tools=[gmail_search, gmail_send])
