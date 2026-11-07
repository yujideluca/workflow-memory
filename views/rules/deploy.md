# Rules tagged deploy

Generated 2026-11-07 from 864 events. Do not edit: record changes as events.

installing, releasing, changing configuration, outward-facing or destructive acts

- ... (#5450a5)
- ... (#8debe2)
- ... (#ba132b)
- [agent-guard.giovanni-authority] agent-guard: Giovanni's direct level requirement is never blocked by the eligibility filter; it runs with a literal warning (ADR-0002 section 3). Codex adapter is a placeholder until the Codex tokens renew (docs/PENDING.md in ~/dev/agent-guard). (#8ec5ec)
- [git.no-force-push] Never force-push. (#d6931b)
- [host.nitro] Giovanni's laptop is an Acer Nitro (host yuji-nitro, Kubuntu 24.04, X11, Nvidia): RTX 3050 with 6 GB VRAM, 23 GB RAM. A spare 512 GB NVMe is mounted only temporarily (no fstab entry). (#08274f)
- [pipeline-check.merge-block] Merges to main are blocked by the local pre-push check (pipeline-check --pre-push, hook in tools/hooks, enabled with git config core.hooksPath tools/hooks) because private repositories on the free GitHub plan cannot use branch protection; pipeline-check is public so CI needs no token (decided 2026-10-24). (#eba53a)
- [quiz.signing-key-backup] QuizApp signing key backup: german-quiz-release.jks is in Giovanni's Google Drive (My Drive root), uploaded 2026-10-22; original in ~/.android. Passwords are kept by Giovanni, not on Drive. (#8c714a)
- [release.pool-promote] Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25). (#ffd6ac)
- [release.promote] A version may be promoted to the user channel once it survives the automated tests updated for what it changes (gate with mutation + tests changed with the code); then promoting is Giovanni's decision. No minimum time in beta; do not argue for one. (#7a7bd2)
- [safety.ask-before-outward] Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (#4b8e6b)
- [service.claude-assistant] claude-assistant (systemd user service, linger on) runs 'claude remote-control' in tmux socket 'claude', home ~/assistant, app name yuji-nitro-assistant. bypassPermissions was Giovanni's own choice (2026-10-11): never change it without asking. Watch with claude-assistant attach (Ctrl+b d leaves); restart with systemctl --user restart claude-assistant. (#24f108)
- [work.acceptance-evidence] Correction after repeated false completion claims: define success as the user's observable outcome before acting. Configuration, installation and passing component tests do not prove that outcome. Verify the actual execution path and visible behavior; if inaccessible, state precisely what remains unverified and keep the task incomplete. Investigate available evidence before asking the user; perform authorized routine work yourself. Lead reports with the result, evidence and remaining limitation in plain language. (#b80e0e)
- [work.dedication] DEDICATION (core principle, every task): save Giovanni work, never give them work. Half-done work is never acceptable (it caused the 2026-11-04 workflow failure).
1 FINISH: done = the user's observable outcome was seen working (real path/device), not just tests or installed. No loose ends or next steps I could do myself.
2 CHECK BEFORE CLAIMING: never say a file/tool/device does not exist, is unavailable or impossible unless I ran the check this session (ls, which, adb devices, --help, a real attempt). Never say works/done/verified without running it and reading the output. Else say 'not checked'.
3 FOLLOW the existing rules for the task kind unprompted (mem rules TAG: phone test, debug pass, wiki). A broken rule is a defect I report and fix.
4 IF A CHECK is too costly, slow, token-heavy or unsafe: tell Giovanni openly what I skipped, why, cost/risk, my recommendation. Never skip silently or report a skipped check as passed.
5 BEFORE REPORTING compare the result with each requirement; state plainly what is done, not done, unchecked. (#7568c0)
- [work.no-agent-guard] Giovanni does not want agent-guard or any taskmaster/guard system that removes Claude's own tools. It was removed on 2026-11-04 after it locked sessions (lessons: ~/guard-incident-notes/LESSONS.md). Do not propose or rebuild it. (#22f752)
- [work.no-approval-bureaucracy] agent-guard and similar systems: Giovanni does not want approval prompts or queues ('not a babysitter for the AI'). Safety comes from structure (closed tool lists, protected paths, validated/formatted data between agents, the taskmaster deciding from what it sees). Actuators may run anything except sudo. The system must stay functional, fast and small (bounded logs); a full disk caused by the system is a system failure. (#486ad6)
- [work.routine-autonomy] Proceed without repeated confirmation for routine, reversible edits, commands, checks and website access within the requested task. Ask only when an action is dangerous or a required technical permission cannot be avoided; batch necessary access requests instead of asking for each command or site. (#bd8d9b)
- [work.setup-end-to-end] Do installs and setup end to end. Hand over only the steps that need sudo or Giovanni's own approval. (#9cf949)
- [work.verified-by] Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (#6ee2b5)
- [work.web-no-own-version] QuizWeb may ship a standalone maintenance release when it contains relevant changes, without waiting for another Android release. Ports of unreleased Android features still follow app promotion. Supersedes the blanket no-standalone-release rule. (#6e9a0b)
