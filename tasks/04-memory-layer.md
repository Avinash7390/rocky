# Phase 4 — Memory Layer

**Build order:** TRD §17, step 4. **Depends on:** Phase 3 (GitHub, for a
working trigger/session loop to persist state from).

## Goal

Build out the four memory tiers (TRD §12) while the tool surface area is
still small — GitHub + Notion only — and add the eval harness now, before
more integrations make regressions harder to spot.

## Scope

- **Session memory:** confirm SDK session resume/fork behavior matches the
  lifecycle table in TRD §9 (new session, resume, fork-at-checkpoint).
- **Working memory:** Claude memory tool wired to the `memories/` directory
  layout in TRD §12.3 (`preferences.md`, `active-tasks/<task-id>.md`,
  `decisions-log.md`); verify it's written before context-clearing kicks in.
- **Long-term semantic memory:** stand up the vector DB (Upstash Vector or
  Pinecone free tier) with the schema in TRD §12.2 (`id`, `embedding`,
  `metadata.source`, `metadata.updated_at`, `metadata.tags`).
- **Structured episodic log:** Postgres (Supabase/Neon free tier) with the
  schema in TRD §12.1 — `sessions`, `episodic_events`, `kb_documents`,
  `trigger_dedupe`. Wire the idempotency pattern (`dedupe_key` +
  `trigger_dedupe`) into every write-tier action from Phases 2–3.
- **Eval harness:** small hand-curated `(trigger, expected tool calls)`
  dataset in Langfuse, re-run whenever a skill/prompt changes (TRD §14).

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
- Retention/hygiene cron job — already spec'd in TRD §10.3 but can be
  scheduled once this phase's tables exist; wire the job itself here if time
  allows, otherwise defer.

## References

TRD §9 (session lifecycle), §12, §12.1, §12.2, §12.3 (Memory layer), §14
(eval dataset), §16 (idempotency, PII-awareness), §17 step 4.
