"""Phase 3 entrypoint: GitHub MCP + permission gate.

Uses GitHub's official hosted remote MCP server
(https://api.githubcopilot.com/mcp/) rather than the local Docker/npx
variant, so there's no local runtime dependency beyond a token. See
README.md's Suggested Build Order (step 3) and Integration Layer sections.
"""

import asyncio
import os

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

from hooks.permission_gate import can_use_tool

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


def _require_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit(
            "Set GITHUB_TOKEN in .env before running this — a GitHub App "
            "token or classic/fine-grained PAT with repo/issues/PR scopes. "
            "See tasks/03-github-integration.md."
        )
    return token


async def run(prompt: str, token: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful personal AI agent with access to GitHub.",
        mcp_servers={
            "github": {
                "type": "http",
                "url": GITHUB_MCP_URL,
                "headers": {"Authorization": f"Bearer {token}"},
            }
        },
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
    token = _require_token()
    repo = os.environ.get("GITHUB_TEST_REPO", "octocat/Hello-World")
    prompt = (
        f"List the 5 most recently updated open pull requests in {repo}, "
        "with a one-line summary of each."
    )
    try:
        reply = await run(prompt, token)
    except Exception as exc:
        raise SystemExit(f"GitHub integration run failed: {exc}") from exc
    print(reply)


if __name__ == "__main__":
    asyncio.run(main())
