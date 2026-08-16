"""Notion tools exposed to the orchestrator (README.md's Notion integration
deep dive subsection).

Read is auto-approved by the permission gate; create is a write action and
blocks on confirmation — see hooks/permission_gate.py.
"""

from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import notion_client


@tool(
    "notion_read_page",
    "Read a Notion page's title and content (block children, recursively).",
    {"page_id": str},
)
async def notion_read_page(args: dict[str, Any]) -> dict[str, Any]:
    page = await notion_client.get_page(args["page_id"])
    blocks = await notion_client.get_block_children(args["page_id"])
    return {"content": [{"type": "text", "text": str({"page": page, "blocks": blocks})}]}


@tool(
    "notion_create_page",
    "Create a new Notion page as a child of an existing page. Pass an empty "
    "string for content if the page should have no body text.",
    {"parent_page_id": str, "title": str, "content": str},
)
async def notion_create_page(args: dict[str, Any]) -> dict[str, Any]:
    page = await notion_client.create_page(
        args["parent_page_id"], args["title"], args.get("content") or None
    )
    url = page.get("url", page.get("id"))
    return {"content": [{"type": "text", "text": f"Created page: {url}"}]}


notion_server = create_sdk_mcp_server("notion", tools=[notion_read_page, notion_create_page])
