#!/usr/bin/env python3
"""Reports git work that is not safely on its remote main, for every repository under ~/dev.

Why: the one-branch rule (work.single-branch) and the GitHub rule (work.github-standard) were only text; sessions that stopped
(usage limit, closed terminal) left uncommitted files, CI branches, worktrees and repos without a remote. This is the check.
Modes: `report` (list, exit 0), `hook-stop` (Claude Code Stop hook: once per session, never blocks). The hook answers with
JSON `{"systemMessage": ...}`: plain text printed by a Stop hook reaches neither the assistant nor the screen, a systemMessage is
shown to the user.
A deliberate extra branch is declared with `git config --add repo-sync.branch NAME`. Standard library only. Read-only: it never commits, pushes or deletes anything.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get('REPO_SYNC_ROOT', str(Path.home() / 'dev')))
STATE = Path(os.environ.get('REPO_SYNC_STATE', str(Path.home() / '.local/state/repo-sync')))
DIRTY_MIN_AGE = 20 * 60        # files touched in the last 20 minutes are probably a live session's: shown, not nagged about
MAIN = ('main', 'master')


def git(repo, *args):
    """Output of a read-only git call; '' when git fails or does not answer in time (never raises)."""
    try:
        p = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ''
    return p.stdout.strip() if p.returncode == 0 else ''


def repos(root=ROOT):
    return sorted(p for p in Path(root).iterdir() if (p / '.git').is_dir())


def newest_mtime(repo, lines):
    t = 0.0
    for ln in lines:
        f = Path(repo) / ln[3:].split(' -> ')[-1].strip('"')
        try:
            t = max(t, f.stat().st_mtime)
        except OSError:
            pass
    return t


def check(repo, now=None):
    """Problems of one repository, as short sentences."""
    now = now or time.time()
    out = []
    if not git(repo, 'rev-parse', '--git-dir'):
        return ['git did not answer here (broken repository or a timeout): not checked']
    remotes = git(repo, 'remote').split()
    declared = git(repo, 'config', '--get-all', 'repo-sync.branch').split()
    if not remotes:
        out.append('no remote: the work exists on this disk only')
    st = [ln for ln in git(repo, 'status', '--short').splitlines() if ln]
    if st:
        age = (now - newest_mtime(repo, st)) / 60
        out.append(f'{len(st)} uncommitted file(s), newest touched {age:.0f} min ago' + (' (a live session?)' if age * 60 < DIRTY_MIN_AGE else ''))
    for b in git(repo, 'branch', '--format=%(refname:short)|%(upstream:short)|%(upstream:track)').splitlines():
        name, up, track = (b.split('|') + ['', ''])[:3]
        if name in MAIN:
            if remotes and 'ahead' in track:
                out.append(f'{name} has commits not pushed {track}')
            elif remotes and not up:
                out.append(f'{name} follows no remote branch, so unpushed commits cannot be seen (git push -u origin {name})')
        elif name and name not in declared:
            out.append(f'extra branch {name}' + (f' {track}' if track else '') + ' (rule: one branch, main)')
    # Branches that exist on the remote only (as of the last fetch; no network call here): a CI branch whose local copy was deleted.
    for ref in git(repo, 'branch', '-r', '--format=%(refname:short)').splitlines():
        remote, _, name = ref.partition('/')
        if name and name not in MAIN and name != 'HEAD' and name not in declared:
            out.append(f'extra remote branch {ref} (rule: one branch, main)')
    wts = [ln for ln in git(repo, 'worktree', 'list', '--porcelain').split('\n\n')][1:]
    for w in wts:
        path = w.splitlines()[0][9:] if w else ''
        if path:
            out.append(f'extra worktree {path}')
    return out


def report(root=ROOT):
    return {p.name: probs for p in repos(root) if (probs := check(p))}


def format_report(r):
    return '\n'.join(f'- {name}: ' + '; '.join(probs) for name, probs in r.items())


def hook_stop():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    sid = str(data.get('session_id') or 'none')
    STATE.mkdir(parents=True, exist_ok=True)
    seen = STATE / f'seen-{sid}'
    r = report()
    if not r or seen.exists():
        return 0
    seen.write_text(str(time.time()))
    for old in STATE.glob('seen-*'):
        if time.time() - old.stat().st_mtime > 7 * 86400:
            old.unlink()
    text = 'Repos not in sync with their remote (commit, push to main, delete CI branches and worktrees; or say why not):\n' + format_report(r)
    print(json.dumps({'systemMessage': text}))
    return 0


def main(argv=None):
    a = (argv if argv is not None else sys.argv[1:]) or ['report']
    if a[0] == 'hook-stop':
        return hook_stop()
    r = report()
    print(format_report(r) if r else 'all repositories are in sync')
    return 0


if __name__ == '__main__':
    sys.exit(main())
