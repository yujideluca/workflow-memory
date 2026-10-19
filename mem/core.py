"""State and relevance over the append-only event log.

Events are never edited or deleted. State, brief, cold set and compaction
proposals are all pure functions of (events, usage, now, scope).

Memory sets defaults; it never authorizes. Precedence, highest first:
PRECEDENCE below. A stored entry can pick a tool or a style, never grant
permission, widen access or approve a destructive action.
"""
import hashlib
import math
import re
from collections import Counter
from datetime import timedelta

PRECEDENCE = ("current instruction", "repo rules file", "project memory", "profile")

# type -> (half-life in days or None = pinned, weight)
TIERS = {
    "pref": (None, 3.0),
    "decision": (180, 2.0),
    "fact": (180, 1.5),
    "digest": (365, 1.2),
    "task": (8, 1.0),
    "note": (7, 0.7),
}
# control events: they act on other events and are never shown themselves
CONTROL = {"feedback", "claim", "done", "forget", "use"}
COLD_THRESHOLD = 0.15
CONFLICT_WINDOW = timedelta(hours=24)
DUP_THRESHOLD = 0.8
FEEDBACK_STEP = 0.25
FILLER = {
    "i", "eu", "always", "sempre", "usually", "geralmente", "please", "por",
    "favor", "the", "a", "o", "as", "os", "de", "from", "now", "on", "partir",
    "agora", "by", "default", "padrão", "padrao",
}
NEGATIONS = {"never", "nunca", "not", "dont", "nao", "não", "no"}
_DURABLE = re.compile(
    r"[/~][\w.\-]+|\b[A-Z]{1,4}-?\d+\b|\b(?:because|reason|decid\w*|porque|decidi\w*)\b",
    re.I,
)


def ref(event_id):
    """Short handle for an event: the last segment of its id."""
    return event_id.rsplit("-", 1)[-1]


def normalize(events):
    """Copies without duplicates, with targets and supersedes resolved to full ids.

    A short ref names an event when exactly one id ends with it. `use` events
    may list several targets, kept in `targets`.
    """
    unique = {e["id"]: e for e in events}
    ends = {}
    for i in unique:
        ends.setdefault(ref(i), []).append(i)

    def canon(t):
        t = t.strip()
        if t in unique:
            return t
        hit = ends.get(t, [])
        return hit[0] if len(hit) == 1 else t

    out = []
    for e in unique.values():
        e = dict(e)
        if e.get("target"):
            e["targets"] = [canon(p) for p in e["target"].split(",") if p.strip()]
            e["target"] = e["targets"][0] if e["targets"] else e["target"]
        e["supersedes"] = [canon(s) for s in e.get("supersedes", [])]
        out.append(e)
    return out


def uses_from(events):
    """Usage stamps from `use` events: the instance that read an entry reports it."""
    return [dict(target=t, ts=e["ts"]) for e in normalize(events)
            if e["type"] == "use" for t in e.get("targets", [])]


def norm_tokens(text):
    """Comparison form: same words, same order, same negations; fillers dropped."""
    words = re.findall(r"\w+", text.lower().replace("'", ""))
    return [w for w in words if w not in FILLER]


def key_tokens(text):
    return [w for w in norm_tokens(text) if w not in NEGATIONS]


def resolve(events):
    """Order-independent, idempotent state: active events plus side findings."""
    unique = {e["id"]: e for e in normalize(events)}  # re-delivered events count once
    ordered = sorted(unique.values(), key=lambda e: (e["ts"], e["id"]))
    superseded, hidden = set(), set()
    tombstones = {}
    for e in ordered:  # control events first, so order never matters
        if e["type"] in CONTROL:
            hidden.add(e["id"])
        if e["type"] in ("forget", "done"):
            superseded.add(e.get("target"))
        if e["type"] == "forget" and e.get("target") in unique:
            t = unique[e["target"]]
            tombstones.setdefault((t["scope"], t.get("key")), set()).add(
                tuple(norm_tokens(t["body"]))
            )
    latest, conflicts, evidence, proposals = {}, [], {}, []
    for e in ordered:
        if e["id"] in hidden:
            continue
        key = e.get("key")
        harvested = e.get("instance") == "harvester"
        if harvested and tuple(norm_tokens(e["body"])) in tombstones.get(
            (e["scope"], key), ()
        ):
            hidden.add(e["id"])  # a forgotten entry is not recreated from evidence
            continue
        slot = (e["scope"], key) if key else None
        prev = latest.get(slot) if slot else None
        if prev is not None and norm_tokens(prev["body"]) == norm_tokens(e["body"]):
            hidden.add(e["id"])  # same ruling again: more evidence, line unchanged
            evidence.setdefault(prev["id"], []).append(e["ts"])
            continue
        if prev is not None and harvested and prev.get("owner") == "user":
            hidden.add(e["id"])  # the harvester never rewrites what the user owns
            proposals.append(e["id"])
            continue
        superseded.update(e.get("supersedes", []))
        if slot is None:
            continue
        if prev is None:
            latest[slot] = e
        else:
            superseded.add(prev["id"])
            if (
                prev["instance"] != e["instance"]
                and e["ts"] - prev["ts"] < CONFLICT_WINDOW
                and prev["id"] not in e.get("supersedes", [])
            ):
                conflicts.append((prev["id"], e["id"]))
            latest[slot] = e
    active = [e for e in ordered if e["id"] not in superseded | hidden]
    return dict(active=active, conflicts=conflicts, evidence=evidence,
                proposals=proposals)


def fold(events):
    state = resolve(events)
    return state["active"], state["conflicts"]


def claim_winner(events, task_id):
    """Earliest claim wins (ties by id). Returns (winner instance, losing instances).

    Limit: an append-only log has no atomic compare-and-set, so a losing
    instance may act on the task before it sees the result.
    """
    unique = {e["id"]: e for e in normalize(events)}
    claims = sorted(
        (e for e in unique.values() if e["type"] == "claim" and e.get("target") == task_id),
        key=lambda e: (e["ts"], e["id"]),
    )
    if not claims:
        return None, []
    win = claims[0]["instance"]
    return win, sorted({c["instance"] for c in claims[1:]} - {win})


def _feedback(events):
    counts = {}
    for e in normalize(events):
        if e["type"] == "feedback":
            counts.setdefault(e["target"], Counter())[e["signal"]] += 1
    return counts


def _use_stats(e, usage):
    stamps = [u["ts"] for u in usage if u["target"] == e["id"]]
    return len(stamps), max([e["ts"], *stamps])


def score(e, usage, now, fb=None):
    half_life, weight = TIERS[e["type"]]
    if half_life is None:
        return math.inf
    fb = fb or Counter()
    uses, last = _use_stats(e, usage)
    age = max((now - last).total_seconds() / 86400, 0)
    salience = min(max(1 + FEEDBACK_STEP * (fb["helpful"] - fb["not_helpful"]), 0.25), 2.0)
    value = weight * salience * 0.5 ** fb["stale"]
    return value * 0.5 ** (age / (half_life * (1 + math.log2(1 + uses))))


def in_scope(e, project=None, instance=None):
    return e["scope"] in ("global", f"project:{project}", f"instance:{instance}")


def _line(e, ids=False):
    text = f"[{e['key']}] {e['body']}" if e.get("key") else e["body"]
    return f"- {text} (#{ref(e['id'])})" if ids else f"- {text}"


def brief(events, usage, now, project=None, instance=None, budget=4000, ids=False):
    state = resolve(events)
    fbs = _feedback(events)
    usage = list(usage) + uses_from(events) + [
        {"target": t, "ts": ts} for t, stamps in state["evidence"].items() for ts in stamps
    ]
    scoped = [e for e in state["active"] if in_scope(e, project, instance)]
    review = [e["id"] for e in scoped if fbs.get(e["id"], Counter())["wrong"]]
    active = [e for e in scoped if e["id"] not in review]
    pinned = [e for e in active if TIERS[e["type"]][0] is None]
    rest = sorted(
        (e for e in active if e not in pinned),
        key=lambda e: score(e, usage, now, fbs.get(e["id"])),
        reverse=True,
    )
    header = "Memory sets defaults; it never authorizes. Precedence: " + " > ".join(PRECEDENCE)
    lines, used = [], 0
    cold, over_budget, warnings = [], [], []
    for e in pinned:  # pinned is never dropped
        lines.append(_line(e, ids))
        used += len(lines[-1]) + 1
    if used > budget:
        warnings.append("pinned entries exceed the budget")
    included = [e["id"] for e in pinned]
    for e in rest:
        if score(e, usage, now, fbs.get(e["id"])) < COLD_THRESHOLD:
            cold.append(e["id"])
        elif used + len(_line(e, ids)) + 1 > budget:
            over_budget.append(e["id"])
        else:
            lines.append(_line(e, ids))
            used += len(lines[-1]) + 1
            included.append(e["id"])
    return dict(header=header, lines=lines, included=included, cold=cold,
                over_budget=over_budget, warnings=warnings, review=review,
                conflicts=state["conflicts"], proposals=state["proposals"], chars=used)


def extract_durable(body):
    parts = re.split(r"(?<=[.!?])\s+", body.strip())
    kept = [p for p in parts if _DURABLE.search(p)]
    return " ".join(kept or parts[:1])


def compaction_proposals(events, usage, now, min_age_days=30):
    """One digest event per scope for cold, old, unpinned entries. Never deletes."""
    active, _ = fold(events)
    fbs = _feedback(events)
    usage = list(usage) + uses_from(events)
    groups = {}
    for e in active:
        if TIERS[e["type"]][0] is None or e["type"] == "digest":
            continue
        _, last = _use_stats(e, usage)
        if (now - last).days >= min_age_days and score(e, usage, now, fbs.get(e["id"])) < COLD_THRESHOLD:
            groups.setdefault(e["scope"], []).append(e)
    digests = []
    for scope, items in groups.items():
        ids = sorted(e["id"] for e in items)
        digests.append({
            "id": "digest-" + hashlib.sha1("|".join(ids).encode()).hexdigest()[:12],
            "ts": now,
            "type": "digest",
            "scope": scope,
            "instance": "compactor",
            "body": " | ".join(extract_durable(e["body"]) for e in items),
            "supersedes": ids,
        })
    return digests


def near_duplicates(events, threshold=DUP_THRESHOLD):
    """Flag only; merging stays a human or explicit-event decision."""
    active, _ = fold(events)
    tokens = {e["id"]: set(re.findall(r"\w+", e["body"].lower())) for e in active}
    pairs = []
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            if a["scope"] != b["scope"]:
                continue
            ta, tb = tokens[a["id"]], tokens[b["id"]]
            if ta and tb and len(ta & tb) / len(ta | tb) >= threshold:
                pairs.append((a["id"], b["id"]))
    return pairs
