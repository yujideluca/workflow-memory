# ADR-0008: Rules are modules; the one standing order is to route each message to its tags

- **Status:** accepted
- **Date:** 2026-11-07
- **Type (ISO/IEC/IEEE 14764):** perfective
- **Decided by:** Giovanni (idea and owner) / built by Claude Code

## Context

ADR-0007 (2026-11-05) gave every rule tags: kinds of task such as `coding` or `git`. Start-up showed a short index, and `mem rules TAG` printed the full rules. Three things were still printed in every session:

- The `always` rules (language, who Giovanni is, privacy) were printed in full.
- `mem brief` was what the Remote Control assistant runs at the first message of each conversation. It still printed the old ranked list of about 40 rules.
- Nothing reminded a long session to load new rules when the task changed. In 141 recorded sessions the median session covered 3 topics.

A review on 2026-11-07 also found that the rules themselves had piled up: 95 active entries. Among them were 3 empty ones (text "..."), 2 contradictions, 2 wrong facts, expired or retired entries, and 8 overlapping "finish and prove" rules.

Giovanni's request: rules become modules of heuristics. The AI's only standing order is to classify each request into tags, so it knows which rules to engage. Then the modules for those tags make up the working philosophy of that session. He asked for a test with every level of Claude and Codex before the definitive implementation.

## Decision

1. **No rule body is printed at start-up.** The start-up text is the header, the **router**, the tag index, the how-to lines and the open items. The router says: "for each message, classify the task into the tags (several or none), and before acting, run `mem rules TAG ...` for every tag not loaded yet in this conversation; classify again whenever the task changes". The `always` tag is retired: nothing prints it, and `mem check` warns about a rule that still carries it. The test on the real log requires zero such rules.
2. **The prompt hook prints one line**, the router nudge with the tag names (at most 400 characters), for every non-empty prompt. This is the only change to the "prints nothing" prompt hook. Preference harvesting stays silent.
3. **`mem brief` prints the router**, the same as start-up, plus the open items. `mem brief --full` keeps the old ranked list for inspection.
4. **New tag `outward`**: acts others see or that cannot be undone (email, messages, purchases, publishing, deleting). `deploy` keeps only installs, releases and configuration.
5. **`mem add` refuses empty or placeholder text** ("...", "TODO", one letter). The old empty events stay in the log, forgotten; validation of old events is unchanged, so nothing is quarantined after the fact.
6. **Rule cleanup** (events of 2026-11-07, script in the change log row):
   - Forgotten:
     - the 3 empty rules;
     - the expired "no Codex for 36 h" rule;
     - an agent-guard decision;
     - two touchpad repair notes;
     - the token-diet changelog;
     - the 10-Haiku-workers decision, which contradicted "5 workers".
   - Merged:
     - `work.dedication` absorbs acceptance-evidence, verified-by, test-yourself and setup-end-to-end;
     - the new `work.autonomy` absorbs build-then-ask, act-on-ok, routine-autonomy and no-approval-bureaucracy;
     - `work.no-retired-refs` absorbs one-consistent-scope;
     - the two Telegram rules become one, as do the two stay-awake rules and the two plain-language rules.
   - Corrected: `host.nitro` (Kubuntu 26.04, Wayland) and `project.quizapp` (it has a GitHub remote).
   - Trimmed: the stale status copy in `matcher.analysis-status`.
   - Renamed: `work.web-no-own-version` to `quiz.web-standalone-release`, because the old name said the opposite of its text.

   Result: 95 to 75 entries, every user rule reachable by a tag, none tagged `always`.

## Alternatives considered

- **Keep a few `always` rules** (language, privacy). Rejected: Giovanni asked for routing to be the only standing order. The privacy rule now sits under `docs-memory` and `outward`, where it acts. Answering in the language of the message is now under `reporting`.
- **A hook that guesses the tags from the prompt text** (keywords). Rejected: it would be a second classifier to maintain, and it would be wrong on short phone messages. The model classifies better than a keyword list, and the nudge only reminds it.
- **Nudge only at start-up.** Rejected after the simulation: long sessions (the Remote Control assistant runs for days) change task without a new start-up.

## Simulation before rollout (2026-11-07)

`~/sim-router/scripts/sim.py`: 15 scenarios (13 single requests, 2 conversations that change task in the second message), 7 models (Claude Haiku, Sonnet, Opus and Fable 5.x; Codex gpt-6-luna low, gpt-6.1-terra medium, gpt-6.1-sol high), old memory (main before this change) and new memory (this change with the cleanup applied), each in a sandbox copy with its own git remote. A run counts as a hit when every required tag was loaded before the first action that is not `mem`.

Results:
- **Old memory:** 60/119 hits (50%). By model: Claude 12-14 of 17, Codex 2-4 of 17. The email and branch-deletion requests were never routed to the ask-first rule (0/7 each). The second message of a conversation that changes task was a hit 4/14 times.
- **New memory, first wording:** 105/119 (88%). Claude 16-17 of 17, Codex sol 16, luna 13, terra 9. Most Codex misses read a skill file first and loaded the rules second.
- **New memory, final wording** (adds "as the very first step, before reading skills or files"; Codex at all three levels plus Claude Haiku and Sonnet): 82/85 (96%). Two of the three misses are artefacts of the scorer: `command -v mem && mem rules ...` was counted as a non-mem action. The real miss is luna answering a German correction without loading `german`. Task-switch turns: 10/10. Opus and Fable were not re-run with the final wording (17/17 each with the first wording).
- **Cost:** the new memory loads more extra tags, mostly Codex (up to 24 extra tags in 17 runs). This costs context, not correctness.

Limit: `codex exec` runs only hooks marked trusted, so Codex received the same hook text placed before the message, not through a real hook.

## Consequences

- Start-up is shorter and has no rule body, so the 2 KB cut cannot hide one. Test `test_real_log_start_up_output_fits_the_harness_cut` also requires zero `always` rules.
- Every prompt costs about 300 characters of context (the nudge).
- A rule now reaches a session only if the model routes to its tag. A rule that matters everywhere must carry every tag where it acts; `mem check` keeps warning about untagged user rules.
- Tests: `Router` and `PlaceholderText` in `tests/test_tags.py`; updated start-up, brief and prompt-hook tests.
