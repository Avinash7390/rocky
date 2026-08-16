# Phase 1 — Foundations

**Build order:** README.md's Suggested Build Order, step 1. **Depends on:** nothing (first phase).

## Goal

Stand up the orchestrator process itself — an Agent SDK "hello world" in Python —
with observability wired in from the very first call, before any external
integration exists.

## Scope

- Python project scaffold matching the directory layout in README.md's
  Orchestration Layer section
  (`agent/main.py`, `.claude/skills/`, `hooks/`, `.claude/subagents/`,
  `tools/`, `mcp_servers.json`, `memories/`).
- Minimal `main.py` that starts a single long-running process and invokes the
  Claude Agent SDK (`claude-agent-sdk`) with a trivial built-in-tools-only
  query, no custom tools yet.
- Langfuse Cloud Hobby account + native Anthropic SDK instrumentation wired in
  so every call is traced from day one (see README.md's Observability
  (Langfuse) section).
- No trigger webhook server, no MCP servers, no memory tiers yet — this phase
  proves the SDK loop runs and is observable, nothing else.

## Deliverables

- [ ] Project scaffold committed, `python -m agent.main` (or equivalent) runs
      a single query end-to-end.
- [ ] Trace for that query visible in Langfuse, tagged with tool/latency/token
      spans as described in README.md's Observability (Langfuse) section.
- [ ] `requirements.txt` / `pyproject.toml` pinning `claude-agent-sdk` and the
      Langfuse SDK.

## Out of scope (later phases)

- Trigger layer (README.md's Trigger Layer section) — phase 3.
- Any MCP server / integration (README.md's Integration Layer section) — phases 2, 3, 6.
- Memory tiers (README.md's Memory Layer section) — phase 4.

## References

README.md's Orchestration Layer, Observability (Langfuse), and Suggested Build Order (step 1) sections.
