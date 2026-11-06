"""mem sync must survive a locally rebuilt views/ and must never report success over a broken pull."""
import os, subprocess, tempfile, unittest
from unittest import mock
from pathlib import Path
from mem import sync

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
ROOT = Path(__file__).resolve().parent.parent


def git(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, env=ENV, capture_output=True, text=True, check=True).stdout


def mem(cwd, *a):
    return subprocess.run(["python3", "-m", "mem", *a], cwd=cwd, env=ENV, capture_output=True, text=True, check=True).stdout


class SyncViews(unittest.TestCase):
    def setUp(self):
        # sync.push runs its own git commands; a CI runner has no identity, and a rebase needs one
        patch = mock.patch.dict(os.environ, {k: v for k, v in ENV.items() if k.startswith("GIT_")})
        patch.start()
        self.addCleanup(patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        git(t, "clone", "-q", "--bare", str(ROOT), "remote.git")
        git(t, "clone", "-q", "remote.git", "me")
        git(t, "clone", "-q", "remote.git", "bot")
        self.me, self.bot = t / "me", t / "bot"

    def tearDown(self):
        self.tmp.cleanup()

    def _bot_pushes_views(self):
        mem(self.bot, "add", "--type", "note", "--owner", "user", "--key", "t.other", "other writer")
        mem(self.bot, "build")
        git(self.bot, "add", "-A"); git(self.bot, "commit", "-qm", "bot views"); git(self.bot, "push", "-q")

    def test_locally_rebuilt_views_do_not_break_sync(self):
        self._bot_pushes_views()
        mem(self.me, "add", "--type", "note", "--owner", "user", "--key", "t.mine", "mine")
        mem(self.me, "build")                                   # dirties tracked views/
        self.assertEqual(sync.push(self.me), "pushed")
        status = git(self.me, "status", "--porcelain")
        self.assertNotIn("U", "".join(l[:2] for l in status.splitlines()), status)
        self.assertEqual(git(self.me, "stash", "list"), "")
        self.assertEqual(git(self.me, "rev-list", "--count", "@{u}..HEAD").strip(), "0")
        self.assertEqual(sync.pull(self.me), "pulled")

    def test_sync_works_on_a_machine_without_a_git_identity(self):
        # a CI runner or a fresh laptop: no user.name/email anywhere. The commit AND the rebase
        # (and its autostash) inside sync.push must still work.
        home = Path(self.tmp.name) / "emptyhome"
        home.mkdir()
        bare = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        bare.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
        self._bot_pushes_views()
        mem(self.me, "add", "--type", "note", "--owner", "user", "--key", "t.mine", "mine")
        mem(self.me, "build")                                   # dirty tracked views: forces an autostash
        with mock.patch.dict(os.environ, bare, clear=True):
            self.assertEqual(sync.push(self.me, retries=0, sleep=lambda s: None), "pushed")
        self.assertEqual(git(self.me, "rev-list", "--count", "@{u}..HEAD").strip(), "0")

    def test_event_conflict_is_reported_not_called_pushed(self):
        # a rebase that cannot complete must never be reported as "pushed"
        # Both writers already know a valid event that sorts after the new one.
        # Fixed historical dates keep this regression independent of the wall clock.
        later = mem(self.bot, "--now", "2001-01-01T00:00:00Z", "add", "--type", "note",
                    "--owner", "user", "--key", "t.later", "pre-existing event").strip()
        git(self.bot, "add", "events"); git(self.bot, "commit", "-qm", "later event"); git(self.bot, "push", "-q")
        git(self.me, "pull", "--ff-only", "-q")
        # `mem add` prints where it stored the event; never guess it from the sort order of the log
        f = self.me / mem(self.me, "--now", "2000-01-01T00:00:00Z", "add", "--type", "note", "--owner", "user", "--key", "t.mine", "mine").strip()
        self.assertTrue(f.is_file(), f)
        self.assertGreater(self.me / later, f)
        git(self.me, "add", "events"); git(self.me, "commit", "-qm", "mem: new events")
        (self.bot / f.relative_to(self.me)).parent.mkdir(parents=True, exist_ok=True)
        (self.bot / f.relative_to(self.me)).write_text("conflicting content\n")
        git(self.bot, "add", "-A"); git(self.bot, "commit", "-qm", "clash"); git(self.bot, "push", "-q")
        remote = self.me.parent / "remote.git"
        before = git(remote, "rev-parse", "HEAD")
        with mock.patch.object(sync, "_git", wraps=sync._git) as calls:
            out = sync.push(self.me, retries=0, sleep=lambda s: None)
        self.assertTrue(out.startswith("conflict after pull, nothing pushed:"), out)
        self.assertEqual(git(remote, "rev-parse", "HEAD"), before)
        self.assertFalse(any("push" in call.args[1:] for call in calls.call_args_list), calls.call_args_list)
        self.assertIn(str(f.relative_to(self.me)), git(self.me, "diff", "--name-only", "--diff-filter=U").splitlines())

    def _bot_pushes_event(self, key):
        mem(self.bot, "add", "--type", "note", "--owner", "user", "--key", key, "other writer")
        git(self.bot, "add", "events"); git(self.bot, "commit", "-qm", key); git(self.bot, "push", "-q")

    def test_pull_and_push_do_not_depend_on_fetch_head(self):
        # Several sessions start at once and each hook pulls the same clone. `git pull` merges whatever is in
        # .git/FETCH_HEAD, which concurrent fetches append to, so it failed with "Cannot fast-forward to multiple
        # branches". sync must work from the remote-tracking branch instead; an unwritable FETCH_HEAD proves it.
        self._bot_pushes_event("t.one")
        fetch_head = self.me / ".git" / "FETCH_HEAD"
        if fetch_head.exists():
            fetch_head.unlink()
        fetch_head.mkdir()
        self.assertEqual(sync.pull(self.me), "pulled")
        self.assertEqual(git(self.me, "rev-parse", "HEAD"), git(self.bot, "rev-parse", "HEAD"))
        self._bot_pushes_event("t.two")
        mem(self.me, "add", "--type", "note", "--owner", "user", "--key", "t.mine", "mine")
        self.assertEqual(sync.push(self.me, retries=0, sleep=lambda s: None), "pushed")
        self.assertEqual(git(self.me, "rev-list", "--count", "HEAD..@{u}").strip(), "0")

    def test_concurrent_pulls_of_one_clone_all_succeed(self):
        from concurrent.futures import ThreadPoolExecutor
        self._bot_pushes_event("t.one")
        with ThreadPoolExecutor(4) as pool:
            results = list(pool.map(lambda _: sync.pull(self.me), range(4)))
        self.assertEqual(results, ["pulled"] * 4)
        self.assertEqual(git(self.me, "rev-parse", "HEAD"), git(self.bot, "rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
