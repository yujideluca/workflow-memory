# ADR-0007: Rules are fetched by the kind of task (rule tags)

- **Status:** accepted
- **Date:** 2026-11-05
- **Type (ISO/IEC/IEEE 14764):** corrective
- **Decided by:** Giovanni (idea and owner) / built by Claude Code


## 1. Intent and why
On 2026-11-04 agent-guard locked Giovanni's sessions. The rules that would have stopped it already existed but never reached the sessions: the start-up brief is about 18 KB, the harness shows only the first 2 KB, and pinned preferences print oldest first, so any rule added after a failure lands past the cut (evidence: `~/guard-incident-notes/ROOT-CAUSES.md`). In 24 of 25 sessions since 2026-11-03 only 11-12 of 56 rules were visible, and the visible ones leaned towards "act".

Giovanni's idea: tag every rule by the kind of task where it matters, show only a short index at start-up, and let Claude fetch the full rules for a task kind at the right moment, the way it loads a skill when the skill's description fits.

## 2. Goals
- A rule can carry several tags. A tag names a kind of task (deploy, troubleshooting, ...), not a topic.
- The start-up brief becomes small (under 1.5 KB, so the 2 KB cut never hides anything): the few `always` rules in full, then an index "tag: n rules, use when ...".
- `mem rules TAG [TAG ...]` prints the full, current wording of every active rule that has any of those tags, each rule once.
- Existing rules are all tagged in one migration (table in section 6); nothing is lost; `mem search` keeps working.
- Fully backwards compatible with the event log (append-only, idempotent, order independent: principles 1 and 3).

## 3. Non-goals
- NOT the forced safety net (a hook that injects rules when a risky action runs). Giovanni will set that up as the next step. This design only makes it possible: the hook will call `mem rules`.
- No change to rule wording in this step (the "perfect the rules" work is separate).
- No change to open items (pendencies), harvesting or sync.

## 4. Anti-goals (a failure even if it technically works)
- A rule that exists but can be reached by no tag and is not in the index. `mem check` must warn on any active, user-owned pref without a tag.
- An index that grows past the 2 KB cut again. A test must fail if the start-up output for the real log exceeds 2,000 characters before the open-items section.
- Claude having to guess tag names. The index lists every tag with a use-when line, generated from the data.

## 5. Decisions
Giovanni decided:
- Rules are tagged by task function; multiple tags per rule.
- Rules are fetched on demand, like skills. The forced hook is a later, separate step.
- Claude assigns the initial tags; Giovanni corrects the table.

My calls (mark as such, change freely):
1. Language: Python, standard library only, inside `mem/` (what the repo already uses).
2. Storage: a new optional `tags` field (list of lowercase words) on pref events; `mem add --tags a,b`; superseding keeps or replaces tags like any other field. Old events without the field stay valid.
3. A tag's use-when line lives in one small file `mem/tags.toml` (tag -> one-line description). Adding a tag without a line is a `mem check` error, so the index is never silently incomplete.
4. `always` is a tag: its rules are printed in full at start-up (language, who Giovanni is, no third-party data). Target at most 3 rules.
5. Scope rules stay as they are: a project-scoped rule only appears for that project, also through `mem rules`.
6. Harvester entries (`auto.*`) are not tagged and not in the index; they stay findable with `mem search`.
7. After /clear or compaction the same short brief is printed (no 110-character truncation needed any more).

## 6. Proposed tags (vocabulary and the full table to correct)
Vocabulary and use-when lines:
- `always`: printed in full at start-up.
- `deploy`: installing, releasing, changing system, Claude or tool configuration, anything outward-facing or destructive, rollbacks.
- `troubleshooting`: debugging, testing, fixing findings, proving that something works.
- `coding`: starting, designing or changing code, choosing tools and dependencies.
- `reporting`: how to answer, explain, report results and my own mistakes.
- `git`: branches, commits, repos, GitHub.
- `docs-memory`: wiki pages, memory entries, closing protocol.
- `device`: phone, adb, browser, Telegram.
- Domain tags: `quiz`, `radiology`, `german`, `status-quo`, `codex`.

Table (key -> tags):
- language.reply -> always, reporting
- person.profile -> always
- policy.third-party-data -> always, docs-memory
- work.verified-by -> reporting, troubleshooting, deploy
- work.acceptance-evidence -> troubleshooting, reporting, deploy
- work.setup-end-to-end -> deploy
- safety.ask-before-outward -> deploy
- work.routine-autonomy -> deploy, troubleshooting
- work.no-approval-bureaucracy -> deploy
- work.no-agent-guard -> deploy, coding
- release.promote, release.pool-promote, work.web-no-own-version -> deploy (+ quiz for the last two)
- work.test-yourself -> troubleshooting, coding, device
- work.fix-findings -> troubleshooting, coding
- work.troubleshoot-documentation -> troubleshooting, docs-memory
- work.test-ui-on-phone -> device, troubleshooting
- status-quo.e2e -> troubleshooting, status-quo
- work.build-then-ask, work.ask-language, work.ask-with-context, work.maintenance, work.shared-tools, work.avoid-fragile-deps, work.no-qwen, work.infer-from-pattern, work.encode-decisions, work.one-consistent-scope -> coding (ask-with-context also reporting; shared-tools and maintenance also git; encode-decisions also docs-memory)
- style.plain-language, style.explain-new-information, work.act-on-ok, style.phone (assistant instance) -> reporting
- git.no-force-push, work.single-branch, work.github-standard, work.document-commits, repos.public, repos.workflow-memory-unprotected -> git (no-force-push also deploy; workflow-memory-unprotected also docs-memory; document-commits is the commit-message rule)
- wiki.plain-language, wiki.complete-skill-content, wiki.coauthor-trailer, work.no-retired-refs, pendencies.verify-before-reminding -> docs-memory (coauthor-trailer also git)
- work.phone-stay-awake, work.phone-stay-awake-ac, telegram, browser.hang-refresh -> device
- quiz.spacing-rules, quiz.qa-process, web.follow-user-version (QuizApp and QuizWeb copies) -> quiz (+ troubleshooting, deploy, coding as fitting)
- matcher.*, radiology.* -> radiology (+ coding where it is about how to build)
- german.* -> german
- codex.* (codex instance) -> codex

## 7. What is left to the builder
- Exact event validation (tag characters, maximum tags per rule), the format of the index lines, and the `mem rules` output layout.
- Migration: one `mem add --supersedes` per rule is the append-only way; the builder may add a single `mem tag KEY TAG ...` command that writes those events.
- Tests (repo rule: stdlib unittest), the ADR, DESIGN.md, and the wiki page for `mem` in English, `.de`, `.pt-BR`.

## 8. Plan (done 2026-11-05)
All steps were carried out in this order: tests first, implementation, migration of the rules (section 6, applied with `mem tag`), full test suite and `pipeline-check`, DESIGN.md and wiki, commits in areas.

## 9. Answers to the builder check (added 2026-11-04)
Verified in the code: `core.resolve` (the "same ruling again" branch) hides an event whose normalized body equals the current one in the same (scope, key) slot and counts it as evidence. So a tags-only supersede would be dropped. Event `parse` reads named head fields; no check rejects an unknown head line (to be confirmed by a test).

Decided by Claude on 2026-11-05 (Giovanni: "the rule tags design is yours"):
- Q1: tags take part in the identical-ruling comparison in `resolve` (one small change, no new event type). An event with no `tags` line only restates; `tags: -` clears on purpose.

My calls:
- Q2: `mem add --supersedes X` without `--tags` copies the tags of X at write time. Nothing is computed at read time, so order independence is unaffected. `--tags ""` clears them on purpose.
- Q3: one scope for the size test: everything printed before the open-items section (header, `always` rules, index, the `mem rules` hint, warnings, and the four instruction lines moved up to sit before the open items) must be at most 1,900 characters on the real log. The goal in section 2 becomes the same number.
- Q4: `mem rules` takes `--project` and `--instance`; with no flags it derives the project from the working directory and uses the instance from the global `--instance` flag. Rules of other instances (`codex.*`) show only when that instance is asked for. The forced hook will pass both explicitly.
- Q5: the table is a first pass. The builder decides the fuzzy lines (the `+ ...` and wildcard entries) from the rule text and `mem check` lists anything left untagged; Giovanni reviews the final table before the migration is applied (step 4). The table covers every keyed rule I could see (about 55 of 56); the rest are harvester entries, which stay untagged on purpose.
- Q6: new head line `tags: a, b`. Compatibility with older readers is a test in step 2 (an old-format reader must not quarantine a tagged event). No version bump unless that test fails.

## Consequences (as built)

- Start-up output on the real log: about 1,700 characters (limit 1,900, test `test_real_log_start_up_output_fits_the_harness_cut`), down from about 17 KB. After `/clear` or compaction the output is identical, so the 110-character cut of ADR-0005 no longer exists.
- Facts and decisions are no longer printed at start-up; the ones that matter carry tags, the rest are one `mem search` away.
- `mem add` without `--tags` keeps the tags of the entry it replaces; `mem tag KEY TAG ...` changes them; `mem rules TAG ...` prints the full rules; `mem check` warns about any user-owned pref without a tag.
- The chat app (no shell) reads `views/BRIEF.md` (always rules and the index) and `views/rules/TAG.md`, both generated.
- Harvester entries stay untagged, except one rule Giovanni said in his own words (`auto.48f402a649`, "respect my pipeline").
- The forced safety net (a hook that injects rules when a risky action runs) is the next step and will call `mem rules`.
