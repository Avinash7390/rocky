# Phase 8 — Skills, Subagents, Hooks, Plugins

**Build order:** TRD §17, step 8 (final phase). **Depends on:** Phases 1-7 —
this phase refactors workflows that only exist once prior integrations are
live.

## Goal

Refactor recurring workflows into Skills once it's clear which ones actually
get run repeatedly, rather than guessing up front.

## Scope

- Review actual usage from Phases 2-7 (episodic log in Postgres is the
  source of truth per TRD §12.1) to find the highest-frequency workflows.
- Build out the four skills already stubbed in the directory layout
  (TRD §9): `triage-inbox`, `weekly-github-digest`, `notion-capture`,
  `spotify-mood-playlist` — plus any others the usage data surfaces.
- `permission_gate.py` hook: formalize the `canUseTool` implementation that's
  been ad hoc since Phase 2, backed by the static risk-tier table accumulated
  across Phases 2, 3, and 6.
- `researcher.py` subagent: split out multi-step research/investigation
  tasks (e.g. "keep researching X" sessions from TRD §9's session-lifecycle
  table) from the main orchestrator loop.
- Evaluate whether any workflow is generic enough to package as a plugin for
  reuse outside this project.

## Deliverables

- [ ] At least the four stubbed `SKILL.md` files implemented and loaded from
      `.claude/skills/`.
- [ ] `permission_gate.py` hook replacing any inline risk-tier logic used in
      earlier phases, single source of truth for read/write/ask
      classification.
- [ ] `researcher.py` subagent handling at least one multi-day/forked-session
      task end to end.
- [ ] Eval dataset (TRD §14) extended to cover the new skills, confirming no
      regression versus the pre-refactor tool-call behavior.

## Out of scope

- New external integrations — none planned; this phase is purely internal
  restructuring of existing capability.

## References

TRD §9 (directory layout, session lifecycle), §14 (eval regression check),
§17 step 8.
