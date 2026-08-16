"""Agent SDK hello world (README.md's Suggested Build Order, Phase 1).

One query through the Claude Agent SDK, traced through Langfuse when
credentials are present. No custom tools, no trigger server, no memory
tiers yet — this only proves the orchestration loop runs and is observable.
"""

import asyncio
import os

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)
from langfuse import get_client, observe

LANGFUSE_ENABLED = bool(os.environ.get("LANGFUSE_PUBLIC_KEY")) and bool(
    os.environ.get("LANGFUSE_SECRET_KEY")
)


@observe(name="agent.hello_world", as_type="generation")
async def run_query(prompt: str) -> str:
    """Send a single prompt through the Agent SDK and return the reply text."""
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful personal AI agent.",
    )
    reply_parts: list[str] = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    reply_parts.append(block.text)
        elif isinstance(message, ResultMessage) and LANGFUSE_ENABLED:
            model = next(iter((message.model_usage or {}).keys()), None)
            get_client().update_current_generation(
                model=model,
                usage_details=message.usage,
                metadata={
                    "session_id": message.session_id,
                    "num_turns": message.num_turns,
                    "total_cost_usd": message.total_cost_usd,
                },
            )

    return "".join(reply_parts)


async def main() -> None:
    prompt = "In one sentence, confirm you're running via the Claude Agent SDK."
    try:
        reply = await run_query(prompt)
    except Exception as exc:
        raise SystemExit(
            f"Agent SDK query failed: {exc}\n\n"
            "If this says 'Not logged in', the `claude` CLI the SDK spawns "
            "isn't authenticated yet — run `claude /login` in a terminal "
            "(or set ANTHROPIC_API_KEY in .env) and try again."
        ) from exc

    print(reply)

    if LANGFUSE_ENABLED:
        get_client().flush()
    else:
        print(
            "\n[langfuse] LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY not set — "
            "this run was not traced. See tasks/01-foundations.md.",
        )


if __name__ == "__main__":
    asyncio.run(main())
