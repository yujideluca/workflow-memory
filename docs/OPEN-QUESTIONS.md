# Waiting for Giovanni

The project is built and tested. Nothing below was done, because each item changes how every session or chat
starts, or touches the old setup. Each has a recommended answer.

## Switch-over (the step that makes this the live workflow)
1. **Claude Code hooks.** `bin/mem install-hooks` adds SessionStart (pull and print the brief), UserPromptSubmit
   (harvest preferences, prints nothing) and Stop (push) to `~/.claude/settings.json`, with a backup, and
   `--uninstall` reverses it. The old repo's SessionStart hook is still there and prints its own inbox.
   Recommendation: install the new hooks and remove the old session-start inbox hook in the same step.
2. **Instructions files.** `~/.claude/CLAUDE.md` still points at the old repo (bootstrap, rules that cite it) and
   `~/assistant/CLAUDE.md` links into it. Recommendation: replace both with a short file that points here and
   carries the standing rules (they are already imported as events and appear in `views/BRIEF.md`).
3. **claude.ai Settings.** Replace the line that reads `code/CORE.md` with the text in `docs/CLAUDE-AI.md`.
4. **The old setup.** Its systemd timers (daily check, nightly review, sync) and `claude-workflow-backup` remain.
   Recommendation: disable the timers, keep the old repo read-only as an archive, and delete the obsolete
   `feat/event-memory*` branches.

## Choices that depend on you
5. **Protecting `main`.** The GitHub connector can write any path on any branch. A branch rule that lets only
   `events/**` through for the connector needs a plan that supports it on a private repo; do you want it?
6. **The health vocabulary check** rejects words like patient, diagnosis, medication. It is blunt on purpose.
   Keep it, widen it or narrow it?
7. **Re-calibrate around 2026-11-20** with `python3 scripts/calibrate.py` (it needs 30 days and 100 gaps; today
   it has 8 days). Fact and decision half-lives (180 days) cannot be measured yet.
8. **Not tested:** the connector in a browser chat (phone chat and project chat were tested).
