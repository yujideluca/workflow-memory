# Memory brief

Generated 2026-10-26 from 334 events. Do not edit: record changes as events.

Memory sets defaults; it never authorizes. Precedence: current instruction > repo rules file > project memory > profile

- [language.reply] Giovanni writes in English or Portuguese: answer in the language of the message. Use they/them for Giovanni. (#0c1417)
- [work.verified-by] Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (#5cba3e)
- [work.setup-end-to-end] Do installs and setup end to end. Hand over only the steps that need sudo or Giovanni's own approval. (#803489)
- [git.no-force-push] Never force-push. (#b07b2e)
- [safety.ask-before-outward] Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (#ef8e45)
- [work.test-yourself] After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (#6c6d10)
- [style.plain-language] Explain in plain language: define each technical term the first time it appears and say what it means in human terms before the details. Never assume Giovanni knows something only mentioned in passing. (#817781)
- [work.encode-decisions] A decision stated once must be encoded where it takes effect, not only logged; Giovanni should never have to repeat it. (#e5d741)
- [person.profile] Giovanni is a pre-hospital emergency physician in Brazil, preparing the Goethe B2 exam (Nov 2026) and the FSP to work in Germany. (#9f3a0e)
- [policy.third-party-data] Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (#baab57)
- [work.build-then-ask] After a project and plan are approved, build it end to end without progress pauses; ask the open questions at the end. (#c1f1f8)
- [work.ask-with-context] When asking Giovanni about a development decision that is new (not a topic already debated), give clear context first: what is being decided, why, options, and your recommendation. If it involves many steps never discussed, include a flowchart. A badly framed question cannot be answered well. (#abdad0)
- [telegram] To send via Telegram use the tg-send bot (tg-send -f FILE caption), never the phone app; read ~/.local/bin/tg-send, it has no --help (any argument is sent as a message). Messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages: always tell Giovanni to check that chat. (#c09dc8)
- [pendencies.verify-before-reminding] Pendencies (unfinished goals, known problems) are open items: record them with mem task --check HOW. They show in every chat until solved, archived or deleted; project-specific only when Giovanni says so. Before reminding Giovanni of one, run its check; if it no longer applies, close it; if unchecked, say so. Never call an item open from memory alone. (#ad71c7)
- [work.no-qwen] Local Qwen is not part of the workflow: do not use or propose it for coding or delegation. Its files were deleted 2026-10-21. (#303850)
- [work.maintenance] Software projects follow the golden path: ADRs for structural decisions, requirements before code, one quality gate run by CI on every push, debt as GitHub Issues labelled debt/P1-P3, about one session in five on debt or prevention, monthly architecture review. New projects start from ~/dev/project-template. (#d975f2)
- [release.promote] A version may be promoted to the user channel once it survives the automated tests updated for what it changes (gate with mutation + tests changed with the code); then promoting is Giovanni's decision. No minimum time in beta; do not argue for one. (#d71784)
- [work.ask-language] Before any project that involves coding, ask Giovanni which programming language(s) to use (front end, back end, tools) before designing or writing code; never pick the language yourself. (#f1e117)
- [work.fix-findings] Findings from a maintenance review that Giovanni answers 'deve' are fixed in the same session, with the test first; hypotheses wait for his answer. (#566908)
- [work.shared-tools] A tool used by more than one project lives once, in its own repository, and is consumed by pinned version, never copied (example: pipeline-check, github.com/yujideluca/pipeline-check). (#63efec)
- [work.github-standard] Every project has a versioned repository on GitHub (private unless it must be public); a folder in ~/dev without git and a remote is a gap to fix. (#9b6938)
- [work.no-retired-refs] A retired protocol or tool is not named in anything that works today (skills, CLAUDE.md, memory, READMEs, scripts); only history (ADRs, decision logs, the wiki page of the retired thing) may mention it. (#164a12)
- [wiki.plain-language] Wiki pages must help someone with no previous knowledge of the system or its technical language: define a term where it first appears, link complex terms to a definition, spell out an acronym or abbreviation at its first use on each page, and let a skill page carry the skill's own definition. (#f4e33f)
- [work.act-on-ok] When Giovanni says 'solve it', do the work (create issues, write log rows, fix) instead of listing proposals; check memory and past messages for decisions already made (e.g. pipeline-check licence = MIT) before asking. (#c1c894)
- [repos.public] Repos that need branch protection are public, because GitHub Free has no protection on private repos. german-quiz, remote-terminal, wiki, workflow-memory and processing-sketches were made public on 2026-10-25 after a clean secret scan. (#b5a8cf)
- [repos.workflow-memory-unprotected] workflow-memory is intentionally without branch protection: its mem job pushes derived files to main with the built-in token and a required check rejects that push (simulation 2026-10-25). Local pre-push check stands in; pipeline-check.toml has protection_exception, so protecao-de-branch is an accepted aviso there, not a failure. (#398bdc)
- [release.pool-promote] Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25). (#de2122)
- [work.test-ui-on-phone] Test any phone-facing web UI on Giovanni's real phone (Motorola, adb), not only in a narrowed desktop browser: serve the build with adb reverse and read frame times with Chrome DevTools over adb forward; the public wiki address needs Giovanni's own Google sign-in, so do not sign in for them. (#f7008d)
- [work.phone-stay-awake] Giovanni's phone must stay awake for other projects: never turn off or change its stay-awake setting (svc power stayon, stay_on_while_plugged_in, screen timeout). If a test needs the screen on, only send a wake key; read a device setting before changing it and put back exactly what was there. (#03ca1c)
- [wiki.complete-skill-content] In the wiki project, every skill page must contain the complete source SKILL.md description and instructions, not a shortened summary. The page-generation trigger and writer must locate and read the complete source before writing, and keep the full content on the page and its language versions. (#12386c)
- [work.routine-autonomy] Proceed without repeated confirmation for routine, reversible edits, commands, checks and website access within the requested task. Ask only when an action is dangerous or a required technical permission cannot be avoided; batch necessary access requests instead of asking for each command or site. (#b9bd12)
- [work.acceptance-evidence] Correction after repeated false completion claims: define success as the user's observable outcome before acting. Configuration, installation and passing component tests do not prove that outcome. Verify the actual execution path and visible behavior; if inaccessible, state precisely what remains unverified and keep the task incomplete. Investigate available evidence before asking the user; perform authorized routine work yourself. Lead reports with the result, evidence and remaining limitation in plain language. (#e80181)
- [codex.skills-ownership] Maintain Codex-owned versions of incompatible Claude skills in the separate codex-skills GitHub project, using Claude skills as the basis without editing their originals; management tooling is Python. (#ce282d)
- [work.troubleshoot-documentation] Investigate documentation failures before declaring them blocked. Prefer an isolated committed worktree and narrow reconciliation that preserves other sessions’ edits; do not treat a dirty wiki tree alone as the end of troubleshooting. (#90a529)
- [codex.status-fields] Show five-hour and weekly budget percentages remaining, tokens used in the current context and context-window size in the native Codex terminal status line, alongside the separate task-progress footer. Supersedes earlier task-only instructions. (#69f6b4)
- [codex.status-display] Task footer styling (Claude's compact line): green Progress percentage label, normal terminal background, middle-dot separators, completed/total tasks and estimated remaining time, no drawn or animated bar. This restricts appearance only; the native Codex status line still shows five-hour and weekly budget percentages remaining, tokens used in the current context and context-window size (key codex.status-fields). (#87a4b1)
- [work.single-branch] Keep every repository on one branch, main. Use a branch only briefly to get CI before promoting to main, then delete it (local and remote) and remove its worktree. Never leave parallel feature, session or draft branches; fold their work into main. (#cefeb3)
- [style.explain-new-information] When introducing new information or a pendency, name the specific component and change; avoid vague references such as migration without saying what moves and why. (#a7bb57)
- [work.web-no-own-version] QuizWeb may ship a standalone maintenance release when it contains relevant changes, without waiting for another Android release. Ports of unreleased Android features still follow app promotion. Supersedes the blanket no-standalone-release rule. (#a94fd9)
- (10 more entries did not fit; they are in the log and searchable)

## Open items

Open items (shown in every chat until solved, archived or deleted):
- [open item] machine-bootstrap has no commit and no GitHub repository yet: commit locally, then Giovanni decides public or private (state/ holds package lists and settings, no secrets) and pushes; the monthly review needs it (work.github-standard) | check: git -C ~/dev/machine-bootstrap ls-remote origin 2>/dev/null | grep -q . (since 2026-10-25, checked 2026-10-26, #a0dde6)
- [open item] rclone gdrive uses the shared client_id that stops working during 2026 (it is already 2026-10): create an own client_id (rclone.org/drive/#making-your-own-client-id) or the Drive copy of the secrets will fail | check: ! rclone lsd gdrive: 2>&1 | grep -q 'shared Google Drive client_id' (since 2026-10-25, checked 2026-10-26, #0ee03e)
- [open item] Codex status: native terminal footer has context capacity and session counters; desktop service masked and launcher blocked. Custom animated progress bar is still not integrated below input. Current desktop-chat host does not use tui.status_line; investigate supported host extension before claiming visible integration. Five-hour/weekly schema has percentages, no token allowance. | check: test -L /home/yuji/.config/systemd/user/codex-pbar.service && ! git -C /home/yuji/dev/codex-pbar grep -q ter… (since 2026-10-25, checked 2026-10-26, #fda16d)
- [open item] QuizWeb branch first-maintenance-review (web import validation, sharp s search, zero-goal bar) matches app changes already on QuizApp main: ship it with the next app version (rename to web-<versionName> at promote time; QuizApp CI picks that branch); do not merge it to QuizWeb main before the app is promoted (WB-1 / web follows the user version) | check: cd ~/dev/QuizWeb && git ls-remote --heads origin first-maintenance-review | grep -q . (since 2026-10-24, checked 2026-10-26, #7c55a5)
- [open item] Monthly architecture review of all ~/dev projects (next due by 2026-11-22): run the skill revisao-manutencao (it runs tools/pipeline-check.sh in each project, reads build/pipeline-check/report.json, proposes debt issues P1-P3 and a Preventive row; checklist in ~/dev/project-template/docs/MAINTENANCE.md). First review done 2026-10-24 for QuizApp and pipeline-check; other projects adopted pipeline-check on branches awaiting merge | check: ! grep -qE "^\| $(date +%Y-%m)-[0-9]{2} \| Preventive \| \… (since 2026-10-24, checked 2026-10-26, #c091ff)

## Recording

Load the GitHub tools first (`get_file_contents`, `create_branch`, `create_or_update_file`). Then create ONE new
file on `main` of `yujideluca/workflow-memory`; never edit an existing one.

path: `events/YYYY/MM/YYYYMMDDTHHMMSSZ-app-xxxxxx.md` (UTC time, xxxxxx = 6 random characters)

```
---
type: pref          # pref, fact, decision, task
scope: global
key: short.topic    # the same key replaces the old rule
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

