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

Each phase has its own entrypoint. Fill in only the `.env` vars the phase
you're running needs — every entrypoint guards on its own required config
and fails with a clear message (not a stack trace) if something's missing.

| Phase | Entrypoint | Task doc | Needs in `.env` |
|---|---|---|---|
| 1 — Foundations | `main.py` | [tasks/01-foundations.md](tasks/01-foundations.md) | nothing required (falls back to the local `claude` CLI login) |
| 2 — Notion | `notion_main.py` | [tasks/02-notion-integration.md](tasks/02-notion-integration.md) | `NOTION_TOKEN`, `NOTION_ROOT_PAGE_ID` |
| 3 — GitHub | `github_main.py` | [tasks/03-github-integration.md](tasks/03-github-integration.md) | `GITHUB_TOKEN` |

```bash
.venv/bin/python main.py           # Phase 1
.venv/bin/python notion_main.py    # Phase 2
.venv/bin/python github_main.py    # Phase 3
```

Set `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` to trace any run in
Langfuse; every entrypoint runs untraced (not broken) without them.

Every write-tier tool call (Notion page creation, GitHub issue/PR writes,
...) is gated by `.claude/hooks/permission_gate.py`: it prints the tool call
and blocks on a `y/N` terminal prompt before running. Read-only calls
auto-approve. See that file's `RISK_TIERS` table for the exact
classification, and its module docstring for why unclassified tools default
to "ask" rather than silent allow.

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
├── github_main.py                  # Phase 3: GitHub MCP + permission gate
├── .claude/
│   ├── skills/                      # empty until Phase 8
│   ├── hooks/
│   │   └── permission_gate.py       # shared risk-tier table + canUseTool, all phases
│   └── subagents/                   # researcher.py lands in Phase 8
├── tools/
│   ├── notion_client.py             # rate-limited Notion REST client
│   └── notion_tool.py               # SDK tool wrappers + MCP server
├── mcp_servers.json                 # reference only — entrypoints build MCP configs in Python from env vars, not this file
└── memories/                        # Claude memory-tool working directory — Phase 4
```
