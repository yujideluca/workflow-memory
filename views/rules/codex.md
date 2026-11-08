# Rules tagged codex

Generated 2026-11-08 from 945 events. Do not edit: record changes as events.

work done by Codex

- [codex.usage-limit] 2026-11-08: the Codex account hit its usage limit after about 2.5M tokens in one night (finding-tag pilot, 10 parallel sessions); reset came hours later. Plan Codex jobs above a few million tokens with Giovanni first. (#7cd83f)
- [work.codex-back] Codex is live again (Giovanni 2026-11-06): run radiology steps C2-C5 with many parallel codex exec sessions, model gpt-6.1-sol wherever a Sonnet-class worker would be used; each session fresh --ephemeral under 250k tokens; heavy local jobs one at a time under flock /tmp/radiology-heavy.lock. (#4820c7)
- [work.requirement-ids] Requirement IDs are two capital letters, a dash and the next free number (AN-29). When a task for Codex or a subagent will add requirement rows, give it its IDs in the prompt: the next free numbers, a separate block per task when several run in parallel (V2 gets AN-29..31, C5 AN-32..35). Never invent sub-schemes like AN-V2-1 or C4-CLIN-1. A research report adds no requirement row. Lesson 2026-11-07: three parallel radiology tasks got AN-V2-*, AN-C5-*, C4-CLIN-* from my prompt; the pinned checker skipped them silently and V2 could not be pushed. pipeline-check v0.7.0 now refuses such IDs. (#f13b46)
