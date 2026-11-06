# Memory brief

Generated 2026-11-06 from 758 events. Do not edit: record changes as events.

Memory sets defaults; it never authorizes. Precedence: current instruction > repo rules file > project memory > profile
- [language.reply] Giovanni writes in English or Portuguese: answer in the language of the message. Use they/them for Giovanni. (#2a978d)
- [person.profile] Giovanni is a pre-hospital emergency physician in Brazil, preparing the Goethe B2 exam (Nov 2026) and the FSP to work in Germany. (#94659d)
- [policy.third-party-data] Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (#e91444)
Rules are tagged by kind of task. Before a task of one of these kinds, fetch `views/rules/TAG.md` from the repository (same tools as Recording) and follow its full wording:
- deploy (19): installing, releasing, changing configuration, outward-facing or destructive acts
- troubleshooting (8): debugging, testing, fixing findings, proving that it works
- coding (18): starting, designing or changing code; choosing tools
- reporting (8): how to answer, explain and report results or mistakes
- git (13): branches, commits, repos, GitHub
- docs-memory (13): wiki pages, memory entries, closing a task
- device (11): phone, adb, browser, Telegram
- quiz (4): QuizApp and QuizWeb
- radiology (13): radiology report matcher and crawler
- german (2): German exam practice and corrections
- status-quo (1): the Status Quo tray
- codex (4): work done by Codex

## Open items

Open items (shown in every chat until solved, archived or deleted):
- [open item] Status Quo wallpaper colours (SQ-37, 2026-11-06) done and wiki published; status-quo tree still uncommitted (incl. docs/TRACEABILITY.md, which the gate wants committed); ui_e2e.sh not run; Windows/GNOME not run on real systems | check: cd ~/dev/status-quo && git status --short | grep -c . (since 2026-11-06, #6dff46)
- [open item] Translation check (2026-11-06): burn timer disabled and the running burn stopped by Giovanni; only the daily trickle (04:00, 40 calls) stays on. ~2,863 p1 reviews pending. Re-enable weekly burn only on Giovanni's word: systemctl --user enable --now translation-check-burn.timer. fix --yes not run. Wiki pages for it not written. | check: systemctl --user is-enabled translation-check-trickle.timer (since 2026-11-06, #308326)
- [open item] Wiki map merge (2026-11-06): v6 is merged into ~/dev/wiki main as commits be23e36 and 1a2f508 (gate passes locally; NOT pushed, NOT installed). Next with Giovanni's go: push via a CI branch (work.single-branch), wait for the green gate, then tools/install.sh and a first-line check in Chrome. Two foreign uncommitted files stay in the tree: server/lib/wiki/content/stale.ex, server/mix.lock. Open question: zoom raster time +60..75 % (cause not found). Backup: git tag backup/dy8-snapshot-before-v6,… (since 2026-11-06, #62d1eb)
- [open item radiology] Radiology matcher (2026-11-05): T1, S3b done; v1 and v4 scored on test half (v4 below v1 in EN/DE/PT). Next: S3 Giovanni reviews filler result (empty final list) and dangerous misses; S1 v2/v3 after Codex budget (2026-11-06 12:30, C3-C5); rerun labels/sets after the 21k pending cases are translated; memory: heavy jobs one at a time. Nothing committed in radiology-crawler. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep 'S1' (since 2026-11-05, checked 2026-11-06, #3acbe3)
- [open item] Radiology matcher (2026-11-05): age fix (AN-24/25/26), v4 re-tuned (defaults kept), age hint tested and left off (AN-27). Next: Giovanni reviews dangerous-miss sample (draft levels); score corrected v4 once on new cases after L1d (21k pending cases); v2/v3 after Codex budget 2026-11-06 12:30; DE/PT LLM age tags not made. Nothing committed in radiology-crawler (docs/TRACEABILITY.md regenerated). | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep 'S1' (since 2026-11-05, checked 2026-11-06, #da69a2)
- [open item] Radiology matcher (2026-11-06): corrected v4 scored once on new half (EN top-10 .629, DE .503, PT .589; v1 .640/.502/.608). Later-downloaded cases (16,909 pending): rebuild labels with case-labels-20261105b as earlier, score only the extra new cases. v2/v3 after Codex budget 2026-11-06 12:30. Nothing committed in radiology-crawler. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep L1d (since 2026-11-06, #dd3019)
- [open item] Radiology matcher (2026-11-06): L1d labels rebuilt with frozen halves (AN-28, case-labels-20261105b, 3,527 new cases). Next: wait for downloads (16,909 pending, ~330/h), rebuild labels with 20261105b as earlier, score corrected v4 once on the new half; v2/v3 after Codex budget 2026-11-06 12:30. Nothing committed in radiology-crawler. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep L1d (since 2026-11-06, #382138)
- [open item] Radiology matcher (2026-11-05): age filter fixed (AN-24/25/26, age removes only if exclusive; tuning top-10 EN .610 DE .495 PT .580). Next: Giovanni decides on using age as a ranking hint (not tested) and on S3 sample; re-tune v4 with the new filter; score corrected v4 once on new cases after L1d; v2/v3 after Codex budget 2026-11-06 12:30; DE/PT LLM age tags not made. Nothing committed in radiology-crawler (docs/TRACEABILITY.md regenerated). | check: python3 -I ~/dev/radiology-crawler/tools/ana… (since 2026-11-05, #b7442c)
- [open item radiology] Radiology matcher, next steps (2026-11-05): (1) DONE tuned v4 defaults (T1). (2) S3b filler list stage B; (3) S1 score v2-4 on the test half once; (4) memory pressure: run heavy jobs one at a time; (5) wiki: radiology-analysis pages edited and checked but NOT published (another session has uncommitted changes in ~/dev/wiki content/: acer-nitro, laptop-setup); publish when the tree is clean; nothing committed in radiology-crawler. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status… (since 2026-11-05, #26d273)
- [open item] Radiology matcher analysis in progress: read ~/dev/radiology-crawler/docs/ANALYSIS-STATUS.md first, continue the open steps, keep it and the plan site home page current. Codex has no budget until 2026-11-06 12:30 (UTC-3, Giovanni 2026-11-05): do not wait for it; work on the steps Claude can do alone (L1c fix the weak word lists using the Haiku comparison, L1d case translation and labels, F4, T1, S3b), then ask again. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | gr… (since 2026-11-05, checked 2026-11-05, #311460)
- [open item] Rclone uses the replacement Google client secret; backup verified. Still to do by Giovanni: revoke the exposed ORIGINAL secret (created 2026-10-26 09:23). Link: https://console.cloud.google.com/auth/clients?project=850308375942 (older layout: https://console.cloud.google.com/apis/credentials?project=850308375942). Steps: 1) open the link, sign in with the Google account of the Drive backup; 2) click the OAuth client whose ID starts with 850308375942; 3) in 'Client secrets' find the secret creat… (since 2026-11-05, #06a016)
- [open item] Status Quo implementation in progress at ~/dev/status-quo: user accepted layout and clarified independent removable/interchangeable widgets in a generic tray, Rust throughout, KDE first. Scope-driven template pipeline; continue all scopes without milestone approval pauses. | check: test ! -x /home/yuji/.local/bin/status-quo (since 2026-11-01, #39dc95)
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

