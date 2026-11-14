# Rules tagged outward

Generated 2026-11-14 from 1092 events. Do not edit: record changes as events.

acts others see or cannot undo: sending email or messages, purchases, publishing, deleting

- [hospitation.after-only] Giovanni 2026-11-10: Heidelberg has already accepted the Hospitation (5-30 April 2027); only documents remain to be sent. Do not seek other Hospitation or pathology places before the Hospitation ends, to avoid accepting and later declining an offer. (#c8ccf6)
- [notify.telegram-process] Giovanni 2026-11-10: send process updates (Gmail replies that change the Hospitation/Approbation process, missed milestones) by Telegram via tg-send. This is the go-ahead for that kind of message; keep them short and without patient or third-party data. (#24ea86)
- [policy.third-party-data] Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (#2ed756)
- [release.pool-promote] Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25). (#8c704c)
- [release.promote] A version may be promoted to the user channel once it survives the automated tests updated for what it changes (gate with mutation + tests changed with the code); then promoting is Giovanni's decision. No minimum time in beta; do not argue for one. (#510e5a)
- [safety.ask-before-outward] Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (#095231)
- [telegram] To send Giovanni a message or file use the tg-send bot on the Acer (tg-send "text" or tg-send -f FILE [caption]), never the phone's Telegram app. Read ~/.local/bin/tg-send first: it has no --help (any argument is sent as a message). It is one-way, only to Giovanni; messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages, so always tell Giovanni to check that chat. Files up to 50 MB. The token is in ~/.config/telegram-bot, never in memory. Telegram bots are not end-to-end encrypted: send no patient data. Unprompted messages need Giovanni's go-ahead per kind. (#6f4975)
- [work.delegate-admin] Giovanni 2026-11-10: bureaucracy makes them anxious; do everything possible in their place (emails, documents, checklists, quote comparison, tracking Gmail replies). Be proactive: tell them when an email updates the process and when a time milestone passed without its goal met. Outward acts still follow safety.ask-before-outward. (#ef15a9)
