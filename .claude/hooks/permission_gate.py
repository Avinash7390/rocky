"""Static risk-tier permission gate (TRD §9, §15).

Risk-tier classification is a table you maintain per tool, not something the
model decides about itself. Read-only tools auto-approve; write/destructive
tools block on confirmation.

No trigger webhook server exists yet (§10 is separate build-order work from
tool integrations), so "ask" is a blocking terminal prompt for now — swap
`_confirm` for a round-trip over the trigger channel once §10's server
exists, without changing the risk table or the `can_use_tool` contract.

Tool names for external MCP servers (GitHub, Google Workspace, Spotify)
aren't guaranteed stable across server versions, and this file can't
enumerate every tool a remote server exposes without introspecting it live.
That's fine by design: unclassified tools default to "write" (ask) below,
never to silent allow, so a missing table entry is a minor annoyance
(one extra confirmation prompt) rather than a safety gap.
"""

import asyncio
import os
from typing import Any, Literal

from claude_agent_sdk import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

RiskTier = Literal["read", "write", "destructive"]

# Dev/staging mode (TRD §15 flowchart): in "dev"/"staging", write and
# destructive calls auto-approve instead of blocking on a prompt. Defaults
# to "prod" (always ask) so a missing/unset AGENT_MODE fails toward safety,
# not convenience — you have to opt into the looser mode explicitly.
AGENT_MODE = os.environ.get("AGENT_MODE", "prod").strip().lower()
_DEV_MODES = {"dev", "development", "staging"}

# Tool names are MCP-qualified: mcp__<server_name>__<tool_name>.
RISK_TIERS: dict[str, RiskTier] = {
    # Notion (TRD §11.1)
    "mcp__notion__notion_read_page": "read",
    "mcp__notion__notion_create_page": "write",
    # GitHub (TRD §11) — official hosted remote MCP server, curated subset of
    # its documented tools. Anything not listed here safely defaults to "ask".
    "mcp__github__get_repository": "read",
    "mcp__github__get_file_contents": "read",
    "mcp__github__list_commits": "read",
    "mcp__github__list_issues": "read",
    "mcp__github__get_issue": "read",
    "mcp__github__list_pull_requests": "read",
    "mcp__github__get_pull_request": "read",
    "mcp__github__search_code": "read",
    "mcp__github__search_repositories": "read",
    "mcp__github__create_issue": "write",
    "mcp__github__update_issue": "write",
    "mcp__github__add_issue_comment": "write",
    "mcp__github__create_pull_request": "write",
    "mcp__github__merge_pull_request": "write",
    "mcp__github__create_or_update_file": "write",
    "mcp__github__push_files": "write",
    "mcp__github__delete_file": "destructive",
    # Gmail (TRD §11)
    "mcp__gmail__gmail_search": "read",
    "mcp__gmail__gmail_send": "write",
    # Google Drive (TRD §11) — read-only scope, no write tool exists
    "mcp__drive__drive_search": "read",
    # Google Calendar (TRD §11)
    "mcp__calendar__calendar_list_events": "read",
    "mcp__calendar__calendar_create_event": "write",
    # Spotify (TRD §11) — read-only use case, no write tools exist
    "mcp__spotify__spotify_currently_playing": "read",
    "mcp__spotify__spotify_recently_played": "read",
    "mcp__spotify__spotify_playlists": "read",
    # YouTube (TRD §11, §11.2) — read-only scope, no write tools exist
    "mcp__youtube__youtube_list_subscriptions": "read",
    "mcp__youtube__youtube_list_playlists": "read",
    "mcp__youtube__youtube_liked_videos": "read",
}

_ASK_TIERS = {"write", "destructive"}


def _confirm(tool_name: str, tool_input: dict[str, Any]) -> bool:
    print(f"\n[permission gate] {tool_name} wants to run with input:")
    print(f"  {tool_input}")
    answer = input("  Approve? [y/N] ").strip().lower()
    return answer == "y"


async def can_use_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    context: ToolPermissionContext,
) -> PermissionResultAllow | PermissionResultDeny:
    # Unclassified tools default to "write" (ask), not silent allow — an
    # unclassified tool is a maintenance gap, not a reason to auto-approve.
    tier = RISK_TIERS.get(tool_name, "write")

    if tier not in _ASK_TIERS:
        return PermissionResultAllow()

    if AGENT_MODE in _DEV_MODES:
        return PermissionResultAllow()

    approved = await asyncio.to_thread(_confirm, tool_name, tool_input)
    if approved:
        return PermissionResultAllow()
    return PermissionResultDeny(message=f"Denied by permission gate: {tool_name}")
