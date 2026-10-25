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
- Other types decay with half-lives: decision and fact 180 days, digest 365, note 7. A task never decays (see Open items). Each use stretches
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
  those gaps and which gives a half-life of 7 days for notes (a cold entry is one scoring under 0.15).
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

## Open items (pendencies)

What is still open, kept in front of Giovanni until it is dealt with, so goals and known problems are not lost
between sessions or between Claude Code and the Claude app. It is its own flow (`mem/pendency.py`) with its own
budget; nothing else competes with it.

- **What it is.** A `task` event: `what is open | check: how to verify it still applies`, with an optional
  `category`. `mem task --check HOW [--category C] "text"`; the CLI refuses a task without a check. A chat may
  write the same file by hand (the how-to in `views/BRIEF.md` says how); one without a check is shown as
  "(no check recorded)" and listed under Warnings in `views/REVIEW.md`.
- **Nothing lapses.** An open item is announced at the start of every chat until Giovanni decides. Three exits:
  solved (`mem done REF`), parked (`mem archive REF`: no more notifications, still listed with
  `mem pending --archived` and searchable; `mem reopen REF` brings it back when it becomes a problem) and
  deleted (`mem forget REF`: gone from every view and from search; the file stays in the append-only log, like
  any entry). A check (`mem use REF --note HOW`) records when and how it was last verified and changes nothing else.
- **Scope.** Shown everywhere by default: any project, any chat. Only when Giovanni says so is an item, or a whole
  category, made scope-dependent: `mem scope project:X REF` or `mem scope project:X --category C`. That writes a
  `rescope` event; a category rule covers present and future items of that category; the latest applicable
  rescope wins (by timestamp; a tie is settled by event id, so two marks in the same second are arbitrary);
  `mem scope global ...` undoes it. The Claude app has no project, so its file shows global items only.
- **Budget.** 2,000 tokens (7,200 characters at the same 3.6 characters per token as the brief), separate from
  the 2,900-character entry budget. `core.brief` ignores tasks, so neither budget can take room from the other.
  Within the ceiling the most recently active items come first; the rest are counted ("N more did not fit") and
  raise a warning that points at solve, archive or delete. One item never takes more than 500 characters. Worst
  case the ceiling is 4.4% of the median first turn (45,740 tokens on 2026-10-20); with no open items it costs
  nothing. Archived items take no budget.
- **Where it shows.** The session-start hook (global items plus those of the current project), `mem brief`, and
  `views/BRIEF.md` for the Claude app. `mem pending [--archived|--all]` lists every item, whatever its scope.
- **Rules it carries.** Session start always tells the reader how to record, solve, park, delete and scope an
  item. When items are shown it adds the verify rule: before reminding Giovanni of one, run its check in the
  current context; if it no longer applies, close it and do not present it as pending; if it could not be checked,
  say "unchecked" and how it was verified.
- **What else knows about it.** `events.py` (types `archive`, `reopen`, `rescope`; field `category`),
  `validate.py` (targets, category), `core.py` (control events are hidden; `compaction_proposals` never digests a
  task), `search.py` (finds open and archived items), `project.build` (section and warnings),
  `scripts/calibrate.py` (counts entry lines only, reports the ceiling). `tests/test_pendency.py` covers each of
  these; a mutation check (25 mutants) was run against it.

Why it exists: on 2026-10-20 an item was reported as open from memory of the conversation, after the system had
already settled it.

## Decision log

Newest first. **Type** is the ISO/IEC/IEEE 14764 category (corrective, adaptive, perfective, preventive). Structural decisions also have an ADR in `docs/adr/`.

| Date | Type | Decision | Why |
|---|---|---|---|
| 2026-10-25 | Adaptive | **workflow-memory stays without branch protection; documented as an exception** (pipeline-check v0.5.0, PC-16). The repository is public, but a simulation showed that a required `gate` check rejects the push of the `mem` job (`GH006 Required status check "gate" is expected`), because that job pushes derived files to `main` with the built-in token and GitHub does not let that bot bypass a rule on a personal account. Giovanni chose to keep the local pre-push check (`tools/hooks/pre-push`) and to record the exception in `pipeline-check.toml` (`protection_exception`), so `protecao-de-branch` is `aviso` with the reason, not `falha`. Not chosen: a personal access token for the job (a secret to renew), a separate branch for derived files (changes how every reader gets the views). | A gap accepted on purpose must stay visible and written where the check reads it. |
| 2026-10-25 | Preventive | **Monthly architecture review**: pipeline-check v0.4.0, local mode, report of 2026-10-25: 0 falhas, 0 avisos, 1 pulado (protecao-de-branch); 1 proposal; proposals created as pipeline-check#4 | Monthly review standard (ADR-0013): the program measures, the skill judges |
| 2026-10-24 | Corrective | **First maintenance review: bug-finding tests and four fixes** (`docs/TESTES-AUTOMATIZADOS.md`, `tests/test_bughunt.py`): event headers are collapsed to one line (a newline could forge `owner: user`), GitHub fine-grained, GitLab and Google API tokens count as secrets, international phone numbers count as contact data, a repeated ruling keeps its `supersedes` | The privacy boundary and the file format had gaps no existing test looked at; the check was written from the rules, not from the code |
| 2026-10-24 | Preventive | **`pipeline-check` adopted** ([ADR-0004](adr/0004-program-measures-skill-judges.md)): the shared program (own repository, pinned in `pipeline-check.version`) runs the unit tests once in CI and locally, plus a local pre-push check for code paths | The tests ran only on pushes touching the data paths and nothing blocked a bad push of the tools themselves |
| 2026-10-24 | Preventive | **One list of privacy patterns** (`mem/privacy-patterns.tsv`), read by `validate.py` and copied to the wiki, whose gate compares the copy (issue #3) | Two hand-kept lists had drifted: memory lacked Telegram bot tokens, Google client secrets and `password: value`; the wiki lacked bearer tokens. The union is stricter in both. E-mail stays a per-program policy (memory refuses all, the wiki allows two) | 
