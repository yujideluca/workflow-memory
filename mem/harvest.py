"""Preference detector: the user's own words only, verbatim quote as evidence."""
import hashlib
import re

from .core import key_tokens, norm_tokens, resolve

_MARKER = re.compile(
    r"\b(always|never|prefer|instead of|from now on|by default|i usually|sempre|nunca|"
    r"prefiro|em vez de|n[aã]o use|a partir de agora|por padr[aã]o|geralmente)\b",
    re.I,
)
_ACTION = re.compile(
    r"\b(use|usar|prefer|prefiro|ask|perguntar|pergunte|answer|respond\w*|write|escrev\w*|"
    r"run|rodar|send|enviar|log|registr\w*|show|mostr\w*|instead|over|than|call|chamar|"
    r"edit\w*|save|salv\w*|install|instal\w*|explain|explic\w*|commit\w*)\b",
    re.I,
)
_GLOBAL = re.compile(
    r"\b(in all my projects|every project|across projects|everywhere|"
    r"em todos os meus projetos|todos os projetos|em todo lugar)\b",
    re.I,
)
_AGENT_LIKE = re.compile(r"\*\*|\w+\.\w+:\d+")
_CODE = re.compile(r"```.*?```", re.S)


def candidates(prompts):
    """prompts: dicts with text, ts, project, source. Only source == 'user' counts."""
    out = []
    for p in prompts:
        if p.get("source") != "user":
            continue  # tool output and agent text never become preferences
        for s in re.split(r"(?<=[.!?])\s+", _CODE.sub("", p["text"])):
            s = s.strip()
            if (not s or s.endswith("?") or _AGENT_LIKE.search(s)
                    or not _MARKER.search(s) or not _ACTION.search(s)):
                continue
            kt = key_tokens(s)
            out.append(dict(
                text=s, ts=p["ts"], project=p["project"], norm=tuple(norm_tokens(s)),
                explicit=bool(_GLOBAL.search(s)),
                key="auto." + hashlib.sha1(" ".join(kt).encode()).hexdigest()[:10],
            ))
    return out


def event_id(c):
    """Deterministic, so a repeated hook call writes the same file."""
    digest = hashlib.sha1(c["text"].encode()).hexdigest()[:6]
    return f"{c['ts']:%Y%m%dT%H%M%SZ}-harvester-{digest}"


def promote(events, now, min_projects=2):
    """Global entries for keys the harvester saw in min_projects projects.

    Pure and idempotent: ids come from the key and wording, and an id already
    in the log is never proposed again. One sentence fanned out to several
    projects within an hour counts as one project.
    """
    known = {e["id"] for e in events}
    groups = {}
    for e in events:
        if e.get("instance") == "harvester" and e["scope"].startswith("project:"):
            groups.setdefault(e["key"], []).append(e)
    glob = {e["key"] for e in resolve(events)["active"] if e["scope"] == "global"}
    out = []
    for key, items in sorted(groups.items()):
        seen = {(tuple(norm_tokens(e["body"])), e["ts"].replace(minute=0, second=0, microsecond=0)):
                e["scope"] for e in items}
        if len(set(seen.values())) < min_projects or key in glob:
            continue
        latest = max(items, key=lambda e: (e["ts"], e["id"]))
        digest = hashlib.sha1(f"{key}|{' '.join(norm_tokens(latest['body']))}".encode()).hexdigest()[:6]
        eid = f"{now:%Y%m%dT%H%M%SZ}-harvester-promo{digest}"
        if any(k.endswith(f"-harvester-promo{digest}") for k in known):
            continue
        out.append(dict(id=eid, ts=now, type="pref", scope="global", key=key, body=latest["body"],
                        instance="harvester", owner="harvester", supersedes=[], target=None,
                        signal=None))
    return out


def converge(cands, min_projects=2):
    """Pref events. A topic goes global when scoped so explicitly or seen in
    min_projects projects (one sentence fanned out within an hour counts once)."""
    groups = {}
    for c in cands:
        groups.setdefault(c["key"], []).append(c)
    events = []
    for key, items in groups.items():
        seen = {(c["norm"], c["ts"].replace(minute=0, second=0, microsecond=0)): c["project"]
                for c in items}
        is_global = any(c["explicit"] for c in items) or len(set(seen.values())) >= min_projects
        for c in items:
            events.append(dict(
                id="h-" + hashlib.sha1(f"{key}|{c['ts'].isoformat()}|{c['text']}".encode()).hexdigest()[:12],
                ts=c["ts"], type="pref", key=key, body=c["text"], instance="harvester",
                owner="harvester", supersedes=[],
                scope="global" if is_global else f"project:{c['project']}",
                evidence=[dict(project=c["project"], ts=c["ts"], quote=c["text"])],
            ))
    return events
