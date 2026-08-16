"""Phase 2 entrypoint: Notion tool + permission gate wired into the Agent SDK.

Proves the auth-token -> integration-layer pattern (README.md's Suggested
Build Order, step 2) and
exercises the permission gate on a real write action (page creation) before
anything higher-stakes is involved.
"""

import asyncio
import os

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

from hooks.permission_gate import can_use_tool
from tools.notion_tool import notion_server


def _require_config() -> str:
    root_page_id = os.environ.get("NOTION_ROOT_PAGE_ID")
    if not os.environ.get("NOTION_TOKEN") or not root_page_id:
        raise SystemExit(
            "Set NOTION_TOKEN and NOTION_ROOT_PAGE_ID in .env before "
            "running this. See tasks/02-notion-integration.md for how to "
            "create the internal integration and share your 'Agent Access' "
            "page with it."
        )
    return root_page_id


async def run(prompt: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful personal AI agent with access to Notion.",
        mcp_servers={"notion": notion_server},
        # Deliberately no allowed_tools: an allowed_tools entry that names a
        # whole tool (no "(...)" specifier) auto-approves it *before*
        # can_use_tool runs — see claude_agent_sdk.types._whole_tool_allowed
        # and CanUseToolShadowedWarning. Listing notion_create_page there
        # would silently bypass the permission gate for the one write action
        # it exists to protect. Leaving allowed_tools unset (default: no
        # restriction) means every MCP tool call falls through to
        # can_use_tool, which is what actually gates it.
        can_use_tool=can_use_tool,
    )
    reply_parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    reply_parts.append(block.text)
    return "".join(reply_parts)


async def main() -> None:
    root_page_id = _require_config()
    prompt = (
        f"Read the Notion page {root_page_id} and tell me its title. Then "
        "create a new child page under it titled 'Agent smoke test' with "
        "the content 'Created by the Phase 2 Notion integration test.'"
    )
    try:
        reply = await run(prompt)
    except Exception as exc:
        raise SystemExit(f"Notion integration run failed: {exc}") from exc
    print(reply)


if __name__ == "__main__":
    asyncio.run(main())
