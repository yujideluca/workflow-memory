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

PRIVACY = (
    ("secret", re.compile(
        r"gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_\-]{20,}|AKIA[0-9A-Z]{16}|"
        r"-----BEGIN [A-Z ]*PRIVATE KEY|\bbearer\s+[A-Za-z0-9._\-]{20,}|xox[baprs]-[A-Za-z0-9\-]{10,}",
        re.I)),
    ("email address", re.compile(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+")),
    ("phone number", re.compile(r"(?:\+\d{1,3}[\s.\-]?)?\(?\d{2}\)?[\s.\-]\d{4,5}[\s.\-]\d{4}")),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
)


def privacy_reasons(text):
    return [name for name, rx in PRIVACY if rx.search(text)]


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
            valid.append(e)
    return valid, invalid


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
