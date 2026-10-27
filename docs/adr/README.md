# Architecture decision records

One short file per structural decision (format: [MADR](https://adr.github.io/madr/), trimmed; template
`0000-template.md`). `docs/DESIGN.md` describes how the system works now; an ADR says why, what was rejected and
what must stay true. An accepted ADR is never rewritten: a new decision supersedes it.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Record architecture decisions as ADRs | accepted |
| [0002](0002-event-log.md) | One append-only event log folded by a pure function, instead of a protocol | accepted (reconstructed) |
| [0003](0003-roles-and-boundaries.md) | Roles of Giovanni and the Claude instances; workflow-memory is their only shared interface | accepted |
| [0004](0004-program-measures-skill-judges.md) | A program measures and blocks, a skill judges and proposes | accepted |
| [0005](0005-trim-startup-brief.md) | Trim the startup brief and split memory by tool | accepted |
| [0006](0006-clock-skew.md) | An event can never be later than the moment it is read | accepted |
