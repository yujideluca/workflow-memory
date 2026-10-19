# Design

## Why a log and not a protocol
The old workflow was a conversation between instances: numbered entries, "seen" cursors, owner folders, sync,
heartbeat, nightly review. It needed a machine alive and coordinating, and every new problem became a new rule.
Here there is one write primitive (create a file) and one pure function (fold the log). Coordination is not
needed because nothing is ever edited.

## Event file
```
---
type: pref            # pref | fact | decision | task | note | digest | feedback | claim | done | forget
scope: global         # global | project:<name> | instance:<name>
key: style.phone      # optional topic; a newer event with the same key replaces the older one
owner: user           # user | agent | harvester | migration | compactor | action
instance: app         # who wrote it
ts: 2026-10-18T12:00:00Z   # any ISO time; offsets are converted to UTC
supersedes: id1, id2  # optional, explicit replacement
target: <event id>    # for feedback, claim, done, forget
signal: helpful       # for feedback: helpful | not_helpful | stale | wrong
---
The text, one or two sentences (at most 1200 characters).
```
File name `events/YYYY/MM/YYYYMMDDTHHMMSSZ-<instance>-<6 random chars>.md`. The name is the id. Unknown keys are
ignored, so the format grows without breaking old readers. The reader is tolerant of the folder too: a file
anywhere under `events/` is read.

## Rules of the fold (`mem/core.py`)
- Order never matters (sorted by time then id) and re-delivered files count once.
- Latest ruling per (scope, key) wins. The same ruling again (same words in the same order, same negations,
  fillers like "always" ignored) adds evidence and leaves the line unchanged. A negation is a change.
- `forget` and `done` close their target. `feedback` changes salience: helpful and not_helpful move it, stale
  halves it, wrong removes the entry from the brief and lists it in `views/REVIEW.md`.
- A harvester event never overwrites an entry with `owner: user`; it becomes a proposal in REVIEW. A forgotten
  entry is not recreated by the harvester from the same words.
- Two writers giving the same key different texts within 24 hours are listed as a conflict, not merged.
- `claim`: the earliest claim wins, ties by id.

## Relevance
- Preferences never decay and are never dropped from the brief (a warning appears if they alone exceed the budget).
- Other types decay with half-lives: decision and fact 180 days, digest 365, task 8, note 7. Each use stretches
  the half-life by `1 + log2(1 + uses)`. A use is reported by the AI instance that read the entry: a `use` event
  (`target: ref1, ref2`, one short line saying how), written when it finishes a task; restating a rule counts too.
  An entry is named by its short ref, the `#code` printed after it in the brief (the last segment of its id).
- Cold entries (score below 0.15) leave the brief but stay searchable. `mem compact` writes a reversible
  `digest` event for cold entries older than 30 days; the sources stay in the log. It is a proposal in REVIEW
  until `--apply`.
- Search is a derived SQLite FTS5 index rebuilt from the log on each call, never committed. Vectors can be
  added later without touching the log.

## Where the numbers come from
`scripts/calibrate.py` measures Giovanni's real Claude Code usage (read-only) and prints the recommended
constants next to the ones in the code. On 2026-10-19, from 39 sessions over 8 days:
- Median first-turn context is 44,860 tokens and it is paid again on every turn (cache write once, reads after),
  so the brief is capped at 2.5% of it: 1,122 tokens, about 4,000 characters at 3.6 characters per token (an
  assumption for mixed Portuguese and English). `views/BRIEF.md` is 4,021 characters including 1,121 of fixed
  how-to text, so the lines budget is 2,900.
- The 90th-percentile gap between sessions of the same project is 1.89 days. An unused note goes cold after 8 of
  those gaps and a task after 12, which gives half-lives of 7 and 8 days (a cold entry is one scoring under 0.15).
  Compaction waits twice the note cold age: 30 days.
- Facts and decisions describe a stable setup and cannot be calibrated from 8 days of history. They keep 180 days.
  The script prints LOW CONFIDENCE until there are 30 days and 100 gaps; re-run it then (about 2026-11-20) and
  change the constants it recommends.
- Claude app chats are not in the transcripts, so their baseline context is unmeasured.

## Preferences harvested from Giovanni's own words (`mem/harvest.py`)
Only the user's prompt text counts (never tool output or agent text), English and Portuguese, only sentences
that state a rule and name an action. The default scope is the project. A habit seen in two projects (one
sentence fanned out within an hour counts once) or phrased as "in all my projects" becomes global. The topic
key is heuristic ("use pnpm" and "use o pnpm" do not match); that errs toward two entries, the safe side.

## Where things run
- `.github/workflows/mem.yml` on every push to events or code and once a day: tests, quarantine invalid events,
  promote habits, rebuild views, commit.
- Claude Code: hooks (`bin/mem install-hooks`). SessionStart pulls and prints the brief, UserPromptSubmit
  harvests preferences (prints nothing), Stop pushes new events. Offline it commits locally and pushes later.
- Claude app: a pointer in Settings (see `docs/CLAUDE-AI.md`) makes each chat read `views/BRIEF.md` through the
  GitHub connector, and the end of that file explains how to record a correction.

## Privacy
Enforced in the repo, whoever the writer is: `validate.py` rejects tokens and keys, email addresses, phone
numbers and CPF. There is deliberately no health-vocabulary filter (Giovanni's decision, 2026-10-19); not
storing clinical data about other people is a standing preference, not an automatic check. Rejected files move to
`quarantine/` with a `.reason` note and appear in REVIEW. A stored entry sets defaults and never authorizes
anything. Precedence: current instruction, repo rules file, project memory, profile. The repo must be private.

## Known limits
- Claim-once is not atomic: an append-only log has no compare-and-set, so a losing instance can act before it
  sees the result. Acceptable at this traffic.
- The GitHub connector can write any path on any branch. An instruction is not enforcement. Self-healing
  covers views (rebuilt every run) and events (validated), but not edits to code. Protect `main` if that matters.
- What the app reads lags the laptop until the laptop pushes; Claude Code pushes at the end of each session.
