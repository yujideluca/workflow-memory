# Rules tagged device

Generated 2026-11-07 from 900 events. Do not edit: record changes as events.

phone, adb, browser, Telegram

- [browser.hang-refresh] Quando algum site travar durante uma tarefa no navegador, dê F5 (recarregue a página) e continue, em vez de esperar ou desistir. (#17621c)
- [device.phone] Giovanni's phone is a Motorola edge 50 fusion, driven over adb for app tests. (#109c32)
- [host.nitro] Giovanni's laptop is an Acer Nitro (host yuji-nitro): Kubuntu 26.04 with Plasma 6 on Wayland, Nvidia RTX 3050 with 6 GB VRAM, 23 GB RAM, /tmp is RAM. A second NVMe (nvme0n1) is mounted only under /run/media (no fstab entry). (#0cb7ba)
- [telegram] To send Giovanni a message or file use the tg-send bot on the Acer (tg-send "text" or tg-send -f FILE [caption]), never the phone's Telegram app. Read ~/.local/bin/tg-send first: it has no --help (any argument is sent as a message). It is one-way, only to Giovanni; messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages, so always tell Giovanni to check that chat. Files up to 50 MB. The token is in ~/.config/telegram-bot, never in memory. Telegram bots are not end-to-end encrypted: send no patient data. Unprompted messages need Giovanni's go-ahead per kind. (#6f4975)
- [work.dedication] DEDICATION: save Giovanni work, never give them work; half-done work is not acceptable (it caused the 2026-11-04 failure).
1 DEFINE DONE first as Giovanni's observable outcome. Configuration, installation or passing component tests do not prove it; verify the real path and visible behaviour.
2 FINISH end to end, installs and setup included; hand over only steps that need sudo or Giovanni's own approval. After coding, do a debugging pass and test reversible features yourself (on the phone for a phone feature). Investigate evidence before asking.
3 CHECK BEFORE CLAIMING: never say something is missing, impossible, working, done or verified without running the check in this session and reading the output (ls, which, adb devices, --help, a real attempt); else say 'not checked' and keep the task open.
4 If a check is too costly, slow or unsafe, say what was skipped, why, the risk and your advice; never skip silently.
5 REPORT: compare the result with each requirement; lead with result, evidence and remaining limitation in plain language; say what is done, not done, unchecked; end with 'Verified by:' (what was run, what could not be checked). (#1af374)
- [work.phone-stay-awake] Giovanni's phone must stay awake for other projects: never turn off or lower its stay-awake setting (svc power stayon, stay_on_while_plugged_in, screen timeout). Since 2026-10-29 stay_on_while_plugged_in is 3 (AC+USB) at Giovanni's request; the 60 s screen timeout is unchanged. If a test needs the screen on, only send a wake key; read a device setting before changing it and put back exactly what was there. (#dac20f)
- [work.test-ui-on-phone] Test any phone-facing web UI on Giovanni's real phone (Motorola, adb), not only in a narrowed desktop browser: serve the build with adb reverse and read frame times with Chrome DevTools over adb forward; the public wiki address needs Giovanni's own Google sign-in, so do not sign in for them. (#c6d902)
