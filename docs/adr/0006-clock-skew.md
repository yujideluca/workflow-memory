# ADR-0006: An event can never be later than the moment it is read

- **Status:** accepted
- **Date:** 2026-10-30
- **Type (ISO/IEC/IEEE 14764):** corrective
- **Decided by:** Giovanni (owner) / proposed by Claude Code

## Context

CI run 41120215899 failed. The Claude app wrote `events/2026/10/20261030T201000Z-app-p3x8wd.md` in a commit made at
20:03:15Z: the chat app has no clock and guesses the time, here seven minutes ahead. A test took the newest event as
`sorted(events)[-1]`, so it picked that file instead of the event it had just created. Machine clocks were not the
problem (the laptop is NTP-synchronised, GitHub runners too); the problem was trusting a writer's stamp for order.

## Decision

- Never find "the event I just wrote" by sort order. `mem add` and the other writers print the stored path; code and
  tests use that (`test_event_conflict_is_reported_not_called_pushed`).
- On read, `validate.clamp_to_now` caps every event time at `now` and keeps the claim in `ts_claimed`. A skewed
  writer cannot reorder the log; the result depends only on the file and `now`, so `--now` builds stay reproducible.
- A stamp more than one day ahead is still quarantined as before.

## Alternatives considered

- **Tighten the one-day tolerance** — would quarantine real events from clockless writers: lost data for a cosmetic error.
- **Sync every writer's clock** — impossible for the chat app, which has none.
- **Rewrite the stamp in CI** — breaks the append-only rule (`append-only` job).

## Consequences

- An event stamped ahead counts as written "now" until its claimed time passes; its original stamp is never lost.
- Tests: `ClockSkewTests` in `tests/test_bughunt.py`.
