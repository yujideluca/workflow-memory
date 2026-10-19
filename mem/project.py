"""Projections: every file in views/ is generated from the log and never edited by hand."""
import json
from collections import Counter
from pathlib import Path

from . import core, events as ev, validate

BRIEF_BUDGET = 3000
CONFIG = "mem.json"


def config(root):
    try:
        return json.loads((Path(root) / CONFIG).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _howto(root):
    repo = config(root).get("repo", "<owner>/<repo>")
    return f"""## Recording a correction or a lasting preference

When the user corrects you or states a rule that should last, record it. Load the
GitHub tools first (`get_file_contents`, `create_branch`, `create_or_update_file`),
then create ONE new file on `main` of `{repo}`. Never edit an existing file.

path: `events/YYYY/MM/YYYYMMDDTHHMMSSZ-app-xxxxxx.md` (UTC time, xxxxxx = 6 random letters or digits)

```
---
type: pref
scope: global
key: short.topic.name
owner: user
instance: app
ts: 2026-01-31T12:00:00Z
---
The rule, in the user's own words, one or two sentences.
```

`type` is pref, fact, decision or task. A new pref with the same `key` replaces the old one.
Never write secrets, contact data or health information about anyone: such files are quarantined.
"""


def build(root, now, instance="app", budget=BRIEF_BUDGET):
    """Return {view name: text}. Pure given the files and `now`."""
    events, invalid = validate.load_checked(root, now)
    usage = ev.load_usage(root)
    state = core.resolve(events)
    out = core.brief(events, usage, now, instance=instance, budget=budget)
    stamp = f"Generated {now:%Y-%m-%d} from {len(events)} events. Do not edit: record changes as events."
    brief = "\n".join([
        "# Memory brief", "", stamp, "", out["header"], "", *out["lines"],
        *([f"- ({len(out['over_budget'])} more entries did not fit; they are in the log and searchable)"]
          if out["over_budget"] else []),
        "", _howto(root),
    ])
    prefs = ["# Preferences in force", "", stamp, ""]
    by_id = {e["id"]: e for e in state["active"]}
    for e in state["active"]:
        if e["type"] != "pref":
            continue
        n = len(state["evidence"].get(e["id"], []))
        prefs.append(f"- [{e['scope']}] {e.get('key') or '-'}: {e['body']}"
                     + (f" (restated {n}x)" if n else "") + f" ({e['owner']})")
    fbs = core._feedback(events)
    review = [("Quarantined events (invalid or private)", [f"{p}: {'; '.join(r)}" for p, r in invalid]),
              ("Conflicting rulings (two writers, same key, same day)",
               [f"{a} vs {b}" for a, b in state["conflicts"]]),
              ("Harvester proposals that would change a user-owned entry",
               [f"{pid}: {by_id.get(pid, {}).get('body', '')}" for pid in state["proposals"]]),
              ("Entries marked wrong (hidden from the brief)",
               [f"{e['id']}: {e['body']}" for e in state["active"]
                if fbs.get(e["id"], Counter())["wrong"]]),
              ("Near-duplicate entries",
               [f"{a} ~ {b}" for a, b in core.near_duplicates(events)]),
              ("Cold entries ready to compact (run `mem compact --apply`)",
               [d["body"][:100] for d in core.compaction_proposals(events, usage, now)]),
              ("Warnings", out["warnings"])]
    lines = ["# Needs a decision", "", stamp, ""]
    shown = [(title, items) for title, items in review if items]
    for title, items in shown:
        lines += [f"## {title}", *[f"- {i}" for i in items], ""]
    if not shown:
        lines.append("Nothing needs a decision.")
    return {"BRIEF.md": brief + "\n", "PREFERENCES.md": "\n".join(prefs) + "\n",
            "REVIEW.md": "\n".join(lines) + "\n"}


def review_count(texts):
    return sum(1 for line in texts["REVIEW.md"].splitlines() if line.startswith("- "))


def write_views(root, texts):
    """Write only what changed. Returns the names written."""
    changed = []
    for name, text in texts.items():
        path = Path(root) / "views" / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            ev.atomic_write(path, text)
            changed.append(name)
    return changed
