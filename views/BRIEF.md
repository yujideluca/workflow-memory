# Memory brief

Generated 2026-10-22 from 100 events. Do not edit: record changes as events.

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
- [pendencies.verify-before-reminding] Pendencies (unfinished goals, known problems) are open items: record them with mem task --check HOW. They show in every chat until solved, archived or deleted; project-specific only when Giovanni says so. Before reminding Giovanni of one, run its check; if it no longer applies, close it; if unchecked, say so. Never call an item open from memory alone. (#ad71c7)
- [work.no-qwen] Local Qwen is not part of the workflow: do not use or propose it for coding or delegation. Its files were deleted 2026-10-21. (#303850)
- [work.maintenance] Software projects follow the golden path: ADRs for structural decisions, requirements before code, one quality gate run by CI on every push, debt as GitHub Issues labelled debt/P1-P3, about one session in five on debt or prevention, monthly architecture review. New projects start from ~/dev/project-template. (#d975f2)
- [release.promote] A version may be promoted to the user channel once it survives the automated tests updated for what it changes (gate with mutation + tests changed with the code); then promoting is Giovanni's decision. No minimum time in beta; do not argue for one. (#d71784)
- (9 more entries did not fit; they are in the log and searchable)

## Open items

Open items (shown in every chat until solved, archived or deleted):
- [open item maintenance] Monthly architecture review of all ~/dev projects (first one due by 2026-11-22): run the checklist in ~/dev/project-template/docs/MAINTENANCE.md, add a Preventive row 'Monthly architecture review' to each project's decision log | check: ! grep -qE "^\| $(date +%Y-%m)-[0-9]{2} \| Preventive \| \*\*Monthly architecture review" ~/dev/QuizApp/DESIGN.md (open = no review row this month; checklist in ~/dev/project-template/docs/MAINTENANCE.md) (since 2026-10-22, #4dcb2c)
- [open item] Phased apt updates (tmux, ubuntu-pro-client, ubuntu-pro-client-l10n) still held back since 2026-10-21; Giovanni chose to wait; rerun sudo apt upgrade in a few days | check: ! apt list --upgradable 2>/dev/null | grep -q -E '^(tmux|ubuntu-pro-client)/' (since 2026-10-21, #2526ce)

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
Open items: `type: task`, text `what is open | check: how to verify it still applies`, optional `category: x`.
Verify: `type: use`, `target: ref`, a line on how. Solved: `type: done`; park: `type: archive` (`reopen`
undoes it); delete: `type: forget`; each with `target: ref`.
No secrets or contact data: such files are quarantined.

