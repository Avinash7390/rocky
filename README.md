# rocky

Personal AI agent, built with the [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview),
phase by phase per [`TRD.md`](TRD.md) §17. Each `tasks/NN-*.md` file scopes
one phase; the rest of this repo is the running code.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env  # then fill in whichever phase you're running
```

Requires Python 3.10+ (`claude-agent-sdk` won't install on older versions).

## Run

**Phase 1 — foundations** ([tasks/01-foundations.md](tasks/01-foundations.md)):
single traced query, built-in tools only.

```bash
.venv/bin/python main.py
```

No `ANTHROPIC_API_KEY` needed if you already have the `claude` CLI
authenticated locally — the Agent SDK shells out to it. Set
`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` to trace the run in Langfuse;
without them the script still runs, just untraced.

**Phase 2 — Notion integration** ([tasks/02-notion-integration.md](tasks/02-notion-integration.md)):
Notion read/create-page tools behind the permission gate.

```bash
.venv/bin/python notion_main.py
```

Needs `NOTION_TOKEN` and `NOTION_ROOT_PAGE_ID` set in `.env` — see the task
doc for how to create the internal integration and share a page with it. The
create-page call is a write action: the permission gate will print the tool
call and block on a `y/N` terminal prompt before it runs.

## Layout

```
rocky/
├── TRD.md                          # technical requirements doc
├── tasks/                          # one scoped planning doc per build phase
├── main.py                         # Phase 1: hello-world query
├── notion_main.py                  # Phase 2: Notion tools + permission gate
├── .claude/
│   ├── skills/                      # empty until Phase 8
│   ├── hooks/
│   │   └── permission_gate.py       # risk-tier table + canUseTool (Phase 2)
│   └── subagents/                   # researcher.py lands in Phase 8
├── tools/
│   ├── notion_client.py             # rate-limited Notion REST client
│   └── notion_tool.py               # SDK tool wrappers + MCP server
├── mcp_servers.json                 # still empty — Phase 2 wires tools in-process, not via this file
└── memories/                        # Claude memory-tool working directory — Phase 4
```
