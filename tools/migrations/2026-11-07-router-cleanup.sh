#!/usr/bin/env bash
# Rule cleanup + retag for ADR-0008. Usage: cleanup.sh MEM_CODE_DIR MEM_ROOT
set -euo pipefail
CODE="$1"; ROOT="$2"
m() { python3 "$CODE/bin/mem" --root "$ROOT" --instance code "$@" >/dev/null; }
add() { # key tags supersedes ; text on stdin ; owner user
  m add --type "${4:-pref}" --owner "${5:-user}" --key "$1" --tags "$2" --supersedes "$3" -
}
# 1. useless: empty, expired, about removed systems, history notes, superseded
for r in 5450a5 8debe2 ba132b 8ec5ec 2b0ea5 0ae3c0 8b2983 9506a2 d44ea4; do m forget "$r"; done

# 2. merged: finish and prove (dedication + acceptance-evidence + verified-by + test-yourself + setup-end-to-end)
add work.dedication coding,troubleshooting,reporting,deploy,device 7568c0,b80e0e,6ee2b5,434377,9cf949 <<'T'
DEDICATION: save Giovanni work, never give them work; half-done work is not acceptable (it caused the 2026-11-04 failure).
1 DEFINE DONE first as Giovanni's observable outcome. Configuration, installation or passing component tests do not prove it; verify the real path and visible behaviour.
2 FINISH end to end, installs and setup included; hand over only steps that need sudo or Giovanni's own approval. After coding, do a debugging pass and test reversible features yourself (on the phone for a phone feature). Investigate evidence before asking.
3 CHECK BEFORE CLAIMING: never say something is missing, impossible, working, done or verified without running the check in this session and reading the output (ls, which, adb devices, --help, a real attempt); else say 'not checked' and keep the task open.
4 If a check is too costly, slow or unsafe, say what was skipped, why, the risk and your advice; never skip silently.
5 REPORT: compare the result with each requirement; lead with result, evidence and remaining limitation in plain language; say what is done, not done, unchecked; end with 'Verified by:' (what was run, what could not be checked).
T
# 3. merged: autonomy (build-then-ask + act-on-ok + routine-autonomy + no-approval-bureaucracy)
add work.autonomy coding,troubleshooting,deploy,reporting 50e8d1,b430cf,bd8d9b,486ad6 <<'T'
AUTONOMY: once a project and plan are approved, or Giovanni says 'solve it', build end to end without progress pauses and do the work (issues, log rows, fixes) instead of listing proposals; collect the open questions and ask them at the end. Proceed without repeated confirmation for routine, reversible edits, commands, checks and website access inside the task; batch unavoidable access requests instead of asking for each one. Before asking anything, check memory and past messages for decisions already made (example: pipeline-check licence = MIT). Systems built for the agents get no approval prompts or queues ('not a babysitter for the AI'): safety comes from structure (closed tool lists, protected paths, validated data between agents), actuators may run anything except sudo, and the system stays fast and small (bounded logs; a full disk it causes is its own failure). Outward-facing or destructive acts still need asking first (safety.ask-before-outward).
T
# 4. merged smaller pairs
add work.no-retired-refs docs-memory,coding 7ec2df,60122c <<'T'
A retired protocol or tool is not named in anything that works today (skills, CLAUDE.md, memory, READMEs, scripts); only history (ADRs, decision logs, the wiki page of the retired thing) may mention it. A system must read as if it had been designed this way from the start: one consistent scope document, no traces of discarded designs in code, policy or docs (rewrite as much as needed).
T
add telegram device,outward f53934,5a89a4 <<'T'
To send Giovanni a message or file use the tg-send bot on the Acer (tg-send "text" or tg-send -f FILE [caption]), never the phone's Telegram app. Read ~/.local/bin/tg-send first: it has no --help (any argument is sent as a message). It is one-way, only to Giovanni; messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages, so always tell Giovanni to check that chat. Files up to 50 MB. The token is in ~/.config/telegram-bot, never in memory. Telegram bots are not end-to-end encrypted: send no patient data. Unprompted messages need Giovanni's go-ahead per kind.
T
add work.phone-stay-awake device c64de9,81b65f <<'T'
Giovanni's phone must stay awake for other projects: never turn off or lower its stay-awake setting (svc power stayon, stay_on_while_plugged_in, screen timeout). Since 2026-10-29 stay_on_while_plugged_in is 3 (AC+USB) at Giovanni's request; the 60 s screen timeout is unchanged. If a test needs the screen on, only send a wake key; read a device setting before changing it and put back exactly what was there.
T
add style.plain-language reporting 97287f,8ee096 <<'T'
Explain in plain language: define each technical term the first time it appears and say what it means in human terms before the details. Never assume Giovanni knows something only mentioned in passing. When introducing new information or a pendency, name the specific component and change; avoid vague references such as 'migration' without saying what moves and why.
T
# 5. wrong facts and stale snapshots corrected
add host.nitro deploy,device 08274f fact migration <<'T'
Giovanni's laptop is an Acer Nitro (host yuji-nitro): Kubuntu 26.04 with Plasma 6 on Wayland, Nvidia RTX 3050 with 6 GB VRAM, 23 GB RAM, /tmp is RAM. A second NVMe (nvme0n1) is mounted only under /run/media (no fstab entry).
T
add project.quizapp quiz,coding ac5a32 fact migration <<'T'
QuizApp lives in ~/dev/QuizApp (Kotlin, GitHub remote yujideluca/german-quiz): a German B2 quiz with 3 modes and Anki-style scheduling, tested on the phone over adb.
T
add matcher.analysis-status radiology fcb609 fact <<'T'
Radiology matcher statistical analysis: the single status record is ~/dev/radiology-crawler/docs/analysis-status.json (readable: docs/ANALYSIS-STATUS.md and the step-by-step guide on the plan site home page ~/Documents/Radiology Report Matcher/index.html). Read it first when you continue the work; never trust a status copied anywhere else.
T
add quiz.web-standalone-release deploy,quiz 6e9a0b <<'T'
QuizWeb may ship a standalone maintenance release when it contains relevant changes, without waiting for another Android release. Ports of unreleased Android features still follow app promotion.
T
# 6. retag: the retired always tag goes; outward acts get their own tag
m tag language.reply reporting
m tag person.profile reporting,german
m tag policy.third-party-data docs-memory,outward
m tag safety.ask-before-outward outward,deploy
m tag git.no-force-push git
m tag release.promote deploy,outward
m tag release.pool-promote deploy,quiz,outward
