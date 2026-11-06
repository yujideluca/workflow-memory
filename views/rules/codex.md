# Rules tagged codex

Generated 2026-11-06 from 735 events. Do not edit: record changes as events.

work done by Codex

- [codex.touchpad-fullscreen] 2026-10-26: Codex had tmux mouse=on, alternate screen on, and app mouse flags off. Wheel input did not move its transcript; Page Up did. codex-pbar now binds wheel to Page Up/Down only for fullscreen apps without mouse capture, preserving native mouse/copy mode. Giovanni confirmed physical scrolling restored. Real terminal tests cover both directions, two sizes, fresh isolated servers and the installed launcher. Earlier test checked only mouse=on. Reboot untested. Reapply or undo live routing: ~/fixes/codex-touchpad-scroll.sh [--undo]. (#0ae3c0)
- [codex.touchpad-quarter] 2026-10-27 UTC: the previous PageUp/PageDown wheel fallback restored navigation but was too sensitive. codex-pbar now emits native one-row mouse events max(1,floor(current pane height/4)) times per tick without app mouse capture, recalculated per event after resize. Live measured 13 rows in pane 52; installed fresh-launch fixture measured 7 in pane 29. Giovanni confirmed this sensitivity is right. Tests count events at heights 24,18,3 in both directions and preserve native mouse capture. Physical reboot untested. (#8b2983)
- [work.no-codex-36h] Codex has no budget (Giovanni, 2026-11-05): work without Codex for 36 hours, until 2026-11-06 12:30 (UTC-3). Do not wait for it, start Codex steps or propose them; do every step Claude can do alone (Haiku workers for tagging). After that time, ask again before assuming Codex is back. (#2b0ea5)
