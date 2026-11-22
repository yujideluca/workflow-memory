"""Rule tags (ADR-0007, ADR-0008): rules are modules fetched by the kind of task, never printed at start-up.

A pref, decision or fact can carry tags (`tags: a, b`). The start-up output prints the router (the one standing
order: classify each message into tags, then load their rules) and an index "tag (n rules): use when ...".
The `always` tag is retired: nothing prints it, and `mem check` warns about a rule that still carries it. `mem rules TAG ...` prints the full, current wording of every active
rule that has any of the tags. Pure functions of the event log, like the rest of the fold.
"""
import re
import tomllib
from collections import Counter
from pathlib import Path

from . import core

TAGGED = ("pref", "decision", "fact")
MAX_TAGS = 6
ALWAYS = "always"
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
MAX_STARTUP = 1900   # characters printed before the open items (the harness shows only the first 2 KB)
LOAD = "run mem rules TAG [TAG ...]"
BRIEF_LEN = 160      # characters of a rule shown in a briefing line (ADR-0010); a shorter rule is shown whole
FULL = "mem rules --full KEY|#REF [...]"
BRIEFING_SENTENCE = ("It prints a briefing, one line per rule: for every rule "
                     f"that touches the task, {FULL} and follow the full wording.")
ROUTER = ("Rules are modules loaded by kind of task; none is printed here. Your one standing order: for each message "
          "from Giovanni, first classify the task into the tags below (several can apply, none when nothing fits) and "
          f"{LOAD} for every tag not loaded yet in this conversation. Do it as the very first step, before reading "
          f"skills or files and before any other command. {BRIEFING_SENTENCE} Classify again whenever the task "
          "changes. Tags:")
BRIEFING_NOTE = (f"Briefing only: a line with … before its #code is cut. Before acting, load every rule that touches "
                 f"this task in full: {FULL} (a tag name instead prints its whole module).")
HINT = ROUTER  # older name, kept for callers


def vocabulary():
    """tag -> its use-when line, from tags.toml."""
    data = tomllib.loads(Path(__file__).with_name("tags.toml").read_text(encoding="utf-8"))
    return {k: str(v).strip() for k, v in data.items()}


def of(e):
    return e.get("tags") or []


def problems(tags, kind):
    """Why a tag list is invalid for an event of this kind (empty list = fine)."""
    if not tags:
        return []
    why = [] if kind in TAGGED else [f"tags only apply to a pref, decision or fact, not a {kind}"]
    if len(tags) > MAX_TAGS:
        why.append(f"more than {MAX_TAGS} tags")
    vocab = vocabulary()
    for t in tags:
        if not TAG_RE.match(t):
            why.append(f"bad tag {t!r}")
        elif t not in vocab:
            why.append(f"unknown tag {t!r} (add a use-when line to mem/tags.toml)")
    return why


def visible(events, project=None, instance=None):
    """Active, taggable rules in this scope that nobody marked wrong."""
    state = core.resolve(events)
    wrong = core._feedback(events)
    return [e for e in state["active"]
            if e["type"] in TAGGED and core.in_scope(e, project, instance)
            and not wrong.get(e["id"], Counter())["wrong"]]


def rules(events, wanted, project=None, instance=None):
    """Every rule with any wanted tag, each once, ordered by key."""
    want = set(wanted)
    hit = [e for e in visible(events, project, instance) if want & set(of(e))]
    return sorted(hit, key=lambda e: (e.get("key") or "", e["id"]))


def select(events, names, project=None, instance=None):
    """Rules named by tag, key or #ref, each once, ordered by key; plus the names that matched nothing: (rules, unknown names, names of rules that exist outside this scope)."""
    pool, hit, unknown, outside = visible(events, project, instance), {}, [], []
    everywhere = {e["id"]: e for e in core.resolve(events)["active"] if e["type"] in TAGGED}
    for name in names:
        found = [e for e in pool if name in of(e) or e.get("key") == name or core.ref(e["id"]) == name.lstrip("#")]
        if not found and name not in vocabulary():
            there = [e for e in everywhere.values()
                     if e.get("key") == name or (name.lstrip("#") and core.ref(e["id"]) == name.lstrip("#"))]
            (outside if there and name.strip("#") else unknown).append(name)
        hit.update((e["id"], e) for e in found)
    return sorted(hit.values(), key=lambda e: (e.get("key") or "", e["id"])), unknown, outside


def brief(e):
    """One briefing line (ADR-0010): the whole rule when short, else its start, cut at a sentence or word end."""
    body = " ".join(e["body"].split())
    if len(body) > BRIEF_LEN:
        cut = body[:BRIEF_LEN]
        stop = max(cut.rfind(". "), cut.rfind(": "), cut.rfind("; "))
        if stop >= BRIEF_LEN // 2:
            body = cut[:stop + 1]
        else:                                # a body must never collapse to a word or two: cut at a word end
            word = cut.rsplit(" ", 1)[0]
            body = word if len(word) >= BRIEF_LEN // 2 else cut   # no usable word end: a hard cut
        body += " …"
    text = f"[{e['key']}] {body}" if e.get("key") else body
    return f"- {text} (#{core.ref(e['id'])})"


def untagged(events):
    """User-owned prefs that no tag reaches: an anti-goal, listed by `mem check` and the review view."""
    return [e for e in core.resolve(events)["active"]
            if e["type"] == "pref" and e["owner"] == "user" and not of(e)]


def warnings(events):
    n = len(untagged(events))
    return [f"{n} user-owned rule(s) have no tag (mem check lists them)"] if n else []


def index(events, project=None, instance=None):
    """[(tag, number of rules, use-when line)] for every tag with rules here, except always."""
    count = Counter(t for e in visible(events, project, instance) for t in set(of(e)))
    return [(t, count[t], line) for t, line in vocabulary().items() if t != ALWAYS and count[t]]


def render(e):
    return core._line(e, ids=True)


def names():
    """Every tag a rule may be routed to (the vocabulary without the retired `always`)."""
    return [t for t in vocabulary() if t != ALWAYS]


def tagged_always(events):
    """Active rules that still carry the retired `always` tag (ADR-0008): a `mem check` warning."""
    return [e for e in core.resolve(events)["active"] if e["type"] in TAGGED and ALWAYS in of(e)]


def startup(events, header, project=None, instance=None):
    """Lines of the start-up brief: the router, then the index. No rule body (ADR-0008)."""
    lines = [header, ROUTER]
    lines += [f"- {t} ({n}): {line}" for t, n, line in index(events, project, instance)]
    return lines + warnings(events)
