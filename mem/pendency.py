"""Open items (pendencies): what is still open, kept in front of Giovanni until it is dealt with.

It is its own memory flow with its own budget; nothing else in the brief competes with it. An open item is a
`task` event whose text is `what is open | check: how to verify it still applies`, with an optional category.

Lifecycle (nothing lapses by itself; the item is shown in every chat until Giovanni decides):
* solved   -> `done`     closes it for good.
* parked   -> `archive`  hides it from every notification but keeps it, listed and searchable; `reopen`
                         brings it back "when it becomes a problem".
* deleted  -> `forget`   hides it from every view and from search (the file stays in the append-only log).
* checked  -> `use`      records when and how it was last verified; it changes nothing else.

Scope: an item is shown everywhere (any project, any chat) unless Giovanni says it depends on a scope. Then a
`rescope` event moves one item (`target`) or a whole category (`category`, present and future items) to that
scope; the latest applicable rescope wins (by timestamp; a tie is settled by event id, so two marks in the same
second are arbitrary), and rescoping to `global` undoes it. `archive` and `reopen` follow the same rule.

Budget: 2,000 tokens, separate from the entry budget (core.brief ignores tasks).
"""
from . import core

BUDGET_TOKENS = 2000
CHARS_PER_TOKEN = 3.6               # the same assumption as the brief budget (scripts/calibrate.py)
BUDGET_CHARS = int(BUDGET_TOKENS * CHARS_PER_TOKEN)
MAX_LINE = 500                      # one item never takes more than this many characters
CHECK_MARK = "| check:"
HEADING = "Open items (shown in every chat until solved, archived or deleted)"
VERIFY_RULE = ("Open items are reminders, not facts. Before reminding Giovanni of one, run its check and verify "
               "it still applies in this context: if not, close it (mem done REF) and do not present it as "
               "pending; if you could not check it, say 'unchecked'. Record a check with mem use REF --note HOW.")
CREATE_RULE = ("Before a session ends, record what is still open: mem task --check HOW [--category C] \"text\". "
               "Solved: mem done REF. Park: mem archive REF (mem reopen REF). Unneeded: mem forget REF. Open items "
               "show in every chat; make one project-specific (mem scope project:X REF, or --category C) only "
               "when Giovanni says so.")


def items(events):
    """Every open or archived item, each as {event, scope, category, since, checked, last, archived}.

    Solved and deleted items are gone. `scope` is the effective one, after any rescope.
    """
    active = [e for e in core.fold(events)[0] if e["type"] == "task"]
    marks, checks, moves = {}, {}, []
    for e in sorted(core.normalize(events), key=lambda x: (x["ts"], x["id"])):
        if e["type"] in ("archive", "reopen"):
            for t in e.get("targets", []):
                marks[t] = e["type"]                       # the latest of the two wins
        elif e["type"] == "use":
            for t in e.get("targets", []):
                checks[t] = e["ts"]
        elif e["type"] == "rescope":
            moves.append(e)
    out = []
    for t in active:
        scope = t["scope"]
        for m in moves:                                    # chronological: the latest applicable wins
            if t["id"] in m.get("targets", []) or (m.get("category") and m["category"] == t.get("category")):
                scope = m["scope"]
        checked = checks.get(t["id"])
        out.append(dict(event=t, scope=scope, category=t.get("category"), since=t["ts"], checked=checked,
                        last=max(t["ts"], checked or t["ts"]), archived=marks.get(t["id"]) == "archive"))
    return sorted(out, key=lambda i: (i["last"], i["event"]["id"]), reverse=True)


def visible(item, project=None, instance=None):
    return core.in_scope({"scope": item["scope"]}, project, instance)


def _tag(item):
    parts = ["open item"]
    if item["category"]:
        parts.append(item["category"])
    if item["scope"] != "global":
        parts.append(item["scope"])
    return "[" + " ".join(parts) + "]"


def _line(item):
    e = item["event"]
    body = " ".join(e["body"].split())
    flags = " (no check recorded)" if CHECK_MARK not in body else ""
    room = MAX_LINE - len(flags)
    if len(body) > room:
        body = body[:room - 1] + "…"
    when = f"since {item['since']:%Y-%m-%d}"
    if item["checked"]:
        when += f", checked {item['checked']:%Y-%m-%d}"
    return f"- {_tag(item)} {body}{flags} ({when}, #{core.ref(e['id'])})"


def section(events, project=None, instance=None, budget=BUDGET_CHARS):
    """The open items to show here, within `budget` characters, plus what did not fit."""
    shown_here = [i for i in items(events) if not i["archived"] and visible(i, project, instance)]
    lines, used, hidden = [], 0, 0
    for i in shown_here:                                   # most recently active first
        line = _line(i)
        if used + len(line) + 1 > budget:
            hidden += 1
            continue
        lines.append(line)
        used += len(line) + 1
    warnings = []
    if hidden:
        warnings.append(f"open items exceed the {budget}-character budget: {hidden} not shown "
                        "(solve them with mem done, park them with mem archive, or delete them with mem forget)")
    unchecked = [core.ref(i["event"]["id"]) for i in shown_here if CHECK_MARK not in i["event"]["body"]]
    if unchecked:
        warnings.append("open items without a check line: " + ", ".join("#" + r for r in unchecked))
    return dict(lines=lines, shown=len(lines), hidden=hidden, chars=used, warnings=warnings)


def render(sec):
    """Printable lines for a section; empty when there is nothing to say."""
    if not sec["lines"] and not sec["hidden"]:
        return []
    out = [HEADING + ":", *sec["lines"]]
    if sec["hidden"]:
        out.append(f"({sec['hidden']} more open item(s) did not fit: mem pending)")
    return out
