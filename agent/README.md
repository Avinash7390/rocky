# agent

Phase 1 (foundations) of the personal AI agent — see [`../tasks/01-foundations.md`](../tasks/01-foundations.md)
and [`../TRD.md`](../TRD.md) §9 for the full design.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Requires Python 3.10+ (`claude-agent-sdk` won't install on older versions).

## Run

```bash
.venv/bin/python main.py
```

No `ANTHROPIC_API_KEY` needed if you already have the `claude` CLI
authenticated locally — the Agent SDK shells out to it. Set
`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` (see `.env.example`) to trace the
run in Langfuse; without them the script still runs, just untraced.

## Layout

```
agent/
├── main.py            # this phase: single traced query, built-in tools only
├── .claude/
│   ├── skills/         # empty until Phase 8
│   ├── hooks/           # permission_gate.py lands in Phase 2
│   └── subagents/       # researcher.py lands in Phase 8
├── tools/              # custom (non-MCP) tools — first one in Phase 2
├── mcp_servers.json    # empty until Phase 2 (Notion) / Phase 3 (GitHub)
└── memories/           # Claude memory-tool working directory — Phase 4
```
