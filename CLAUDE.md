# workflow-memory (for Claude Code working in this repo)

- This repo is the memory itself. `events/` is append-only: never edit or delete an event file; record a change as a new event (`bin/mem add ... --supersedes ID`, `bin/mem forget ID`).
- `views/` is generated. Never edit it by hand; run `bin/mem build` (CI checks it with `build --check`).
- Standard library only. Run the tests before any change: `python3 -m unittest discover -s tests -t .`
- Never force-push. Never put secrets or contact data in an event; the validator quarantines them. There is no automatic health-vocabulary filter, by Giovanni's decision.
- Design, invariants and known limits: `docs/DESIGN.md`.
