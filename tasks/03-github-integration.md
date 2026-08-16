# Phase 3 — GitHub Integration (end to end)

**Build order:** README.md's Suggested Build Order, step 3. **Depends on:** Phase 1 (Foundations),
Phase 2 (Notion, for the permission-gate pattern).

## Goal

Prove the *full* trigger → orchestrator → tool → trace loop (see README.md's
End-to-End Data Flow section) for the
first time, using GitHub's official MCP server plus a real trigger and a
scheduled job — not just a manual `query()` call like Phase 1.

## Scope

- GitHub App or PAT auth; wire up the official GitHub MCP server (see
  README.md's Integration Layer section).
- Risk-tier table entries for GitHub tools: `read` (repo/issues/PRs read) vs
  `ask` (comment/PR-create).
- Text trigger endpoint: `POST /trigger/text` per the spec in README.md's
  Trigger Layer section (Text trigger subsection; HMAC/bearer auth,
  request/response shape).
- One cron job from README.md's Cron-scheduled jobs subsection: daily
  GitHub/repo re-index (embeddings come later in Phase 5 — for this phase,
  the job can just be a stub that fetches changed files and logs them).
- Full sequence from README.md's End-to-End Data Flow section exercised end
  to end: trigger → session load →
  plan → permission gate → tool call → episodic write → Langfuse trace →
  reply.

## Deliverables

- [ ] `POST /trigger/text` live on the always-on host, signature-checked.
- [ ] Ask the agent (via the endpoint) to summarize open PRs in a repo —
      read-only, auto-approved, full trace visible in Langfuse.
- [ ] Ask the agent to comment on an issue — write action, held by the
      permission gate until confirmed via the trigger channel.
- [ ] Cron job stub registered (Vercel Cron or GitHub Actions scheduled
      workflow) firing the trigger endpoint on a daily schedule.

## Out of scope (later phases)

- Real embeddings/re-index into the vector DB — phase 5.
- Memory tiers beyond the episodic write already covered by Phase 2's
  permission-gate work — phase 4 builds these out properly.

## References

README.md's End-to-End Data Flow, Orchestration Layer (session lifecycle), Trigger Layer (Text trigger / Cron-scheduled jobs), and Integration Layer (GitHub row) sections, plus Suggested Build Order (step 3).
