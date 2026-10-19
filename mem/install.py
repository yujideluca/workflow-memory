"""Wire the hooks into a Claude Code settings.json. Idempotent, with a backup."""
import json
import shutil
from datetime import datetime
from pathlib import Path

from . import events as ev, hooks

EVENTS = {"SessionStart": "hook-session-start", "UserPromptSubmit": "hook-prompt", "Stop": "hook-stop"}


def _is_ours(entry):
    return any(hooks.MARK in h.get("command", "") for h in entry.get("hooks", []))


def apply(settings_path, mem_bin, remove=False):
    path = Path(settings_path)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    block = data.setdefault("hooks", {})
    for event, sub in EVENTS.items():
        kept = [e for e in block.get(event, []) if not _is_ours(e)]
        if not remove:
            kept.append({"hooks": [{"type": "command", "command": f"python3 {mem_bin} {sub}"}]})
        if kept:
            block[event] = kept
        else:
            block.pop(event, None)
    if not block:
        data.pop("hooks")
    if path.exists():
        shutil.copy2(path, path.with_name(f"{path.name}.bak-{datetime.now():%Y%m%d%H%M%S}"))
    ev.atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return f"{'removed from' if remove else 'installed in'} {path}"
