# ADR-0010: Every memory output is a briefing first; the full text is fetched on demand

- **Status:** accepted
- **Date:** 2026-11-22
- **Type (ISO/IEC/IEEE 14764):** perfective
- **Decided by:** Giovanni (owner: "all context sources get a briefing") / built by Claude Code

## Context

A token is the unit a language model reads and writes text in (about four characters). The context is everything
the model re-reads at every step of a session: instructions, rules, the conversation so far, files it opened.

Giovanni asked why token use stayed very high although saving context had been decided twice (ADR-0005 on
2026-10-26, ADR-0008 on 2026-11-07). A measurement of the session logs of 2026-11-08 to 2026-11-22
(21,788 model calls, tool `token-thrift report`) gave the answer:

- The average call carried 149,000 tokens of context; 86 % of the cost sat in calls above 100,000 tokens.
- 39 % of the cost was spent by subagents (helper sessions the main session starts), most of it on the two most
  expensive models.
- 14.5 % was spent re-storing a large context after a pause longer than the cache lifetime of about one hour.
- The start-up brief, the thing both earlier decisions trimmed, is about 2,500 tokens: under 2 % of an average call.

Root cause: both earlier efforts measured only the size of the start-up text, never the total, so they optimised
the smallest part; and the decisions that touch the large parts (cheaper models for helpers, shorter sessions)
existed only as sentences for the model to remember, not as settings or programs. Nothing reported the total, so
nobody saw that the cuts changed almost nothing.

Inside the memory itself two outputs were still printed whole:

- `mem rules TAG` printed every rule of a tag in full (5,600 to 12,500 characters per tag, 31,000 for
  `radiology`), although a task touches only a few of them.
- Each open item took up to 500 characters at start-up, after `/clear` and after every compaction.

## Decision

1. `mem rules TAG ...` prints a **briefing**: one line per rule (`[key] text (#ref)`). A rule up to 160 characters is
   shown whole; a longer one is cut at a sentence or word end and ends in `…`. A closing note tells the model to load
   in full every rule that touches the task.
2. `mem rules --full NAME ...` prints the full wording; NAME is a tag, a rule key or a `#ref`.
3. The router text orders both steps: load the briefing of each tag, then the full wording of the rules that apply.
4. Open items at start-up are a briefing too: the text up to 200 characters, without the check; the budget is
   1,000 tokens (was 2,000). `mem pending` prints every item whole, with its check.

## Alternatives considered

- **Keep full rules, drop tags per project.** Rejected: a session in the home folder serves every project.
- **Let a program pick the rules by keywords in the request.** Rejected again (see ADR-0008): a second classifier to
  maintain; the model reads the request better than a keyword list.
- **Cut every rule to 110 characters as after `/clear` (ADR-0005).** Rejected: too short for most first sentences;
  160 keeps the promise of a rule readable.

## Consequences

- Measured on the real log, 2026-11-22: `coding` 12,491 to 4,861 characters, `deploy` 8,988 to 3,432, `reporting`
  5,591 to 2,152, `docs-memory` 8,633 to 3,897, `radiology` 31,212 to 13,984; start-up output 9,458 to 6,115.
- A rule now acts only if the model loads it after reading its line, so **a rule must state its promise in its first
  sentence**. A rule cut before its point is a defect of the rule: rewrite its start.
- One more command per task (`mem rules --full ...`) when rules apply.
- This change is small against the total (the rules of a session are about 5 % of an average call). The large parts
  are handled outside this repository: session length and helper models by Claude Code settings, and the total is
  reported by `token-thrift report`, so the effect of any saving is checked against the whole.
- Tests: `Briefing` in `tests/test_tags.py`; `test_start_up_line_is_a_briefing_without_the_check` and
  `test_budget_is_1000_tokens` in `tests/test_pendency.py`.

## Corrections after review (2026-11-22)

- The chat app has no shell and reads `views/rules/TAG.md`, which holds the full wording. `views/BRIEF.md` therefore
  replaces both parts of the router text (`tags.LOAD` and `tags.BRIEFING_SENTENCE`): the app is told the file holds
  the full wording and to follow it, never that it prints a briefing or to run `mem rules`.
- A briefing body never collapses: when the only sentence end lies before 80 characters, the cut is at the last
  word end before 160; a body with no space is cut hard at 160. The closing note says "a line with … before its
  #code is cut", which is what the lines show.
- A rule key or `#ref` that exists outside the current project or instance is refused as "out of scope here", apart
  from names that match nothing.
- The 1,000-token budget of open items covers the whole printed section (heading, items, the "did not fit" line and
  the two standing rules), not only the item lines. An item that is only a check shows the check in the briefing;
  a room under 20 characters is raised to 20.
- Tests: `test_the_app_brief_says_the_file_holds_the_full_wording`, `test_the_whole_printed_section_is_within_the_budget`
  and the other new `Briefing` and `Budget` tests.
