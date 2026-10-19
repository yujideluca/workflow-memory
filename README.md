# workflow-memory

Shared, long-lived memory for every AI instance Giovanni uses (Claude in the app, in projects, on the phone,
Claude Code, the always-on assistant). It replaces the old claude-workflow-backup protocol.

## The idea in four lines
1. **The log is the memory.** Every fact, preference, decision or task is one new file in `events/`.
   Files are never edited or deleted, so writers never conflict.
2. **State is computed.** `mem/core.py` folds the log: the latest ruling per key wins, repeating a rule adds
   evidence, a negation is a change, `forget` and `done` close entries.
3. **Everything else is generated** into `views/` by a GitHub Action: `BRIEF.md` (what chats read),
   `PREFERENCES.md`, `REVIEW.md` (the only list that needs Giovanni).
4. **No machine is essential.** The Action runs on every push and once a day. Claude Code works on a local
   clone and pushes when it can.

## Who writes how
| Writer | Path |
|---|---|
| Claude app, projects, phone | GitHub connector creates one file in `events/` (steps are at the end of `views/BRIEF.md`) |
| Claude Code, assistant | `bin/mem add ...`, plus hooks that harvest preferences from Giovanni's own words |
| Anything else | write a file in the format of `docs/DESIGN.md`; unknown fields are ignored |

## Commands (`bin/mem`, Python 3 standard library only)
`add`, `feedback`, `forget`, `task`, `claim`, `done`, `use`, `brief`, `search`, `check`, `quarantine`,
`promote`, `compact`, `build [--check]`, `sync [--pull] [--push]`, `install-hooks [--uninstall]`.

## Tests
`python3 -m unittest discover -s tests -t .`

Read `docs/DESIGN.md` for the rules and the known limits, `docs/CLAUDE-AI.md` for the text to paste into the
claude.ai Settings, and `docs/OPEN-QUESTIONS.md` for what waits for Giovanni.
