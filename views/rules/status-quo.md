# Rules tagged status-quo

Generated 2026-11-28 from 1823 events. Do not edit: record changes as events.

the Status Quo tray

- [status-quo.all-deps-one-command] Giovanni 2026-11-14: the tray install command must bring ALL its dependencies (system libraries, and Rust on the source path) automatically; nothing left for the user to install first. Test installers against the real environment, not only forced env vars (v0.1.1 always asked sudo because of a pipefail bug). (#b7d0fe)
- [status-quo.e2e] After every major Status Quo tray change, repeat the manual pass on the real desktop, update crates/desktop/tests/e2e/manual-baseline.json and desktop_e2e.rs, and run tools/ui_e2e.sh (it needs a free screen: STATUS_QUO_E2E_SCREEN_IS_FREE=1, never while Giovanni uses the screen). (#87315b)
- [status-quo.no-code-signing] Giovanni 2026-11-19: Status Quo will not pay for code signing; the Windows installer stays unsigned (SmartScreen notice and Defender command-line detection are accepted limits; document them, do not propose buying a certificate). (#a7b9e9)
- [status-quo.one-paste-install] Status Quo must install on any supported system with one copy-paste command in the terminal (Linux: curl | bash; Windows: PowerShell one-liner), no clone, no Rust, from GitHub releases; fallback to source build when no prebuilt exists. Giovanni 2026-11-14. (#0c0933)
- [work.plug-and-play-means-everything] Giovanni 2026-11-14: 'plug and play' / 'easy install' means the whole outcome for a layperson in the FIRST build: one copy-paste command that installs every dependency and the program and starts it, beginner-written docs on top, a published release, and the real published command run once. Do not deliver the narrowest literal reading (files on a release page) and wait for a correction; define done as that outcome before building. (#739865)
