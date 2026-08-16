# Phase 7 — Voice Trigger

**Build order:** TRD §17, step 7. **Depends on:** Phase 6 (Calendar OAuth
scopes already set up), Phase 4 (`trigger_dedupe` table for idempotency).

## Goal

Add the voice trigger (STT hop) and the Calendar push webhook as a bonus
event-driven trigger, and add idempotency handling here — this is where
duplicate triggers become a real risk for the first time.

## Scope

- **Voice trigger** (TRD §10.2): Phone Shortcut / wake-word app → Whisper
  API → transcribed text → existing `POST /trigger/text` endpoint, tagged
  `source: "voice"`. No new endpoint — this reuses §10.1 unchanged from the
  transcription step onward.
- **Calendar push webhook** (TRD §10.4): register via Calendar API
  `watch()`; handler receives a near-empty notification, makes a follow-up
  `events.get` call before deciding whether to act. Purely additive to the
  existing cron scheduler (§10.3) — never the primary scheduler (per
  feasibility matrix §2 item 9c).
- **Idempotency** (TRD §12.1, §16): every trigger entry point (text, voice,
  calendar webhook) checks `trigger_dedupe` before creating a new session or
  re-running an action; retries increment `retry_count` instead of
  double-executing.
- **Watch renewal cron:** the job already spec'd in TRD §10.3 (~every 25
  days, since Calendar channels expire at 30) — implement it here since this
  is where the watch channel is first created.

## Deliverables

- [ ] Voice memo → transcribed → agent responds, round-trip working via a
      phone Shortcut (or equivalent).
- [ ] Calendar event create/update fires the webhook, handler fetches
      details, decides whether to act.
- [ ] Duplicate trigger (same dedupe key fired twice) verified to execute
      only once.
- [ ] Watch-renewal cron job registered and tested against Calendar's
      documented 30-day expiry.

## Out of scope (later phases)

- None — this is the last integration/trigger phase before Phase 8's
  workflow refactor.

## References

TRD §10.2 (voice trigger), §10.3 (cron jobs incl. watch renewal), §10.4
(Calendar push webhook), §12.1 (`trigger_dedupe`), §16 (idempotency
pattern), §17 step 7.
