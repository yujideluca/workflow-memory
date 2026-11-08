# Rules tagged outward

Generated 2026-11-08 from 920 events. Do not edit: record changes as events.

acts others see or cannot undo: sending email or messages, purchases, publishing, deleting

- [policy.third-party-data] Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (#2ed756)
- [release.pool-promote] Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25). (#8c704c)
- [release.promote] A version may be promoted to the user channel once it survives the automated tests updated for what it changes (gate with mutation + tests changed with the code); then promoting is Giovanni's decision. No minimum time in beta; do not argue for one. (#510e5a)
- [safety.ask-before-outward] Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (#095231)
- [telegram] To send Giovanni a message or file use the tg-send bot on the Acer (tg-send "text" or tg-send -f FILE [caption]), never the phone's Telegram app. Read ~/.local/bin/tg-send first: it has no --help (any argument is sent as a message). It is one-way, only to Giovanni; messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages, so always tell Giovanni to check that chat. Files up to 50 MB. The token is in ~/.config/telegram-bot, never in memory. Telegram bots are not end-to-end encrypted: send no patient data. Unprompted messages need Giovanni's go-ahead per kind. (#6f4975)
