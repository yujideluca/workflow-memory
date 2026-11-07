# ADR-0005: Trim the startup brief and split memory by tool

- **Status:** accepted
- **Date:** 2026-10-26
- **Type (ISO/IEC/IEEE 14764):** perfective
- **Decided by:** Giovanni (owner) / proposed by Claude Code

## Context

Every Claude Code and Codex session prints the memory brief at start, and again after `/clear` and after compaction
(the model's context is rewritten as a shorter summary). A token audit of 63 sessions found the brief at 8-12 KB per print.
Two causes: the prompt harvester had turned generated Codex suggestion prompts into 17 `auto.*` preferences, and rules that
only concern Codex (status line, scrolling) were global, so Claude Code loaded them too. Preferences are pinned (never dropped
by the budget), so a smaller budget alone cannot shrink the brief.

## Decision

- The harvester ignores prompts longer than 1500 characters and sentences that start like a list item or heading
  (`tests/test_system.py::test_prompt_hook_ignores_generated_prompts_and_list_items`).
- Codex hooks run `mem --instance codex`; rules that only concern Codex use scope `instance:codex`.
- After `/clear` or compaction (`source` in the hook payload) each rule is cut to its first 110 characters; the full text
  stays one `mem search` away (`test_session_start_after_clear_or_compact_prints_a_shorter_brief`).

## Alternatives considered

- **Lower the budget** — pinned preferences ignore it.
- **Print nothing after `/clear`** — the session would lose the standing rules.

## Consequences

The brief is about 25% smaller at startup and 45% smaller after `/clear`. A truncated rule can lose a qualifier, so
a rule that matters is written to fit in its first sentence. Codex-only preferences must be recorded with `--scope instance:codex`.
