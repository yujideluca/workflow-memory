# Rules tagged status-quo

Generated 2026-11-14 from 1126 events. Do not edit: record changes as events.

the Status Quo tray

- [status-quo.e2e] After every major Status Quo tray change, repeat the manual pass on the real desktop, update crates/desktop/tests/e2e/manual-baseline.json and desktop_e2e.rs, and run tools/ui_e2e.sh (it needs a free screen: STATUS_QUO_E2E_SCREEN_IS_FREE=1, never while Giovanni uses the screen). (#87315b)
- [status-quo.one-paste-install] Status Quo must install on any supported system with one copy-paste command in the terminal (Linux: curl | bash; Windows: PowerShell one-liner), no clone, no Rust, from GitHub releases; fallback to source build when no prebuilt exists. Giovanni 2026-11-14. (#0c0933)
