# Rules tagged troubleshooting

Generated 2026-11-06 from 727 events. Do not edit: record changes as events.

debugging, testing, fixing findings, proving that it works

- [status-quo.e2e] After every major Status Quo tray change, repeat the manual pass on the real desktop, update crates/desktop/tests/e2e/manual-baseline.json and desktop_e2e.rs, and run tools/ui_e2e.sh (it needs a free screen: STATUS_QUO_E2E_SCREEN_IS_FREE=1, never while Giovanni uses the screen). (#87315b)
- [work.acceptance-evidence] Correction after repeated false completion claims: define success as the user's observable outcome before acting. Configuration, installation and passing component tests do not prove that outcome. Verify the actual execution path and visible behavior; if inaccessible, state precisely what remains unverified and keep the task incomplete. Investigate available evidence before asking the user; perform authorized routine work yourself. Lead reports with the result, evidence and remaining limitation in plain language. (#b80e0e)
- [work.fix-findings] Findings from a maintenance review that Giovanni answers 'deve' are fixed in the same session, with the test first; hypotheses wait for his answer. (#23805a)
- [work.routine-autonomy] Proceed without repeated confirmation for routine, reversible edits, commands, checks and website access within the requested task. Ask only when an action is dangerous or a required technical permission cannot be avoided; batch necessary access requests instead of asking for each command or site. (#bd8d9b)
- [work.test-ui-on-phone] Test any phone-facing web UI on Giovanni's real phone (Motorola, adb), not only in a narrowed desktop browser: serve the build with adb reverse and read frame times with Chrome DevTools over adb forward; the public wiki address needs Giovanni's own Google sign-in, so do not sign in for them. (#c6d902)
- [work.test-yourself] After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (#434377)
- [work.troubleshoot-documentation] Investigate documentation failures before declaring them blocked. Prefer an isolated committed worktree and narrow reconciliation that preserves other sessions’ edits; do not treat a dirty wiki tree alone as the end of troubleshooting. (#0d1cfd)
- [work.verified-by] Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (#6ee2b5)
