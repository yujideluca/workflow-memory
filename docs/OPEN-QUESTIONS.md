# Status and what waits for Giovanni

## Done on 2026-10-19
- Claude Code hooks installed in `~/.claude/settings.json` (backup: `settings.json.pre-mem-*`); the old inbox
  hook is removed. `bin/mem install-hooks --uninstall` reverses the new ones.
- `~/.claude/CLAUDE.md` and `~/assistant/CLAUDE.md` rewritten (backups next to them, the second one was a symlink
  into the old repo and is now a real file). `mem` is linked into `~/.local/bin`.
- Old timers `claude-daily` and `claude-review` disabled; the skill link `gui-code-protocol` removed; the old
  repo's `feat/event-memory*` branches deleted. The old repo stays on disk as an archive: the other skills are
  symlinks into its `code/skills/` and the status-line progress bar runs from its `tools/`, so do not delete it.
- The launcher `~/.local/bin/claude-assistant` now exports `MEM_INSTANCE=assistant` (backup: `.pre-mem`). It
  takes effect the next time the service restarts; the running assistant session was not restarted.
- claude.ai Settings text pasted by Giovanni (`docs/CLAUDE-AI.md`).
- Health-vocabulary filter: not implemented, by Giovanni's decision.

## Waiting
1. **Re-calibrate around 2026-11-20** with `python3 scripts/calibrate.py`.
2. **Not tested:** the connector in a browser chat.
