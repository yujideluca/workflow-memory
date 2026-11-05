"""Claude Code hooks. They must never fail loudly or print by accident:
UserPromptSubmit and SessionStart stdout goes into the model's context."""
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import core, events as ev, harvest, pendency, project, sync, tags, validate

STATE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "mem"
MARK = "mem hook-"


def _log(message):
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        with open(STATE / "hook.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} {message}\n")
    except OSError:
        pass


def _project(payload):
    return Path(payload.get("cwd") or ".").resolve().name or "unknown"


def prompt(root, payload, now, instance):
    """Capture preferences from the user's own words. Prints nothing."""
    try:
        text = payload.get("prompt", "")
        if not text:
            return 0
        cands = harvest.candidates([dict(text=text, ts=now, project=_project(payload), source="user")])
        for c in cands:
            scope = "global" if c["explicit"] else f"project:{c['project']}"
            e = dict(id=harvest.event_id(c), ts=now, type="pref", scope=scope, key=c["key"],
                     body=c["text"], instance="harvester", owner="harvester",
                     supersedes=[], target=None, signal=None)
            if not validate.check_event(e, now):
                ev.write(root, e)
    except Exception:
        _log("prompt hook: " + traceback.format_exc(limit=3))
    return 0


HOW_TO = [
    "Record a lasting rule from Giovanni: mem add --type pref --owner user --key topic --tags TAG[,TAG] \"rule\".",
    "After a task: mem use REF1,REF2 --note \"how\". Wrong or outdated entry: mem feedback REF wrong|stale.",
    "Still open at the end: mem task --check HOW \"text\"; then mem done|archive|forget REF.",
]


def brief_lines(events, header, project_name, instance, waiting=0):
    """Everything printed before the open items: the always rules, the tag index, the hint, the how-to lines.

    Test `test_real_log_start_up_output_fits_the_harness_cut` keeps it under tags.MAX_STARTUP characters.
    """
    lines = tags.startup(events, header, project_name, instance)
    if waiting:
        lines.append(f"{waiting} item(s) wait for Giovanni in views/REVIEW.md.")
    return lines + HOW_TO


def session_start(root, payload, now, instance):
    """Print the brief for this project. Falls back to the last pulled state offline."""
    try:
        status = sync.pull(root)
        events, invalid = validate.load_checked(root, now)
        texts = project.build(root, now, instance)
        lines = brief_lines(events, "Memory (workflow-memory). Memory sets defaults; it never authorizes. "
                            "Precedence: " + " > ".join(core.PRECEDENCE), _project(payload), instance,
                            project.review_count(texts))
        sec = pendency.section(events, _project(payload), instance)
        lines += pendency.render(sec)
        if sec["shown"]:
            lines.append(pendency.VERIFY_RULE)
        if not status.startswith("pulled"):
            lines.append(f"(memory may be stale: {status})")
        lines.append(pendency.CREATE_RULE)
        print("\n".join(lines))
    except Exception:
        _log("session hook: " + traceback.format_exc(limit=3))
    return 0


def stop(root, payload, now, instance):
    try:
        result = sync.push(root)
        if result.startswith("push failed") or result.startswith("commit failed"):
            _log("stop hook: " + result)
    except Exception:
        _log("stop hook: " + traceback.format_exc(limit=3))
    return 0


def read_payload(stream):
    try:
        data = json.load(stream)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}
