"""Event files: one markdown file per event, never edited, never deleted.

A file is `---`, `key: value` lines, `---`, then the text. Unknown keys are
ignored, so the format can grow without breaking old readers.
"""
import os
import re
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TYPES = ("pref", "fact", "decision", "task", "note", "digest",
         "feedback", "claim", "done", "forget", "use", "archive", "reopen", "rescope")
SIGNALS = ("helpful", "not_helpful", "stale", "wrong")
_STEM = re.compile(r"^(\d{8}T\d{6}Z)-([a-z0-9_]+)-")


def parse_ts(text):
    text = text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def parse(text, stem):
    """Return the event dict for a file; raise ValueError when it is unreadable."""
    m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", text, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    head = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        k, sep, v = line.partition(":")
        if not sep:
            raise ValueError(f"bad frontmatter line: {line!r}")
        head[k.strip().lower()] = v.strip()
    named = _STEM.match(stem)
    ts = head.get("ts") or (named.group(1) if named else "")
    if not ts:
        raise ValueError("missing ts")
    try:
        when = parse_ts(ts if "-" in ts else datetime.strptime(ts, "%Y%m%dT%H%M%SZ").isoformat())
    except ValueError:
        raise ValueError(f"bad ts: {ts!r}") from None
    return dict(
        id=stem, ts=when, type=head.get("type", ""), scope=head.get("scope", "global"),
        key=head.get("key") or None, body=m.group(2).strip(),
        instance=head.get("instance") or (named.group(2) if named else "unknown"),
        owner=head.get("owner", "agent"),
        supersedes=[s.strip() for s in head.get("supersedes", "").split(",") if s.strip()],
        target=head.get("target") or None, signal=head.get("signal") or None,
        category=head.get("category") or None,
    )


def render(e):
    def one_line(value):
        # A newline inside a header value would start another header line (for example `owner: user`).
        return " ".join(str(value).split())

    head = [f"type: {one_line(e['type'])}", f"scope: {one_line(e.get('scope', 'global'))}"]
    for name in ("key", "instance", "owner", "target", "signal", "category"):
        if e.get(name):
            head.append(f"{name}: {one_line(e[name])}")
    if e.get("supersedes"):
        head.append("supersedes: " + ", ".join(one_line(s) for s in e["supersedes"]))
    head.append("ts: " + e["ts"].strftime("%Y-%m-%dT%H:%M:%SZ"))
    return "---\n" + "\n".join(head) + "\n---\n" + e.get("body", "").strip() + "\n"


def new_id(now, instance):
    return f"{now:%Y%m%dT%H%M%SZ}-{instance}-{secrets.token_hex(3)}"


def path_for(root, e):
    return Path(root) / "events" / f"{e['ts']:%Y}" / f"{e['ts']:%m}" / f"{e['id']}.md"


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def write(root, e):
    """Write an event once. An existing file with the same id is left alone."""
    path = path_for(root, e)
    if not path.exists():
        atomic_write(path, render(e))
    return path


def load(root):
    """(events, unreadable) where unreadable is [(relative path, reason)]."""
    root, events, bad = Path(root), [], []
    for path in sorted((root / "events").rglob("*.md")):
        try:
            e = parse(path.read_text(encoding="utf-8"), path.stem)
            e["path"] = str(path.relative_to(root))
            events.append(e)
        except (ValueError, UnicodeDecodeError) as err:
            bad.append((str(path.relative_to(root)), str(err)))
    return events, bad
