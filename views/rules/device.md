# Rules tagged device

Generated 2026-11-07 from 862 events. Do not edit: record changes as events.

phone, adb, browser, Telegram

- [browser.hang-refresh] Quando algum site travar durante uma tarefa no navegador, dê F5 (recarregue a página) e continue, em vez de esperar ou desistir. (#17621c)
- [codex.touchpad-fullscreen] 2026-10-26: Codex had tmux mouse=on, alternate screen on, and app mouse flags off. Wheel input did not move its transcript; Page Up did. codex-pbar now binds wheel to Page Up/Down only for fullscreen apps without mouse capture, preserving native mouse/copy mode. Giovanni confirmed physical scrolling restored. Real terminal tests cover both directions, two sizes, fresh isolated servers and the installed launcher. Earlier test checked only mouse=on. Reboot untested. Reapply or undo live routing: ~/fixes/codex-touchpad-scroll.sh [--undo]. (#0ae3c0)
- [codex.touchpad-quarter] 2026-10-27 UTC: the previous PageUp/PageDown wheel fallback restored navigation but was too sensitive. codex-pbar now emits native one-row mouse events max(1,floor(current pane height/4)) times per tick without app mouse capture, recalculated per event after resize. Live measured 13 rows in pane 52; installed fresh-launch fixture measured 7 in pane 29. Giovanni confirmed this sensitivity is right. Tests count events at heights 24,18,3 in both directions and preserve native mouse capture. Physical reboot untested. (#8b2983)
- [device.phone] Giovanni's phone is a Motorola edge 50 fusion, driven over adb for app tests. (#109c32)
- [telegram] To send via Telegram use the tg-send bot (tg-send -f FILE caption), never the phone app; read ~/.local/bin/tg-send, it has no --help (any argument is sent as a message). Messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages: always tell Giovanni to check that chat. (#f53934)
- [tool.telegram-send] To send Giovanni a message or file, run tg-send "text" or tg-send -f FILE [caption] on the Acer (bot @Claude_1123bot, one-way, only to Giovanni's saved chat; token in ~/.config/telegram-bot, never in memory). Files up to 50 MB. Telegram bots are not end-to-end encrypted: send no patient data. Unprompted messages need Giovanni's go-ahead per kind. (#5a89a4)
- [work.dedication] DEDICATION (core principle, every task): save Giovanni work, never give them work. Half-done work is never acceptable (it caused the 2026-11-04 workflow failure).
1 FINISH: done = the user's observable outcome was seen working (real path/device), not just tests or installed. No loose ends or next steps I could do myself.
2 CHECK BEFORE CLAIMING: never say a file/tool/device does not exist, is unavailable or impossible unless I ran the check this session (ls, which, adb devices, --help, a real attempt). Never say works/done/verified without running it and reading the output. Else say 'not checked'.
3 FOLLOW the existing rules for the task kind unprompted (mem rules TAG: phone test, debug pass, wiki). A broken rule is a defect I report and fix.
4 IF A CHECK is too costly, slow, token-heavy or unsafe: tell Giovanni openly what I skipped, why, cost/risk, my recommendation. Never skip silently or report a skipped check as passed.
5 BEFORE REPORTING compare the result with each requirement; state plainly what is done, not done, unchecked. (#7568c0)
- [work.phone-stay-awake] Giovanni's phone must stay awake for other projects: never turn off or change its stay-awake setting (svc power stayon, stay_on_while_plugged_in, screen timeout). If a test needs the screen on, only send a wake key; read a device setting before changing it and put back exactly what was there. (#c64de9)
- [work.phone-stay-awake-ac] Giovanni asked on 2026-10-29 that the test phone's screen stop closing: stay_on_while_plugged_in was 2 (USB only), now 3 (AC+USB). Screen timeout (60 s) unchanged. Still never turn stay-awake off. (#81b65f)
- [work.test-ui-on-phone] Test any phone-facing web UI on Giovanni's real phone (Motorola, adb), not only in a narrowed desktop browser: serve the build with adb reverse and read frame times with Chrome DevTools over adb forward; the public wiki address needs Giovanni's own Google sign-in, so do not sign in for them. (#c6d902)
- [work.test-yourself] After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (#434377)
