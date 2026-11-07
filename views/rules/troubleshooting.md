# Rules tagged troubleshooting

Generated 2026-11-07 from 862 events. Do not edit: record changes as events.

debugging, testing, fixing findings, proving that it works

- [ci.required-jobs] Every CI job that checks a requirement must be a required check on main, and a push is done only when all its jobs are green, not just the required one. Lesson 2026-11-06: status-quo's windows job (SQ-36) stayed red from b701cda unnoticed because only gate was required. (#ea94f4)
- [status-quo.e2e] After every major Status Quo tray change, repeat the manual pass on the real desktop, update crates/desktop/tests/e2e/manual-baseline.json and desktop_e2e.rs, and run tools/ui_e2e.sh (it needs a free screen: STATUS_QUO_E2E_SCREEN_IS_FREE=1, never while Giovanni uses the screen). (#87315b)
- [tests.scratch-folders] Tests never build temp folders by hand (temp_dir()/name-PID, createTempDirectory): /tmp is RAM on the laptop and systemd clears it only after 10 days, and each rerun has a new PID, so leftovers pile up. Use the repo's self-deleting helper (status-quo crates/scratch.rs, pipeline-check tests/common Scratch, JUnit TemporaryFolder in QuizApp); any other temp-folder line must say 'scratch-ok:' and why, which each gate checks. (#81e0d0)
- [work.acceptance-evidence] Correction after repeated false completion claims: define success as the user's observable outcome before acting. Configuration, installation and passing component tests do not prove that outcome. Verify the actual execution path and visible behavior; if inaccessible, state precisely what remains unverified and keep the task incomplete. Investigate available evidence before asking the user; perform authorized routine work yourself. Lead reports with the result, evidence and remaining limitation in plain language. (#b80e0e)
- [work.dedication] DEDICATION (core principle, every task): save Giovanni work, never give them work. Half-done work is never acceptable (it caused the 2026-11-04 workflow failure).
1 FINISH: done = the user's observable outcome was seen working (real path/device), not just tests or installed. No loose ends or next steps I could do myself.
2 CHECK BEFORE CLAIMING: never say a file/tool/device does not exist, is unavailable or impossible unless I ran the check this session (ls, which, adb devices, --help, a real attempt). Never say works/done/verified without running it and reading the output. Else say 'not checked'.
3 FOLLOW the existing rules for the task kind unprompted (mem rules TAG: phone test, debug pass, wiki). A broken rule is a defect I report and fix.
4 IF A CHECK is too costly, slow, token-heavy or unsafe: tell Giovanni openly what I skipped, why, cost/risk, my recommendation. Never skip silently or report a skipped check as passed.
5 BEFORE REPORTING compare the result with each requirement; state plainly what is done, not done, unchecked. (#7568c0)
- [work.fix-findings] Findings from a maintenance review that Giovanni answers 'deve' are fixed in the same session, with the test first; hypotheses wait for his answer. (#23805a)
- [work.routine-autonomy] Proceed without repeated confirmation for routine, reversible edits, commands, checks and website access within the requested task. Ask only when an action is dangerous or a required technical permission cannot be avoided; batch necessary access requests instead of asking for each command or site. (#bd8d9b)
- [work.test-ui-on-phone] Test any phone-facing web UI on Giovanni's real phone (Motorola, adb), not only in a narrowed desktop browser: serve the build with adb reverse and read frame times with Chrome DevTools over adb forward; the public wiki address needs Giovanni's own Google sign-in, so do not sign in for them. (#c6d902)
- [work.test-yourself] After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (#434377)
- [work.troubleshoot-documentation] Investigate documentation failures before declaring them blocked. Prefer an isolated committed worktree and narrow reconciliation that preserves other sessions’ edits; do not treat a dirty wiki tree alone as the end of troubleshooting. (#0d1cfd)
- [work.verified-by] Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (#6ee2b5)
