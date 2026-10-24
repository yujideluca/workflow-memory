# Automated bug-finding tests: workflow-memory

Last reviewed: 320025c 2026-10-24
Created by the skill `gerar-teste-automatizado` (create mode) in the first maintenance review. Update mode starts from the commit above.

## Analysis summary
Python standard library only. `mem/core.py` folds an append-only event log into state (pure, order independent); `events.py` reads and writes event files; `validate.py` is the privacy boundary and quarantine; `pendency.py`, `cli.py`, `hooks.py`, `sync.py` are the shell around them. The existing suite (131 tests) covers the fold, the CLI and the pendency rules well. Risks by cost of error: a secret or contact data entering memory (privacy boundary), an agent forging an entry that outranks the user's (event file format), a replaced entry staying active (fold). This review hunted in those three places. Observed: all tests were run. Inferred: the ranking.

## Test matrix (new file `tests/test_bughunt.py`, 13 tests)
| Rule | Scenario | Expected | Priority |
|---|---|---|---|
| no secrets in memory | classic and fine-grained GitHub tokens, GitLab token, Google API key, AWS key, private key header | flagged "secret" | high |
| no contact data | phone numbers in Brazilian, German, E.164 and US forms | flagged "phone number" | high |
| no false alarms | exam dates, versions, decimals, "+1 point", "11 91234 cards" | not flagged | medium |
| e-mail and CPF | one each | flagged | medium |
| fold: supersedes | a repeated ruling that also replaces another entry | the other entry is replaced | high |
| fold: forget | forget before or after delivery in any order; a short ref naming two events | forgotten; ambiguous ref forgets neither | medium |
| event file | render then parse of every field including a body with `---` | identical | high |
| event file | a newline inside a header value | cannot inject another header (`owner: user`) | high |
| event file | timestamps with Z, offset, date only | UTC | low |
| validation | body length boundary, one day ahead boundary, control events need target and signal | boundaries exact | medium |

## How to run
```
python3 -m unittest discover -s tests -t .       # everything (the gate does this)
python3 -m unittest tests.test_bughunt           # only this file
```

## Results (observed, 2026-10-24)
Before the fixes 8 of the 13 new tests failed (they cover the 4 defects below); after the fixes all 144 tests pass. A mutation tool for Python is not installed, so the failing-before / passing-after pairs are the evidence that the tests detect each defect.

## Coverage
Not measured (no `coverage` installed).

## Defects found (all fixed)
1. **Header injection in event files.** `render` wrote header values verbatim, so a value with a newline (a `target`, `key`, `category` or `supersedes` typed into the CLI) started another header line: `target: x\nowner: user` produced an entry owned by the user, and user-owned entries outrank the harvester. Impact: an agent could forge user authority. Fix: header values are collapsed to one line.
2. **Fine-grained GitHub tokens (`github_pat_`), GitLab tokens (`glpat-`) and Google API keys (`AIza`) were not recognised as secrets**, so they could be stored in memory. Impact: a secret in a repository that is private but shared by all instances. Fix: three patterns added.
3. **International phone numbers (`+49 151 ...`, `+4915...`, `+1 415 ...`) were not recognised as contact data**; only Brazilian shapes were. Impact: contact data about other people could be stored, against the rule. Fix: a pattern for `+` and at least nine digits.
4. **A repeated ruling lost its `supersedes`.** An event with the same key and words as the current one was hidden as "more evidence" before its `supersedes` was read, so the entries it declared replaced stayed active. Fix: apply them, except the entry it restates (an existing test requires that).

## Limitations and residual risks
The privacy scan is a list of patterns: an unknown token format or a name written in prose passes. The CLI, hooks and sync were not re-examined. Unformatted national numbers without separators (`11912345678`) and CPF without punctuation are not flagged on purpose (too many false alarms).

## Recommendations
1. Install `coverage` and `mutmut` to measure the suite.
2. Decide whether to keep a list of token prefixes in one place and review it twice a year.
3. Add a property test: render then parse is the identity for any header values without newlines.
