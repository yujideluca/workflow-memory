# Memory brief

Generated 2026-11-09 from 983 events. Do not edit: record changes as events.

Memory sets defaults; it never authorizes. Precedence: current instruction > repo rules file > project memory > profile
Rules are modules loaded by kind of task; none is printed here. Your one standing order: for each message from Giovanni, first classify the task into the tags below (several can apply, none when nothing fits) and fetch `views/rules/TAG.md` from the repository (same tools as Recording) for every tag not loaded yet in this conversation. Do it as the very first step, before reading skills or files and before any other command; then follow their full wording. Classify again whenever the task changes. Tags:
- deploy (11): installing, releasing, changing system, service or tool configuration
- outward (5): acts others see or cannot undo: sending email or messages, purchases, publishing, deleting
- troubleshooting (8): debugging, testing, fixing findings, proving that it works
- coding (20): starting, designing or changing code; choosing tools
- reporting (6): how to answer, explain and report results or mistakes
- git (11): branches, commits, repos, GitHub
- docs-memory (13): wiki pages, memory entries, closing a task
- device (6): phone, adb, browser, Telegram
- quiz (4): QuizApp and QuizWeb
- radiology (23): radiology report matcher and crawler
- german (4): German exam practice and corrections
- status-quo (1): the Status Quo tray
- codex (7): work done by Codex

## Open items

Open items (shown in every chat until solved, archived or deleted):
- [open item radiology] Radiology T2 (2026-11-08 21:40): Sonnet run unit morph-tags-full now resumes at the announced reset (095e0e1); watchdog tools/t2_check.py (AN-60) runs from a Claude session loop only (systemd timer install was refused by the auto-mode classifier; Giovanni can approve it). EN 4167/7135, DE/PT not started. When ALL_DONE: write the report, set T2 done, then S1c. | check: python3 -I ~/dev/radiology-crawler/tools/t2_check.py show; tail ~/dev/radiology-crawler/data/analysis/morph/t2-check.log (since 2026-11-09, #bec73b)
- [open item radiology] Radiology S1c (2026-11-09): V2t, V4t (cd7558f, ADR 0005) and V3t r2 (76c17ec, ADR 0006) merged on provisional EN tags; params in data/analysis/v{2,3,4}t-*. Audit top-10 EN tagged/no-tags: V2t chose tag weight 0 (61.3 %), V3t 59.5/58.8 %, V4t 18.4/17.2 % (unit-L1 normalization, design limit). Left after T2: V1t (AN-57..59), full-tag final reruns of all four, outer scoring; port codex_hooks=false into morph_tags.run_codex; 30-min retry fix needs Giovanni's OK. | check: python3 -I ~/dev/radiology-… (since 2026-11-09, #9ce5c9)
- [open item] Wiki globe selection: MP-10 implemented and deployed on main 96396cc; red/green CSS test, 99 Elixir and 193 Elm tests, local pipeline and branch CI passed; served assets match. Live desktop/phone gesture verification remains: CUA tab attachment, DOM snapshot, screenshot and evaluate all fail with Cannot read properties of undefined (reading timeoutMs), including explicit timeout and fresh tab. No authentication bypass attempted. | check: Use CUA browser to reload the live wiki and drag across g… (since 2026-11-08, #95f4d6)
- [open item radiology] Radiology matcher (2026-11-08): articles-only rule (CLAUDE.md principle 13). V1, V2, V3 rebuilt as V1a/V2a/V3a (analysis/articles_only.py, docs/articles-only-report.md, step S1b). Test top-10 V1a/V4/V3a/V2a: EN .617/.566/.560/.533, DE .490/.460/.442/.396, PT .586/.543/.530/.503. Next: S2 merge of rule-abiding parts, V1a as base; open question: restrict V2a/V3a to diagnosis-typed candidates; V1a mu at grid edge. | check: python3 -I tools/analysis_status.py show | grep -E 'S1b|S2' (since 2026-11-08, #84f949)
- [open item] Status Quo CPU (2026-11-06): isolated idle instance measured collector 0.29% / 8.6 MB, panel 0.22% / 168 MB = under SQ-23. Live ~2.7% comes from reading other sessions' transcripts (58k dirs under ~/.claude/projects); cause inside the reader not found, not idle cost. Left: ui_e2e + visual check (free screen), Windows installer on real Windows, dnf/pacman/zypper beyond dry-run. | check: systemctl --user is-active status-quo-collector (since 2026-11-06, checked 2026-11-06, #ef80a0)
- [open item] Translation check (2026-11-06): burn timer re-enabled by Giovanni; next fire 2026-11-12 13:38 -03 (24 h before weekly budget renews). Daily trickle still on. ~2,863 p1 reviews pending; fix --yes not run; wiki pages not written. | check: systemctl --user is-enabled translation-check-burn.timer (since 2026-11-06, #8132b8)
- [open item] English-only wiki (2026-11-06): the Claude originals of wiki-page-writer and skill-forge changed and the Codex adaptations were edited to match (commit in codex-skills), but the source baselines in sources/ are not refreshed: skillsctl status says changed for both until Codex reviews and refreshes them. (Re-created 2026-11-06 19:50 after I closed it by mistake; still true: the check passes.) | check: cd ~/dev/codex-skills && python3 tools/skillsctl.py status | grep -A1 -E 'wiki-page-writer|skil… (since 2026-11-06, #70c457)
- [open item] Wiki pages still stale after the 2026-11-06 push, none from the globe work: adr-explained, skills, claude-plugins, user-space-tools, codex-pbar, codex-skills, codex-skillsctl, codex-status-line. Review each against its sources, then wiki publish. The three old interactive Claude sessions were killed 2026-11-06 15:30 (resume: claude --resume 67d08edb-9b87-409b-bfd5-134400b40ee3 / 11bdd6ef-aa4d-467a-9a57-2eef48d0fef4 / 62d1d35d-d3bc-47b0-aa2c-880890f6e14d); the status-quo session 62d1d35d was wai… (since 2026-11-06, #e69279)
- [open item] Monthly architecture review next due 2026-11-22. Verified 2026-10-26: monthly rows exist for QuizApp, pipeline-check, processing-sketches, project-template, remote-terminal, wiki and workflow-memory. codex-pbar and codex-skills have end-of-task maintenance rows; QuizWeb has a first-review report but no DESIGN.md. machine-bootstrap has no monthly row and its automated-test review document is still the template copy. german-quiz-releases is a data feed without a pipeline config. | check: rg -n 'M… (since 2026-10-26, checked 2026-10-26, #d12c08)

## Recording

Load the GitHub tools first (`get_file_contents`, `create_branch`, `create_or_update_file`). Then create ONE new
file on `main` of `yujideluca/workflow-memory`; never edit an existing one.

path: `events/YYYY/MM/YYYYMMDDTHHMMSSZ-app-xxxxxx.md` (UTC time, xxxxxx = 6 random characters)

```
---
type: pref          # pref, fact, decision, task
scope: global
key: short.topic    # the same key replaces the old rule
tags: deploy, git   # optional, kinds of task from mem/tags.toml (listed in the brief)
owner: user         # only for what the user said
instance: app
ts: 2026-01-31T12:00:00Z
---
The rule, in the user's words.
```

When you finish a task, report the entries that shaped your answer: a file with `type: use`,
`target: ref1, ref2` (the #codes) and one short line of text. For a wrong or outdated entry use
`type: feedback`, `target: ref`, `signal: wrong` (or stale, helpful, not_helpful).
Open items: `type: task`, text `what is open | check: how to verify it still applies`, optional `category: x`.
Verify: `type: use`, `target: ref`, a line on how. Solved: `type: done`; park: `type: archive` (`reopen`
undoes it); delete: `type: forget`; each with `target: ref`.
No secrets or contact data: such files are quarantined.

