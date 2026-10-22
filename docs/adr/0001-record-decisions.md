# ADR-0001: Record architecture decisions as ADRs

- **Status:** accepted
- **Date:** 2026-10-22
- **Type (ISO/IEC/IEEE 14764):** preventive
- **Decided by:** Giovanni, from the maintenance and evolution review of 2026-10-22

## Context

The previous system (claude-workflow-backup, gui-code-protocol v2.3-v2.8) recorded its decisions in logbooks,
handoff notes and memory files. When the repo was retired, the reasons went with it: memories still pointed at
files that no longer existed.

## Decision

Structural decisions about this repo get an ADR in `docs/adr/`, in the same commit as the change. `docs/DESIGN.md`
keeps describing the current state. The same format is used in every project (`~/dev/project-template`).

## Alternatives considered

- **Decisions as memory events** — events are for preferences and facts that steer a chat, with a 1 200-character
  limit; a decision with alternatives does not fit, and the brief would grow.

## Consequences

Each structural change carries a short extra file. The monthly architecture review checks for missing ones.
