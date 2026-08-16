"""Low-level Notion API client: rate-limited, backoff-aware, current API version.

Notion allows ~3 req/s per integration and returns 429s on bursts, and
reading one page fans out into several calls (page -> block children ->
nested blocks). Every call goes through a small semaphore + exponential
backoff rather than firing sequentially with no throttling (see README.md's
Notion integration deep dive subsection).
"""

import asyncio
import os
from typing import Any

import httpx

NOTION_API_VERSION = "2025-09-03"
NOTION_BASE_URL = "https://api.notion.com/v1"

_MAX_CONCURRENT_REQUESTS = 3  # matches Notion's ~3 req/s average
_MAX_RETRIES = 5
_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)


class NotionConfigError(RuntimeError):
    """Raised when required Notion configuration (the integration token) is missing."""


def _require_token() -> str:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise NotionConfigError(
            "NOTION_TOKEN is not set. Create an internal integration at "
            "https://www.notion.so/my-integrations, share your 'Agent Access' "
            "page with it, and set NOTION_TOKEN in .env "
            "(see tasks/02-notion-integration.md)."
        )
    return token


async def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {_require_token()}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    url = f"{NOTION_BASE_URL}{path}"

    delay = 1.0
    async with _semaphore, httpx.AsyncClient(timeout=30.0) as client:
        for _ in range(_MAX_RETRIES):
            response = await client.request(method, url, headers=headers, **kwargs)
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", delay))
                await asyncio.sleep(retry_after)
                delay *= 2
                continue
            response.raise_for_status()
            return response.json()

    raise RuntimeError(f"Notion API rate-limited after {_MAX_RETRIES} retries: {method} {path}")


async def get_data_source_id(database_id: str) -> str:
    """Look up a database's (first) data_source_id.

    Since API version 2025-09-03, a 'database' is a container that can hold
    multiple data sources — most query/write calls need data_source_id, not
    database_id, despite what pre-2025 docs/tutorials assume.
    """
    data = await _request("GET", f"/databases/{database_id}")
    sources = data.get("data_sources", [])
    if not sources:
        raise RuntimeError(f"Database {database_id} has no data sources")
    return sources[0]["id"]


async def get_page(page_id: str) -> dict[str, Any]:
    return await _request("GET", f"/pages/{page_id}")


async def get_block_children(block_id: str, *, recursive: bool = True) -> list[dict[str, Any]]:
    """Fetch a block's children, optionally recursing into nested blocks."""
    children: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = await _request("GET", f"/blocks/{block_id}/children", params=params)
        children.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]

    if recursive:
        for block in children:
            if block.get("has_children"):
                block["children"] = await get_block_children(block["id"], recursive=True)

    return children


async def create_page(
    parent_page_id: str, title: str, content: str | None = None
) -> dict[str, Any]:
    """Create a page under parent_page_id with a plain-text title and optional body paragraph."""
    payload: dict[str, Any] = {
        "parent": {"page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    }
    if content:
        payload["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": content}}]},
            }
        ]
    return await _request("POST", "/pages", json=payload)
