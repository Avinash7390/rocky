# Phase 5 — Knowledge Base / RAG Pipeline

**Build order:** README.md's Suggested Build Order, step 5. **Depends on:** Phase 4 (Memory layer —
vector DB and `kb_documents` table must exist).

## Goal

Build the ingestion pipeline for Notion + repos + stack docs and expose it as
a single retrieval tool, so the agent decides when to look something up
instead of the whole KB being stuffed into context every turn.

## Scope

- Ingestion pipeline per README.md's Knowledge Base and RAG Pipeline
  section: sources → sync trigger → ingestion queue
  (rate-limit aware) → header-aware chunking (~500-800 tokens) → embed →
  upsert (vector DB + `kb_documents` row).
- Notion sync: API webhooks (shipped 2026, signature-verified) as the
  primary trigger; daily poll from README.md's Cron-scheduled jobs
  subsection as the safety net. Every
  webhook event still triggers a follow-up fetch, since payloads are sparse.
- GitHub/repo re-index: replace Phase 3's log-only stub with real
  chunk/embed/upsert, on the existing daily cron.
- `content_hash` check against `kb_documents` so the safety-net poll skips
  re-embedding unchanged content.
- `search_knowledge_base` tool per the contract in README.md's Knowledge
  Base and RAG Pipeline section: input
  `query, source_filter?, top_k?` → ranked `{ text, source, title, url,
  score }` list.

## Deliverables

- [ ] Notion webhook endpoint receiving events and enqueuing follow-up
      fetches.
- [ ] GitHub daily re-index actually embedding + upserting changed files.
- [ ] `search_knowledge_base` tool callable by the orchestrator, returning
      real results from both sources.
- [ ] Manual test: ask the agent something answerable only from a Notion
      page or repo doc; confirm it calls the retrieval tool and cites the
      right source.

## Out of scope (later phases)

- Additional sources (Gmail/Drive/Calendar/Spotify/YouTube content) — not
  planned for KB ingestion; those are live-integration
  reads, not indexed knowledge.

## References

README.md's Notion integration deep dive (webhooks/rate limits), Postgres schema / Vector DB design (kb_documents, vector DB schema), and Knowledge Base and RAG Pipeline (ingestion pipeline + retrieval tool contract) sections, plus Suggested Build Order (step 5).
