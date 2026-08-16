# Phase 3 — GitHub Integration (end to end)

**Build order:** TRD §17, step 3. **Depends on:** Phase 1 (Foundations),
Phase 2 (Notion, for the permission-gate pattern).

## Goal

Prove the *full* trigger → orchestrator → tool → trace loop (TRD §7) for the
first time, using GitHub's official MCP server plus a real trigger and a
scheduled job — not just a manual `query()` call like Phase 1.

## Scope

- GitHub App or PAT auth; wire up the official GitHub MCP server (TRD §11).
- Risk-tier table entries for GitHub tools: `read` (repo/issues/PRs read) vs
  `ask` (comment/PR-create).
- Text trigger endpoint: `POST /trigger/text` per the spec in TRD §10.1
  (HMAC/bearer auth, request/response shape).
- One cron job from TRD §10.3: daily GitHub/repo re-index (embeddings come
  later in Phase 5 — for this phase, the job can just be a stub that fetches
  changed files and logs them).
- Full sequence from TRD §7 exercised end to end: trigger → session load →
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

TRD §7 (end-to-end data flow), §9 (session lifecycle), §10.1/§10.3
(trigger + cron), §11 (GitHub integration row), §17 step 3.
