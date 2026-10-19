"""Git transport for a local clone. Never forces; offline means "try later"."""
import subprocess
import time


def _git(root, *args, timeout=30):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout
    )


def _identity(root):
    if _git(root, "config", "user.email").stdout.strip():
        return []
    return ["-c", "user.name=mem", "-c", "user.email=mem@localhost"]


def pull(root):
    try:
        done = _git(root, "pull", "--ff-only", "--quiet", timeout=15)
    except subprocess.TimeoutExpired:
        return "pull skipped: timeout"
    return "pulled" if done.returncode == 0 else "pull skipped: " + (done.stderr.strip().splitlines() or ["unknown"])[0][:120]


def push(root, retries=4, sleep=time.sleep):
    """Commit new events and usage rows, then push with backoff (2, 4, 8, 16 s)."""
    _git(root, "add", "events", "usage")
    if _git(root, "diff", "--cached", "--quiet").returncode != 0:
        done = _git(root, *_identity(root), "commit", "-q", "-m", "mem: new events")
        if done.returncode != 0:
            return "commit failed: " + done.stderr.strip()[:120]
    ahead = _git(root, "rev-list", "--count", "@{u}..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() == "0":
        return "nothing to push"
    for attempt in range(retries + 1):
        try:
            _git(root, "pull", "--rebase", "--autostash", "--quiet", timeout=30)
            done = _git(root, "push", "--quiet", timeout=30)
        except subprocess.TimeoutExpired:
            done = None
        if done is not None and done.returncode == 0:
            return "pushed"
        if attempt < retries:
            sleep(2 ** (attempt + 1))
    return "push failed; events stay committed locally and go out next time"
