"""Google Drive tool exposed to the orchestrator, per TRD §11.

Read-only (`drive.readonly` scope) — no write path, so nothing here needs a
permission-gate "write" entry.
"""

import asyncio
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import google_auth


def _search_sync(query: str, max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("drive", "v3")
    escaped_query = query.replace("\\", "\\\\").replace("'", "\\'")
    results = (
        service.files()
        .list(
            q=f"name contains '{escaped_query}' and trashed = false",
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        )
        .execute()
    )
    return results.get("files", [])


@tool(
    "drive_search",
    "Search Google Drive files by name. Returns id/name/mimeType/modifiedTime/webViewLink.",
    {"query": str, "max_results": int},
)
async def drive_search(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(
        _search_sync, args["query"], int(args.get("max_results") or 10)
    )
    return {"content": [{"type": "text", "text": str(results)}]}


drive_server = create_sdk_mcp_server("drive", tools=[drive_search])
