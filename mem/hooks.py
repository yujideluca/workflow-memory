"""Claude Code hooks. They must never fail loudly or print by accident:
UserPromptSubmit and SessionStart stdout goes into the model's context."""
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import core, events as ev, harvest, project, sync, validate

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


def session_start(root, payload, now, instance):
    """Print the brief for this project. Falls back to the last pulled state offline."""
    try:
        status = sync.pull(root)
        events, invalid = validate.load_checked(root, now)
        out = core.brief(events, [], now, project=_project(payload),
                         instance=instance, budget=project.BRIEF_BUDGET, ids=True)
        texts = project.build(root, now, instance)
        pending = project.review_count(texts)
        lines = ["Memory (workflow-memory). " + out["header"], *out["lines"]]
        if out["over_budget"]:
            lines.append(f"({len(out['over_budget'])} more entries did not fit: mem search \"words\").")
        if pending:
            lines.append(f"{pending} item(s) wait for Giovanni in views/REVIEW.md.")
        if core.open_items(events, _project(payload), instance):
            lines.append("Open items above are reminders, not facts. Before reminding Giovanni of one, run its "
                         "check and verify it still applies in this context: if it no longer does, close it "
                         "(mem done REF) and do not present it as pending; if you could not check it, say "
                         "'unchecked'. State how you verified.")
        if not status.startswith("pulled"):
            lines.append(f"(memory may be stale: {status})")
        lines += [
            "Record a correction or lasting preference from Giovanni: "
            f"python3 {root}/bin/mem add --type pref --owner user --key topic \"the rule\".",
            "When you finish a task, report which entries you used and how, briefly: "
            "mem use REF1,REF2 --note \"how\" (REF is the #code after an entry).",
            "Say an entry was wrong or outdated: mem feedback REF wrong|stale (or helpful|not_helpful).",
        ]
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
