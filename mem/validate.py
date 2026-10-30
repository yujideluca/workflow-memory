"""Validation and the privacy boundary. Enforced in the repo, whoever the writer is."""
import re
import shutil
from datetime import timedelta
from pathlib import Path

from . import events as ev

MAX_BODY = 1200
OWNERS = ("user", "agent", "harvester", "migration", "compactor", "action")
_SCOPE = re.compile(r"^(global|project:[\w.\-]+|instance:[a-z0-9_]+)$")
_KEY = re.compile(r"^[a-z0-9][a-z0-9._\-]*$")
_INSTANCE = re.compile(r"^[a-z0-9_]+$")
NEEDS_TARGET = ("feedback", "claim", "done", "forget", "use", "archive", "reopen")
MAX_USE_NOTE = 200


def _load_privacy():
    """kind -> compiled patterns, from privacy-patterns.tsv (the one list, shared with the wiki)."""
    names = {"secret": "secret", "phone": "phone number", "cpf": "CPF"}
    by_kind = {}
    for line in Path(__file__).with_name("privacy-patterns.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        kind, flags, _what, regex = line.split("\t")
        by_kind.setdefault(names[kind], []).append(re.compile(regex, re.I if flags == "i" else 0))
    return by_kind


PRIVACY_BY_KIND = _load_privacy()
_EMAIL = re.compile(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+")


def privacy_reasons(text):
    hit = {name for name, rxs in PRIVACY_BY_KIND.items() if any(rx.search(text) for rx in rxs)}
    if _EMAIL.search(text):
        hit.add("email address")
    return [name for name in ("secret", "email address", "phone number", "CPF") if name in hit]


def check_event(e, now):
    why = []
    if e["type"] not in ev.TYPES:
        why.append(f"unknown type {e['type']!r}")
    if not _SCOPE.match(e["scope"]):
        why.append(f"bad scope {e['scope']!r}")
    if e["key"] and not _KEY.match(e["key"]):
        why.append(f"bad key {e['key']!r}")
    if not _INSTANCE.match(e["instance"]):
        why.append(f"bad instance {e['instance']!r}")
    if e["owner"] not in OWNERS:
        why.append(f"unknown owner {e['owner']!r}")
    if e["type"] not in ev.TYPES[6:] and not e["body"]:
        why.append("empty text")
    if len(e["body"]) > MAX_BODY:
        why.append(f"text longer than {MAX_BODY} characters")
    if e["type"] == "use" and len(e["body"]) > MAX_USE_NOTE:
        why.append(f"use note longer than {MAX_USE_NOTE} characters")
    if e["type"] in NEEDS_TARGET and not e["target"]:
        why.append(f"{e['type']} needs a target")
    if e["type"] == "feedback" and e["signal"] not in ev.SIGNALS:
        why.append(f"feedback needs a signal in {ev.SIGNALS}")
    if e.get("category"):
        if e["type"] not in ("task", "rescope"):
            why.append("category only applies to a task or a rescope")
        elif not _KEY.match(e["category"]):
            why.append(f"bad category {e['category']!r}")
    if e["type"] == "rescope" and not (e["target"] or e.get("category")):
        why.append("rescope needs a target or a category")
    if e["ts"] > now + timedelta(days=1):
        why.append("timestamp is in the future")
    why += [f"contains {name}" for name in privacy_reasons(" ".join([e["body"], e["key"] or ""]))]
    return why


def load_checked(root, now):
    """(valid events, invalid) where invalid is [(relative path, [reasons])]."""
    events, bad = ev.load(root)
    invalid = [(path, [reason]) for path, reason in bad]
    valid = []
    for e in events:
        reasons = check_event(e, now)
        if reasons:
            invalid.append((e["path"], reasons))
        else:
            valid.append(clamp_to_now(e, now))
    return valid, invalid


def clamp_to_now(e, now):
    """No event can be later than the moment it is read (ADR-0006).

    A writer without a trusted clock (the chat app guesses the time) can stamp an event a few minutes ahead. Order
    follows the clamped time, so that event cannot sort after one really written later. The claimed time stays in
    `ts_claimed`. The result depends only on the event and `now`, so a build with `--now` is still reproducible.
    """
    if e["ts"] <= now:
        return e
    return dict(e, ts=now, ts_claimed=e["ts"])


def quarantine(root, now):
    """Move invalid event files to quarantine/ with a .reason note. Returns the moves."""
    root, moved = Path(root), []
    _, invalid = load_checked(root, now)
    for rel, reasons in invalid:
        src = root / rel
        if not src.exists():
            continue
        dest = root / "quarantine" / src.name
        shutil.move(str(src), str(dest))
        ev.atomic_write(dest.with_suffix(".reason"), "; ".join(reasons) + "\n")
        moved.append((rel, reasons))
    return moved
