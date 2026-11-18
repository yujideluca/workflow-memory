# ADR-0009: Private entries are encrypted in a public repository

- **Status:** accepted
- **Date:** 2026-11-18
- **Type (ISO/IEC/IEEE 14764):** corrective
- **Decided by:** Giovanni ("leave it open and make private data encrypted") / built by Claude Code

## Context

This repository is public (since 2026-10-25, so that GitHub's free plan runs its CI without a minute limit). Open items, the reminders of unfinished work, are written in full sentences and had come to hold Giovanni's own private matters: names of people he deals with, amounts, mail thread numbers. An audit on 2026-11-18 found 16 event files and one view with such names, readable by anyone. Making the repository private was the first idea; it was dropped because every Stop hook pushes here (about 690 CI runs a month) and a private repository pays for CI minutes.

## Decision

1. **Private kinds.** `mem.json` lists the kinds of entry whose text is private: `"seal": ["task", "use", "note"]` (open items, the notes of `mem use`, notes). Rules (`pref`, `fact`, `decision`) stay readable: the chat app and the CI job need their text, and a rule is about how to work, not about a person.
2. **Format.** A private entry is an ordinary event file with one more header line, `sealed: v1`, and its text replaced by a Fernet token (AES-128-CBC with an HMAC-SHA256 signature, from the Python package `cryptography`). Headers (kind, scope, target, time) stay readable, because the CI job needs them to compute state.
3. **Key.** One key file, `~/.config/mem/key` (mode 600), made once by `mem key init` and never stored in any repository. `mem key status` says whether it works and how many entries it cannot read.
4. **Readers without the key** (the CI job, the chat app, a fresh clone) get the fixed text `MASK` in place of the private text. The entry stays valid, keeps its place in the state, and is counted.
5. **Nothing private is written back.** `views/` is always built from the masked entries, with or without the key, so the laptop and the CI job produce the same files. A private entry is never copied into a digest and never compared for near-duplicates. A private entry cannot have a `key:` header, because entries with a key are compared by their text.
6. **No silent fallback.** Where a kind is private and the key (or the package) is missing, `mem` refuses to write the entry instead of writing it in plain text.

## Consequences

- `mem/` was standard library only. `cryptography` is now the one exception, imported only when a key file exists. The CI job does not install it and does not need it; the job `gate` installs it so the tests of this feature run there.
- The chat app no longer sees the text of open items, only that they exist. It can still write one through the GitHub connector, in plain text: `views/BRIEF.md` tells it to put nothing private there.
- Losing the key loses the private texts. The key needs a copy outside the laptop.
- Entries written before this decision stay in plain text in the files and in the git history until the history is rewritten, which needs a forced push and is Giovanni's decision.
- Encryption hides the text, not the fact: file names, times and kinds stay public.

## Alternatives

- **Private repository:** simplest, but CI minutes (see Context).
- **Encrypt every file with a git filter (git-crypt):** the CI job would need the key as a GitHub secret, and the chat app could read nothing at all, rules included.
- **Remove the names by hand:** leaves the next open item just as exposed.
