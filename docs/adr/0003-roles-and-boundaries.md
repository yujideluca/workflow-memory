# ADR-0003: Roles of Giovanni and the Claude instances; workflow-memory is their only shared interface

- **Status:** accepted
- **Date:** 2026-10-22
- **Type (ISO/IEC/IEEE 14764):** preventive
- **Decided by:** Giovanni, from the maintenance and evolution review of 2026-10-22

## Context

Conway's law says a system's structure copies the structure of the people (here: the agents) who build it. With one
person and several Claude instances, each instance used to grow its own memory and its own protocol for talking to
the others, which is how the old gui-code-protocol became heavy. Team Topologies, the usual remedy in companies, is
about giving each team a clear responsibility and a narrow interface to the others.

## Decision

| Actor | Responsibility | Writes to |
|---|---|---|
| **Giovanni** (owner) | Decides what is built; approves anything outward-facing or destructive; says when a beta becomes stable | anything |
| **Claude Code on the laptop** (developer) | Builds, tests, documents and releases software in `~/dev/*`; keeps the projects' ADRs, CI and debt list | project repos, workflow-memory events |
| **Remote assistant** (`claude-assistant`, from the phone) | Short tasks on the laptop when Giovanni is away; same rules as Claude Code | same as Claude Code, `MEM_INSTANCE=assistant` |
| **Claude app** (claude.ai) | Conversation, writing, study (German, clinical questions) | workflow-memory events only, through the GitHub connector |

The instances never talk to each other directly. What one must know from another goes through workflow-memory
(preferences, facts, open items) or through the project repo itself (code, ADRs, issues). No new inter-instance
protocol, logbook or sync rule is added; a coordination need becomes an event type or a field instead.

Golden path: a new software project starts from `~/dev/project-template` (principles, ADRs, requirements, quality
gate, CI, maintenance checklist), so the right way is also the quick way.

## Alternatives considered

- **Per-instance memories and an explicit protocol** — what the old system did; retired.
- **No written roles** — the default until now; roles were implicit and re-explained in each session.

## Consequences

A monthly architecture review (an open item in workflow-memory) plays the role a staff engineer has in a company:
it checks coherence across projects with the checklist in `~/dev/project-template/docs/MAINTENANCE.md`.
