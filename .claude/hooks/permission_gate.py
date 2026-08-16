"""Static risk-tier permission gate (TRD §9, §15).

Risk-tier classification is a table you maintain per tool, not something the
model decides about itself. Read-only tools auto-approve; write/destructive
tools block on confirmation.

No trigger webhook server exists yet (that lands in Phase 3), so "ask" is a
blocking terminal prompt for now — swap `_confirm` for a round-trip over the
trigger channel once §10's server exists, without changing the risk table or
the `can_use_tool` contract.
"""

import asyncio
from typing import Any, Literal

from claude_agent_sdk import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

RiskTier = Literal["read", "write", "destructive"]

# Tool names are MCP-qualified: mcp__<server_name>__<tool_name>.
RISK_TIERS: dict[str, RiskTier] = {
    "mcp__notion__notion_read_page": "read",
    "mcp__notion__notion_create_page": "write",
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

    approved = await asyncio.to_thread(_confirm, tool_name, tool_input)
    if approved:
        return PermissionResultAllow()
    return PermissionResultDeny(message=f"Denied by permission gate: {tool_name}")
