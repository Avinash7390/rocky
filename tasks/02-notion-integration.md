# Phase 2 — Notion Integration

**Build order:** TRD §17, step 2. **Depends on:** Phase 1 (Foundations).

## Goal

Prove the auth-token → integration-layer → knowledge-base pattern end to end
using the source with the least setup friction, and exercise the permission
gate on a real write action (page creation) before anything higher-stakes.

## Scope

- Notion internal integration token (no OAuth flow) — TRD §11.1.
- One top-level "Agent Access" page shared with the integration; everything
  the agent should see organized as children of it.
- Build against the current Notion API version (2025-09-03+): fetch
  `data_source_id` via lookup, don't assume `database_id` alone is enough.
- A small request queue with exponential backoff for the ~3 req/s rate limit
  (page → block-children → nested-blocks fan-out).
- Notion tool exposed to the orchestrator: read a page, create a page.
- Permission gate (`canUseTool`, TRD §9) wired for the first time — classify
  `notion.read_page` as read (auto-approve), `notion.create_page` as write
  (ask for confirmation via the trigger channel).

## Deliverables

- [ ] Notion tool (custom or lightweight MCP) with read + create-page calls.
- [ ] Permission gate blocks on `notion.create_page` until you confirm, and
      the confirmation round-trip is traced in Langfuse.
- [ ] Manual end-to-end test: ask the agent to create a page under "Agent
      Access", confirm the prompt, verify the page appears in Notion.

## Out of scope (later phases)

- Webhook-driven sync into the KB ingestion pipeline — phase 5.
- Any other integration — phase 3 (GitHub), phase 6 (Gmail/Drive/Calendar/
  Spotify/YouTube).

## References

TRD §9 (Permission gate), §11 and §11.1 (Notion deep dive), §17 step 2.
