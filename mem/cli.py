"""Command line. Every command works on a plain local clone; none needs a server."""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import core, events as ev, harvest, hooks, install, pendency, project, search, sync, tags, validate

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def _now(args):
    return ev.parse_ts(args.now) if getattr(args, "now", None) else datetime.now(timezone.utc)


def _write(root, now, kind, text="", scope="global", key=None, owner="agent",
           instance="cli", target=None, signal=None, supersedes=(), category=None, tag_list=None):
    e = dict(id=ev.new_id(now, instance), ts=now, type=kind, scope=scope, key=key, body=text,
             instance=instance, owner=owner, supersedes=list(supersedes), target=target,
             signal=signal, category=category, tags=tag_list)
    why = validate.check_event(e, now)
    if why:
        print("refused: " + "; ".join(why), file=sys.stderr)
        return 2
    print(ev.write(root, e).relative_to(root))
    return 0


def _tag_arg(text):
    """None = not given; [] = '-' (clear); else the list."""
    if text is None:
        return None
    return [t.strip().lower() for t in text.split(",") if t.strip() and t.strip() != "-"]


def run(argv=None, stdin=None):
    p = argparse.ArgumentParser(prog="mem", description=__doc__)
    p.add_argument("--root", default=os.environ.get("MEM_HOME", str(DEFAULT_ROOT)))
    p.add_argument("--now", help="ISO time, for tests and reproducible builds")
    p.add_argument("--instance", default=os.environ.get("MEM_INSTANCE", "code"))
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="record an entry")
    add.add_argument("--type", default="pref", choices=ev.TYPES[:6])
    add.add_argument("--scope", default="global")
    add.add_argument("--key")
    add.add_argument("--owner", default="agent")
    add.add_argument("--supersedes", default="")
    add.add_argument("--tags", help="comma-separated kinds of task (mem/tags.toml); '-' clears; omitted = keep the "
                                    "tags of the entry this one replaces")
    add.add_argument("text", help="the text, or - to read it from stdin")
    fb = sub.add_parser("feedback", help="say an entry helped or was wrong")
    fb.add_argument("target")
    fb.add_argument("signal", choices=ev.SIGNALS)
    for name in ("forget", "done", "archive", "reopen"):
        sub.add_parser(name).add_argument("target")
    task = sub.add_parser("task", help="open an item (pendency) with the check that tells if it still applies")
    task.add_argument("--scope", default="global")
    task.add_argument("--check", required=True,
                      help="how to verify it still applies (a command, a file, a page); it is run before any reminder")
    task.add_argument("--category", help="a group of open items, e.g. quiz; a whole category can be rescoped")
    task.add_argument("text")
    claim = sub.add_parser("claim", help="claim a task; the earliest claim wins")
    claim.add_argument("target")
    use = sub.add_parser("use", help="report which entries you applied, and how")
    use.add_argument("refs", help="comma-separated refs or ids")
    use.add_argument("--note", default="", help="how, in one short line")
    pend = sub.add_parser("pending", help="list open items (pendencies), whatever their scope")
    pend.add_argument("--archived", action="store_true", help="list the parked ones instead")
    pend.add_argument("--all", action="store_true", help="list open and parked together")
    sc = sub.add_parser("scope", help="make an open item, or a whole category, depend on a scope (or global again)")
    sc.add_argument("scope", help="global, project:NAME or instance:NAME")
    sc.add_argument("ref", nargs="?", help="the open item")
    sc.add_argument("--category", help="every open item of this category, present and future")
    br = sub.add_parser("brief", help="print the brief for a project and instance")
    br.add_argument("--project")
    br.add_argument("--budget", type=int, default=project.BRIEF_BUDGET)
    br.add_argument("--ids", action="store_true")
    rl = sub.add_parser("rules", help="print the full rules tagged for a kind of task")
    rl.add_argument("tags", nargs="+", help="one or more tags from mem/tags.toml")
    rl.add_argument("--project", help="default: the name of the working directory")
    tg = sub.add_parser("tag", help="set the tags of an existing rule (key or ref); '-' clears")
    tg.add_argument("rule", help="its key (when unique) or its #ref")
    tg.add_argument("tags", nargs="+")
    tg.add_argument("--scope", help="needed when the same key exists in several scopes")
    sub.add_parser("search").add_argument("query")
    sub.add_parser("check", help="list invalid events; exit 1 if any")
    sub.add_parser("quarantine", help="move invalid events to quarantine/")
    sub.add_parser("dismiss", help="delete a reviewed file from quarantine/").add_argument("name")
    sub.add_parser("promote", help="write global entries for habits seen in 2 projects")
    cp = sub.add_parser("compact", help="digest cold entries (proposal unless --apply)")
    cp.add_argument("--apply", action="store_true")
    build = sub.add_parser("build", help="regenerate views/")
    build.add_argument("--check", action="store_true", help="fail if views are out of date")
    sy = sub.add_parser("sync", help="pull and/or push a local clone")
    sy.add_argument("--pull", action="store_true")
    sy.add_argument("--push", action="store_true")
    for name in ("hook-prompt", "hook-session-start", "hook-stop"):
        sub.add_parser(name)
    ih = sub.add_parser("install-hooks", help="add the hooks to a Claude Code settings.json")
    ih.add_argument("--settings", default=str(Path.home() / ".claude/settings.json"))
    ih.add_argument("--uninstall", action="store_true")

    a = p.parse_args(argv)
    root, now, instance = Path(a.root), _now(a), a.instance
    stdin = stdin or sys.stdin

    if a.cmd == "add":
        text = stdin.read().strip() if a.text == "-" else a.text
        replaces = [s for s in a.supersedes.split(",") if s]
        events, _ = validate.load_checked(root, now)
        active = core.fold(events)[0]
        if a.key and not replaces:  # say what is being replaced, so it is not a conflict
            prev = [e for e in active if e["scope"] == a.scope and e["key"] == a.key]
            if prev and core.norm_tokens(prev[-1]["body"]) != core.norm_tokens(text):
                replaces = [prev[-1]["id"]]
        tag_list = _tag_arg(a.tags)
        if tag_list is None:  # a replacement keeps the tags it replaces, copied now so reading stays order-free
            old = [e for e in active if e["id"] in replaces or core.ref(e["id"]) in replaces]
            tag_list = tags.of(old[0]) if old and old[0].get("tags") is not None else None
        return _write(root, now, a.type, text, a.scope, a.key, a.owner, instance, supersedes=replaces,
                      tag_list=tag_list)
    if a.cmd == "rules":
        events, _ = validate.load_checked(root, now)
        proj = a.project or Path.cwd().name
        unknown = [t for t in a.tags if t not in tags.vocabulary()]
        if unknown:
            print(f"refused: unknown tag(s) {', '.join(unknown)}; known: {', '.join(tags.vocabulary())}",
                  file=sys.stderr)
            return 2
        found = tags.rules(events, a.tags, proj, instance)
        print("\n".join(tags.render(e) for e in found) if found else "(no rules with these tags here)")
        return 0
    if a.cmd == "tag":
        events, _ = validate.load_checked(root, now)
        hit = [e for e in core.fold(events)[0] if e["type"] in tags.TAGGED and (
            core.ref(e["id"]) == a.rule.lstrip("#") or (e["key"] == a.rule and (not a.scope or e["scope"] == a.scope)))]
        if len(hit) != 1:
            print(f"refused: {len(hit)} rules match {a.rule!r}; give --scope or the #ref", file=sys.stderr)
            return 2
        e = hit[0]
        return _write(root, now, e["type"], e["body"], e["scope"], e["key"], e["owner"], instance,
                      supersedes=[e["id"]], tag_list=_tag_arg(",".join(a.tags)))
    if a.cmd == "feedback":
        return _write(root, now, "feedback", "", instance=instance, target=a.target, signal=a.signal)
    if a.cmd in ("forget", "done", "claim", "archive", "reopen"):
        return _write(root, now, a.cmd, "", instance=instance, target=a.target)
    if a.cmd == "task":
        return _write(root, now, "task", f"{a.text} {pendency.CHECK_MARK} {a.check}", a.scope,
                      instance=instance, category=a.category)
    if a.cmd == "use":
        return _write(root, now, "use", a.note, instance=instance, target=a.refs)
    if a.cmd == "brief":
        events, _ = validate.load_checked(root, now)
        out = core.brief(events, [], now, project=a.project, instance=instance,
                         budget=a.budget, ids=a.ids)
        extra = pendency.render(pendency.section(events, a.project, instance))
        print("\n".join([out["header"], *out["lines"], *extra]))
        return 0
    if a.cmd == "pending":
        events, _ = validate.load_checked(root, now)
        for i in pendency.items(events):
            if a.all or i["archived"] == a.archived:
                e = i["event"]
                state = "ARCHIVED" if i["archived"] else "OPEN"
                tag = " ".join(x for x in (i["category"], i["scope"]) if x and x != "global")
                print(f"#{core.ref(e['id'])}  {state}  since {i['since']:%Y-%m-%d}"
                      f"{'  [' + tag + ']' if tag else ''}  {' '.join(e['body'].split())}")
        return 0
    if a.cmd == "scope":
        if bool(a.ref) == bool(a.category):
            print("refused: give either an item or --category", file=sys.stderr)
            return 2
        return _write(root, now, "rescope", "", a.scope, instance=instance, target=a.ref, category=a.category)
    if a.cmd == "search":
        events, _ = validate.load_checked(root, now)
        for eid in search.Index(events, instance=instance).search(a.query):
            print(eid)
        return 0
    if a.cmd == "check":
        _, invalid = validate.load_checked(root, now)
        for path, why in invalid:
            print(f"{path}: {'; '.join(why)}")
        events, _ = validate.load_checked(root, now)
        for e in tags.untagged(events):  # a warning, not an error: the exit code only follows invalid events
            print(f"warning: no tag: [{e['key'] or '-'}] #{core.ref(e['id'])}")
        return 1 if invalid else 0
    if a.cmd == "quarantine":
        for path, why in validate.quarantine(root, now):
            print(f"quarantined {path}: {'; '.join(why)}")
        return 0
    if a.cmd == "dismiss":
        stem = Path(a.name).name.removesuffix(".md").removesuffix(".reason")
        gone = [p for p in (root / "quarantine" / f"{stem}.md", root / "quarantine" / f"{stem}.reason")
                if p.exists()]
        for p in gone:
            p.unlink()
        print(f"dismissed {stem}" if gone else f"nothing named {stem} in quarantine/")
        return 0 if gone else 1
    if a.cmd == "promote":
        events, _ = validate.load_checked(root, now)
        for e in harvest.promote(events, now):
            print(ev.write(root, e).relative_to(root))
        return 0
    if a.cmd == "compact":
        events, _ = validate.load_checked(root, now)
        digests = core.compaction_proposals(events, [], now)
        for d in digests:
            print(f"{'wrote' if a.apply else 'would write'} {d['id']} ({len(d['supersedes'])} entries)")
            if a.apply:
                d.update(owner="compactor", target=None, signal=None, key=None)
                ev.write(root, d)
        return 0
    if a.cmd == "build":
        texts = project.build(root, now)
        if a.check:
            stale = [n for n, t in texts.items()
                     if not (root / "views" / n).exists()
                     or (root / "views" / n).read_text(encoding="utf-8") != t]
            for n in stale:
                print(f"out of date: views/{n}")
            return 1 if stale else 0
        for n in project.write_views(root, texts):
            print(f"wrote views/{n}")
        return 0
    if a.cmd == "sync":
        if a.pull or not a.push:
            print(sync.pull(root))
        if a.push:
            print(sync.push(root))
        return 0
    if a.cmd.startswith("hook-"):
        payload = hooks.read_payload(stdin)
        fn = dict(zip(("hook-prompt", "hook-session-start", "hook-stop"),
                      (hooks.prompt, hooks.session_start, hooks.stop)))[a.cmd]
        return fn(root, payload, now, instance)
    if a.cmd == "install-hooks":
        report = install.apply(Path(a.settings), str(root / "bin" / "mem"), remove=a.uninstall)
        print(report)
        return 0
    return 1


def main():
    sys.exit(run())
