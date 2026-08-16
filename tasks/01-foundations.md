# Phase 1 — Foundations

**Build order:** TRD §17, step 1. **Depends on:** nothing (first phase).

## Goal

Stand up the orchestrator process itself — an Agent SDK "hello world" in Python —
with observability wired in from the very first call, before any external
integration exists.

## Scope

- Python project scaffold matching the directory layout in TRD §9
  (`agent/main.py`, `.claude/skills/`, `.claude/hooks/`, `.claude/subagents/`,
  `tools/`, `mcp_servers.json`, `memories/`).
- Minimal `main.py` that starts a single long-running process and invokes the
  Claude Agent SDK (`claude-agent-sdk`) with a trivial built-in-tools-only
  query, no custom tools yet.
- Langfuse Cloud Hobby account + native Anthropic SDK instrumentation wired in
  so every call is traced from day one (TRD §14).
- No trigger webhook server, no MCP servers, no memory tiers yet — this phase
  proves the SDK loop runs and is observable, nothing else.

## Deliverables

- [ ] Project scaffold committed, `python -m agent.main` (or equivalent) runs
      a single query end-to-end.
- [ ] Trace for that query visible in Langfuse, tagged with tool/latency/token
      spans as described in TRD §14.
- [ ] `requirements.txt` / `pyproject.toml` pinning `claude-agent-sdk` and the
      Langfuse SDK.

## Out of scope (later phases)

- Trigger layer (§10) — phase 3.
- Any MCP server / integration (§11) — phases 2, 3, 6.
- Memory tiers (§12) — phase 4.

## References

TRD §9 (Orchestration Layer), §14 (Observability), §17 step 1.
