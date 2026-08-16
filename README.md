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

Each phase has its own entrypoint, for testing one integration in
isolation. Fill in only the `.env` vars the phase you're running needs —
every entrypoint guards on its own required config and fails with a clear
message (not a stack trace) if something's missing.

| Phase | Entrypoint | Task doc | Needs in `.env` |
|---|---|---|---|
| 1 — Foundations | `main.py` | [tasks/01-foundations.md](tasks/01-foundations.md) | nothing required (falls back to the local `claude` CLI login) |
| 2 — Notion | `notion_main.py` | [tasks/02-notion-integration.md](tasks/02-notion-integration.md) | `NOTION_TOKEN`, `NOTION_ROOT_PAGE_ID` |
| 3 — GitHub | `github_main.py` | [tasks/03-github-integration.md](tasks/03-github-integration.md) | `GITHUB_TOKEN` |
| 6 — Gmail/Drive/Calendar/YouTube | `agent_main.py` | [tasks/06-remaining-integrations.md](tasks/06-remaining-integrations.md) | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| 6 — Spotify | `agent_main.py` | [tasks/06-remaining-integrations.md](tasks/06-remaining-integrations.md) | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` |

```bash
.venv/bin/python main.py           # Phase 1 only
.venv/bin/python notion_main.py    # Phase 2 only
.venv/bin/python github_main.py    # Phase 3 only
.venv/bin/python agent_main.py     # everything configured in .env, together, interactively
```

**`agent_main.py`** is the one meant for testing everything together: it's
an interactive REPL that wires up whichever integrations have their config
present in `.env` and tells you which ones it skipped and why, so you can
test with any subset filled in — you don't need all seven credentials to
try it. Google (Gmail/Drive/Calendar/YouTube) and Spotify each open a
one-time browser consent flow on first use and cache the resulting token
(`.google_token.json` / `.spotify_token.json`, both gitignored).

**Why custom tools instead of GitHub's hosted-MCP pattern for everything:**
GitHub, Notion, and Google (Gmail/Drive/Calendar) all now ship official MCP
servers, so it's fair to ask why only GitHub is wired as a remote MCP server
while the rest are custom `tools/*.py` wrappers around each service's REST
API. Checked as of 2026-08:
- **Notion**: the official *hosted* server (`mcp.notion.com`) is OAuth-only;
  the official *self-hosted* one (`makenotion/notion-mcp-server`) takes the
  same static internal-integration-token this repo already uses, but runs
  via `npx` — an extra Node.js runtime dependency for no functional gain
  over the pure-Python client already here.
- **Gmail/Drive/Calendar**: Google's hosted MCP servers
  (`gmailmcp.googleapis.com` etc.) are all in **Developer Preview**, not GA
  — they require enrolling in Google's [Workspace Developer Preview
  Program](https://developers.google.com/workspace/preview) before they
  work at all. Gmail's is also **draft-only** (`create_draft`, no
  `send_message`), which would drop this repo's `gmail_send` tool entirely.

Re-evaluate this if those servers reach GA, or if the Developer Preview
Program becomes easy to enroll in and Gmail gains send support.

Set `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` to trace any run in
Langfuse; every entrypoint runs untraced (not broken) without them.

Every write-tier tool call (Notion page creation, GitHub issue/PR writes,
Gmail send, Calendar event creation, ...) is gated by
`.claude/hooks/permission_gate.py`: it prints the tool call and blocks on a
`y/N` terminal prompt before running. Read-only calls auto-approve. See that
file's `RISK_TIERS` table for the exact classification, and its module
docstring for why unclassified tools default to "ask" rather than silent
allow. Set `AGENT_MODE=dev` to auto-approve writes too (TRD §15) — useful
for a fast test pass, but it defaults to `prod` (always ask) so you have to
opt into the looser mode explicitly. `agent_main.py` also enforces
`DAILY_SPEND_CAP_USD` (default $5/day) via `tools/cost_guard.py`, checked
before every turn.

## Layout

```
rocky/
├── TRD.md                          # technical requirements doc
├── tasks/                          # one scoped planning doc per build phase
├── main.py                         # Phase 1: hello-world query
├── notion_main.py                  # Phase 2: Notion tools + permission gate
├── github_main.py                  # Phase 3: GitHub MCP + permission gate
├── agent_main.py                   # Phase 6 / unified: every configured integration, interactively
├── .claude/
│   ├── skills/                      # empty until Phase 8
│   ├── hooks/
│   │   └── permission_gate.py       # shared risk-tier table + canUseTool + dev-mode switch, all phases
│   └── subagents/                   # researcher.py lands in Phase 8
├── tools/
│   ├── notion_client.py             # rate-limited Notion REST client
│   ├── notion_tool.py               # Notion SDK tool wrappers + MCP server
│   ├── google_auth.py               # shared Google OAuth2 helper (Gmail/Drive/Calendar/YouTube)
│   ├── gmail_tool.py                # gmail_search (read), gmail_send (write)
│   ├── drive_tool.py                # drive_search (read-only scope)
│   ├── calendar_tool.py             # calendar_list_events (read), calendar_create_event (write)
│   ├── youtube_tool.py              # subscriptions/playlists/liked videos (read-only scope)
│   ├── spotify_client.py            # Spotify OAuth2 (Authorization Code) helper
│   ├── spotify_tool.py              # currently-playing/recently-played/playlists (read-only)
│   └── cost_guard.py                # daily spend cap ledger, used by agent_main.py
├── mcp_servers.json                 # reference only — entrypoints build MCP configs in Python from env vars, not this file
└── memories/                        # Claude memory-tool working directory — Phase 4
```
