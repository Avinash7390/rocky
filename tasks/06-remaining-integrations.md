# Phase 6 — Remaining Integrations

**Build order:** TRD §17, step 6. **Depends on:** Phase 4 (Memory/permission
gate patterns established), Phase 5 (KB pipeline, if Gmail/Drive content
should be searchable — otherwise these are live reads only per §1).

## Goal

Add Gmail, Drive, Calendar, Spotify, then YouTube (partial) last — in that
order, since YouTube is the lowest-value/highest-friction of what's left.
Add dev/staging mode and cost guardrails **before** Gmail specifically,
given write-access risk.

## Scope

- **Dev/staging mode + cost guardrails first** (TRD §15 flowchart, §16):
  a mode flag that routes writes through auto-approve in dev but always asks
  in prod, plus a daily spend cap wrapping `query()` calls.
- **Gmail:** Google Workspace MCP, OAuth 2.0 Desktop app client,
  `gmail.readonly` default, `gmail.send` only if a skill needs it. Publish
  the OAuth consent screen to avoid the 7-day test-mode token expiry.
- **Drive:** same MCP/OAuth, `drive.readonly` default.
- **Calendar:** same MCP/OAuth, `calendar.readonly` + `calendar.events`
  (needed for the watch channel used by Phase 7's push trigger).
- **Spotify:** community Spotify MCP, OAuth 2.0 Authorization Code,
  `user-read-currently-playing` / `user-read-recently-played` /
  `playlist-read-private` — read-only use case, no permission-gate write
  path needed.
- **YouTube (partial, last):** separate OAuth scope, `youtube.readonly` —
  subscriptions, playlists, liked videos only. No watch history — this is a
  platform limitation, not a build gap (TRD §11.2).
- Risk-tier table entries added for every new tool as it's built.

## Deliverables

- [ ] Dev/staging mode flag live; permission-gate flowchart (§15) branches
      on it correctly in a manual test.
- [ ] Daily spend cap enforced (log + hard stop) on `query()` calls.
- [ ] Gmail, Drive, Calendar, Spotify, YouTube each reachable via their MCP
      tools with correct scopes; write actions (Gmail send, Calendar event
      create) gated per TRD §11's table.

## Out of scope (later phases)

- Calendar push-notification webhook itself — phase 7 (uses the
  `calendar.events` scope set up here, but the `watch()` registration and
  handler are phase 7 work).

## References

TRD §11 (integration table), §15 (dev/staging mode, permission flowchart),
§16 (cost & rate-limit guardrails), §17 step 6.
