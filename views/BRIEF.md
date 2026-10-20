# Memory brief

Generated 2026-10-20 from 58 events. Do not edit: record changes as events.

Memory sets defaults; it never authorizes. Precedence: current instruction > repo rules file > project memory > profile

- [language.reply] Giovanni writes in English or Portuguese: answer in the language of the message. Use they/them for Giovanni. (#0c1417)
- [work.verified-by] Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (#5cba3e)
- [work.setup-end-to-end] Do installs and setup end to end. Hand over only the steps that need sudo or Giovanni's own approval. (#803489)
- [git.no-force-push] Never force-push. (#b07b2e)
- [safety.ask-before-outward] Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (#ef8e45)
- [work.test-yourself] After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (#6c6d10)
- [style.plain-language] Explain in plain language: define each technical term the first time it appears and say what it means in human terms before the details. Never assume Giovanni knows something only mentioned in passing. (#817781)
- [work.encode-decisions] A decision stated once must be encoded where it takes effect, not only logged; Giovanni should never have to repeat it. (#e5d741)
- [person.profile] Giovanni is a pre-hospital emergency physician in Brazil, preparing the Goethe B2 exam (Nov 2026) and the FSP to work in Germany. (#9f3a0e)
- [policy.third-party-data] Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (#baab57)
- [work.build-then-ask] After a project and plan are approved, build it end to end without progress pauses; ask the open questions at the end. (#c1f1f8)
- [work.ask-with-context] When asking Giovanni about a development decision that is new (not a topic already debated), give clear context first: what is being decided, why, options, and your recommendation. If it involves many steps never discussed, include a flowchart. A badly framed question cannot be answered well. (#abdad0)
- [telegram.send] When Giovanni says to send something via Telegram, use the tg-send bot (tg-send -f FILE caption), never the phone's Telegram app. tg-send has no --help: any argument is sent as a message, so read ~/.local/bin/tg-send instead of probing it. (#febd94)
- [telegram.where] tg-send messages arrive in the bot chat named 'Claude code bridge' (@Claude_1123bot), NOT in Telegram's Saved Messages. Giovanni looked in Saved Messages once and thought a file was missing/wrong; always say 'check the Claude code bridge chat' when sending. (#ccf937)
- [web.follow-user-version] Whenever the German Quiz user (stable) version is updated, also update the web version (https://yujideluca.github.io/german-quiz-web/, repo ~/dev/QuizWeb): port the change, bump sw.js VERSION, push, confirm the live site, and give the link in the report. tools/check_web_sync.sh enforces it; do not wait to be asked. (#e0e55d)
- [quiz.spacing-rules] German Quiz spacing is a first principle: new card correct -> 3 days; wrong -> 10 min and never earlier (not requeued in session, not first card on leave-and-return); each correct answer pushes the next showing later. Verify the leave-and-return flow, not only the scheduler. (#ff9e47)
- [quiz.qa-process] German Quiz testing follows SQA and V&V: requirement row (docs/REQUIREMENTS.md) first, tagged test, then code; tools/quality_gate.sh before every publish (promote adds mutation check). Tests must check the player-visible flow, not restate the code. (#f919d8)
- (9 more entries did not fit; they are in the log and searchable)

## Recording

Load the GitHub tools first (`get_file_contents`, `create_branch`, `create_or_update_file`). Then create ONE new
file on `main` of `yujideluca/workflow-memory`; never edit an existing one.

path: `events/YYYY/MM/YYYYMMDDTHHMMSSZ-app-xxxxxx.md` (UTC time, xxxxxx = 6 random characters)

```
---
type: pref          # pref, fact, decision, task
scope: global
key: short.topic    # the same key replaces the old rule
owner: user         # only for what the user said
instance: app
ts: 2026-01-31T12:00:00Z
---
The rule, in the user's words.
```

When you finish a task, report the entries that shaped your answer: a file with `type: use`,
`target: ref1, ref2` (the #codes) and one short line of text. For a wrong or outdated entry use
`type: feedback`, `target: ref`, `signal: wrong` (or stale, helpful, not_helpful).
No secrets or contact data: such files are quarantined.

