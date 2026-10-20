# Preferences in force

Generated 2026-10-20 from 80 events. Do not edit: record changes as events.

- [instance:assistant] style.phone: Replies are read on a phone: short, lead with the answer, no wide tables. (user)
- [global] language.reply: Giovanni writes in English or Portuguese: answer in the language of the message. Use they/them for Giovanni. (user)
- [global] work.verified-by: Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be checked. (user)
- [global] work.setup-end-to-end: Do installs and setup end to end. Hand over only the steps that need sudo or Giovanni's own approval. (user)
- [global] git.no-force-push: Never force-push. (user)
- [global] safety.ask-before-outward: Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless Giovanni has explicitly said to proceed. (user)
- [global] work.test-yourself: After coding, do a first debugging pass and test reversible features yourself (for example on the phone) instead of asking. (user)
- [global] style.plain-language: Explain in plain language: define each technical term the first time it appears and say what it means in human terms before the details. Never assume Giovanni knows something only mentioned in passing. (user)
- [global] work.encode-decisions: A decision stated once must be encoded where it takes effect, not only logged; Giovanni should never have to repeat it. (user)
- [global] person.profile: Giovanni is a pre-hospital emergency physician in Brazil, preparing the Goethe B2 exam (Nov 2026) and the FSP to work in Germany. (user)
- [global] policy.third-party-data: Never store clinical, secret or contact data about other people in memory. If a case needs it, Giovanni will ask for a specific procedure. (user)
- [global] work.build-then-ask: After a project and plan are approved, build it end to end without progress pauses; ask the open questions at the end. (user)
- [global] work.ask-with-context: When asking Giovanni about a development decision that is new (not a topic already debated), give clear context first: what is being decided, why, options, and your recommendation. If it involves many steps never discussed, include a flowchart. A badly framed question cannot be answered well. (user)
- [project:QuizApp] quiz.spacing-rules: German Quiz spacing is a first principle: new card correct -> 3 days; wrong -> 10 min and never earlier (not requeued in session, not first card on leave-and-return); each correct answer pushes the next showing later. Verify the leave-and-return flow, not only the scheduler. (user)
- [global] telegram: To send via Telegram use the tg-send bot (tg-send -f FILE caption), never the phone app; read ~/.local/bin/tg-send, it has no --help (any argument is sent as a message). Messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages: always tell Giovanni to check that chat. (user)
- [project:QuizApp] web.follow-user-version: Whenever the German Quiz user (stable) version is updated, also update the web version (https://yujideluca.github.io/german-quiz-web/, repo ~/dev/QuizWeb): port the change, bump sw.js VERSION, push, confirm the live site, and give the link in the report. tools/check_web_sync.sh enforces it; do not wait to be asked. (user)
- [project:QuizApp] quiz.qa-process: German Quiz testing follows SQA and V&V: requirement row (docs/REQUIREMENTS.md) first, tagged test, then code; tools/quality_gate.sh before every publish (promote adds mutation check). Tests must check the player-visible flow, not restate the code. (user)
- [project:QuizWeb] web.follow-user-version: Whenever the German Quiz user (stable) version is updated, also update the web version (https://yujideluca.github.io/german-quiz-web/, repo ~/dev/QuizWeb): port the change, bump sw.js VERSION, push, confirm the live site, and give the link in the report. tools/check_web_sync.sh enforces it; do not wait to be asked. (user)
- [project:QuizWeb] quiz.spacing-rules: German Quiz spacing is a first principle: new card correct -> 3 days; wrong -> 10 min and never earlier (not requeued in session, not first card on leave-and-return); each correct answer pushes the next showing later. Verify the leave-and-return flow, not only the scheduler. (user)
