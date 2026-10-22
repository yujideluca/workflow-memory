# workflow-memory (for Claude Code working in this repo)

Principles and what enforces each (decisions and alternatives: `docs/adr/`):
1. Events are append-only: CI job `append-only` in `.github/workflows/mem.yml` (ADR-0002).
2. Views are derived: `test_check_fails_when_a_view_was_edited_by_hand`, rebuilt by CI on every push.
3. Delivery order never matters: `test_order_independent_and_idempotent`, `test_forget_is_order_independent`.
4. Giovanni's own words outrank the harvester: `test_harvester_never_rewrites_user_owned_entry`.
5. No secrets or contact data: `test_privacy_boundary`; invalid events are quarantined.
6. This repo is the only interface between Claude instances; no new protocol (ADR-0003).
A structural change gets an ADR (`docs/adr/0000-template.md`) in the same commit.

- This repo is the memory itself. `events/` is append-only: never edit or delete an event file; record a change as a new event (`bin/mem add ... --supersedes ID`, `bin/mem forget ID`).
- `views/` is generated. Never edit it by hand; run `bin/mem build` (CI checks it with `build --check`).
- Standard library only. Run the tests before any change: `python3 -m unittest discover -s tests -t .`
- Never force-push. Never put secrets or contact data in an event; the validator quarantines them. There is no automatic health-vocabulary filter, by Giovanni's decision.
- Design, invariants and known limits: `docs/DESIGN.md`.
