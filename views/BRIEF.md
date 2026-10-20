# Memory brief

Generated 2026-10-20 from 79 events. Do not edit: record changes as events.

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
- [telegram] To send via Telegram use the tg-send bot (tg-send -f FILE caption), never the phone app; read ~/.local/bin/tg-send, it has no --help (any argument is sent as a message). Messages arrive in the 'Claude code bridge' chat (@Claude_1123bot), NOT Saved Messages: always tell Giovanni to check that chat. (#c09dc8)
- [decision.no-health-filter] Memory validation has no automatic health-vocabulary filter. Not storing clinical data about other people stays a standing preference, not a check. (#116712)
- [decision.ai-memory-inspiration] ai-memory (akitaonrails) is inspiration only; it is never installed. (#72e118)
- [decision.memory-v3] The old claude-workflow-backup protocol is abandoned. workflow-memory is the new workflow: append-only event log, computed state, views built by a GitHub Action. (#a20747)
- (6 more entries did not fit; they are in the log and searchable)

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

