"""Git transport for a local clone. Never forces; offline means "try later"."""
import contextlib
import os
import subprocess
import time

try:
    import fcntl
except ImportError:         # not POSIX: no lock, sync works as before
    fcntl = None


def _git(root, *args, timeout=30):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout
    )


def _identity(root):
    if _git(root, "config", "user.email").stdout.strip():
        return []
    return ["-c", "user.name=mem", "-c", "user.email=mem@localhost"]


def _first_line(done, default):
    return (done.stderr.strip().splitlines() or [default])[0][:120]


def _fetch(root, timeout):
    """Update the remote-tracking branches without `git pull`.

    Several sessions start at once and their hooks fetch the same clone. `git pull` merges what .git/FETCH_HEAD
    names, and concurrent fetches append to that file, so a pull then fails with "Cannot fast-forward to
    multiple branches". Fetching without FETCH_HEAD and merging `@{u}` avoids the file; a second fetch covers
    the other race, two fetches moving origin/main at once ("incorrect old value provided").
    """
    done = _git(root, "fetch", "--quiet", "--no-write-fetch-head", timeout=timeout)
    if done.returncode != 0:
        done = _git(root, "fetch", "--quiet", "--no-write-fetch-head", timeout=timeout)
    return done


@contextlib.contextmanager
def _one_at_a_time(root, wait):
    """Let one sync at a time work on this clone. Sessions that start together run their hooks together, and two
    merges or rebases in one working tree trip over each other's files. Waits at most `wait` seconds, then goes
    ahead anyway (a stuck holder must not block every session)."""
    found = _git(root, "rev-parse", "--absolute-git-dir", timeout=5)
    if fcntl is None or found.returncode != 0:
        yield
        return
    with open(os.path.join(found.stdout.strip(), "mem-sync.lock"), "a") as f:
        deadline = time.monotonic() + wait
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def pull(root):
    """Fast-forward to the upstream branch (what `git pull --ff-only` did, without FETCH_HEAD)."""
    try:
        with _one_at_a_time(root, wait=15):
            done = _fetch(root, timeout=15)
            if done.returncode == 0:
                done = _git(root, "merge", "--ff-only", "--quiet", "@{u}", timeout=15)
    except subprocess.TimeoutExpired:
        return "pull skipped: timeout"
    return "pulled" if done.returncode == 0 else "pull skipped: " + _first_line(done, "unknown")


def _unmerged(root):
    return bool(_git(root, "diff", "--name-only", "--diff-filter=U").stdout.strip())


def push(root, retries=4, sleep=time.sleep):
    """Commit new events, then push with backoff (2, 4, 8, 16 s)."""
    with _one_at_a_time(root, wait=10):
        _git(root, "add", "events")
        if _git(root, "diff", "--cached", "--quiet").returncode != 0:
            done = _git(root, *_identity(root), "commit", "-q", "-m", "mem: new events")
            if done.returncode != 0:
                return "commit failed: " + done.stderr.strip()[:120]
    ahead = _git(root, "rev-list", "--count", "@{u}..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() == "0":
        return "nothing to push"
    for attempt in range(retries + 1):
        try:
            with _one_at_a_time(root, wait=10):
                # views/ is generated (CI owns it, `mem build` rewrites it): a local rebuild is never worth
                # a merge. Drop it so the pull cannot conflict; the next `mem build` regenerates it.
                _git(root, "checkout", "--", "views")
                # `git pull --rebase` without FETCH_HEAD (see _fetch); a bare `rebase` uses the upstream and its
                # fork point, as pull does.
                pulled = _fetch(root, timeout=30)
                if pulled.returncode == 0:
                    pulled = _git(root, *_identity(root), "rebase", "--autostash", "--quiet", timeout=30)
                if _unmerged(root):     # offline or rejected is retried below; a conflict is not "pushed"
                    return "conflict after pull, nothing pushed: " + (pulled.stderr.strip().splitlines() or ["see git status"])[-1][:120]
                done = _git(root, "push", "--quiet", timeout=30)
        except subprocess.TimeoutExpired:
            done = None
        if done is not None and done.returncode == 0:
            return "pushed"
        if attempt < retries:
            sleep(2 ** (attempt + 1))
    return "push failed; events stay committed locally and go out next time"
