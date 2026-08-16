# Phase 4 — Memory Layer

**Build order:** README.md's Suggested Build Order, step 4. **Depends on:** Phase 3 (GitHub, for a
working trigger/session loop to persist state from).

## Goal

Build out the four memory tiers (see README.md's Memory Layer section) while the tool surface area is
still small — GitHub + Notion only — and add the eval harness now, before
more integrations make regressions harder to spot.

## Scope

- **Session memory:** confirm SDK session resume/fork behavior matches the
  lifecycle table in README.md's Orchestration Layer section (new session,
  resume, fork-at-checkpoint).
- **Working memory:** Claude memory tool wired to the `memories/` directory
  layout in README.md's Memory-tool directory layout subsection
  (`preferences.md`, `active-tasks/<task-id>.md`,
  `decisions-log.md`); verify it's written before context-clearing kicks in.
- **Long-term semantic memory:** stand up the vector DB (Upstash Vector or
  Pinecone free tier) with the schema in README.md's Vector DB design
  subsection (`id`, `embedding`,
  `metadata.source`, `metadata.updated_at`, `metadata.tags`).
- **Structured episodic log:** Postgres (Supabase/Neon free tier) with the
  schema in README.md's Postgres schema subsection — `sessions`,
  `episodic_events`, `kb_documents`,
  `trigger_dedupe`. Wire the idempotency pattern (`dedupe_key` +
  `trigger_dedupe`) into every write-tier action from Phases 2–3.
- **Eval harness:** small hand-curated `(trigger, expected tool calls)`
  dataset in Langfuse, re-run whenever a skill/prompt changes (see
  README.md's Observability (Langfuse) section).

## Deliverables

- [ ] Postgres schema migrated; every write action from GitHub/Notion tools
      logs an episodic event and checks `trigger_dedupe` first.
- [ ] Vector DB provisioned and reachable, empty collection ready for
      Phase 5's ingestion pipeline.
- [ ] Memory-tool directory present and a working-memory write observably
      happens before a context-clearing event.
- [ ] First eval dataset entries in Langfuse, one run executed successfully.

## Out of scope (later phases)

- Populating the vector DB with real content — phase 5 (ingestion pipeline).
- Retention/hygiene cron job — already spec'd in README.md's
  Cron-scheduled jobs subsection but can be
  scheduled once this phase's tables exist; wire the job itself here if time
  allows, otherwise defer.

## References

README.md's Orchestration Layer (session lifecycle), Memory Layer (and its Postgres schema / Vector DB design / Memory-tool directory layout subsections), Observability (Langfuse) (eval dataset), and Production Hardening Patterns (idempotency, PII-awareness) sections, plus Suggested Build Order (step 4).
