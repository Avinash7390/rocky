"""Unified entrypoint: every integration built so far, wired into one
interactive session, gated by one shared permission gate.

Each integration only loads if its own config is present in .env — run
this with whatever subset of NOTION_TOKEN / GITHUB_TOKEN /
GOOGLE_CLIENT_ID+SECRET / SPOTIFY_CLIENT_ID+SECRET you've filled in, and
it'll wire up exactly that subset, printing what got skipped and why. This
is the entrypoint meant for testing everything together, per TRD §17; the
per-phase *_main.py scripts remain for testing one integration in
isolation.
"""

import asyncio
import os
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

sys.path.insert(0, str(Path(__file__).parent / ".claude" / "hooks"))
from permission_gate import can_use_tool  # noqa: E402

from tools import cost_guard  # noqa: E402

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


def _build_mcp_servers() -> tuple[dict, list[str], list[str]]:
    """Build the mcp_servers dict from whatever's configured in the
    environment. Returns (servers, active_names, skipped_reasons)."""
    servers: dict = {}
    active: list[str] = []
    skipped: list[str] = []

    if os.environ.get("NOTION_TOKEN"):
        from tools.notion_tool import notion_server

        servers["notion"] = notion_server
        active.append("notion")
    else:
        skipped.append("notion (missing NOTION_TOKEN)")

    if os.environ.get("GITHUB_TOKEN"):
        servers["github"] = {
            "type": "http",
            "url": GITHUB_MCP_URL,
            "headers": {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        }
        active.append("github")
    else:
        skipped.append("github (missing GITHUB_TOKEN)")

    if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
        from tools.calendar_tool import calendar_server
        from tools.drive_tool import drive_server
        from tools.gmail_tool import gmail_server
        from tools.youtube_tool import youtube_server

        servers["gmail"] = gmail_server
        servers["drive"] = drive_server
        servers["calendar"] = calendar_server
        servers["youtube"] = youtube_server
        active += ["gmail", "drive", "calendar", "youtube"]
    else:
        skipped.append(
            "gmail, drive, calendar, youtube (missing GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET)"
        )

    if os.environ.get("SPOTIFY_CLIENT_ID") and os.environ.get("SPOTIFY_CLIENT_SECRET"):
        from tools.spotify_tool import spotify_server

        servers["spotify"] = spotify_server
        active.append("spotify")
    else:
        skipped.append("spotify (missing SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET)")

    return servers, active, skipped


async def repl(options: ClaudeAgentOptions) -> None:
    print("Type a message and press enter. Ctrl-D or 'exit' to quit.\n")
    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                break
            if not user_input or user_input.lower() in {"exit", "quit"}:
                break

            try:
                cost_guard.check_budget()
            except cost_guard.BudgetExceededError as exc:
                print(f"\n[cost guard] {exc}\n")
                continue

            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="", flush=True)
                elif isinstance(message, ResultMessage):
                    print()
                    cost_guard.record_spend(message.total_cost_usd)


def main() -> None:
    servers, active, skipped = _build_mcp_servers()

    if not active:
        raise SystemExit(
            "No integrations are configured — set at least one of "
            "NOTION_TOKEN, GITHUB_TOKEN, GOOGLE_CLIENT_ID+SECRET, or "
            "SPOTIFY_CLIENT_ID+SECRET in .env before running this. "
            "See the per-phase tasks/*.md docs for how to get each one."
        )

    print(f"Active integrations: {', '.join(active)}")
    for reason in skipped:
        print(f"Skipped: {reason}")
    print()

    options = ClaudeAgentOptions(
        system_prompt=(
            "You are a helpful personal AI agent. You have access to the "
            f"following integrations: {', '.join(active)}."
        ),
        mcp_servers=servers,
        can_use_tool=can_use_tool,
    )

    try:
        asyncio.run(repl(options))
    except Exception as exc:
        raise SystemExit(f"Agent session failed: {exc}") from exc


if __name__ == "__main__":
    main()
