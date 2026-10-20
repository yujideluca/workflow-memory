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
        mem(self.me, "add", "--type", "note", "--owner", "user", "--key", "t.mine", "mine")
        f = sorted((self.me / "events").rglob("*.md"))[-1]
        git(self.me, "add", "events"); git(self.me, "commit", "-qm", "mem: new events")
        (self.bot / f.relative_to(self.me)).parent.mkdir(parents=True, exist_ok=True)
        (self.bot / f.relative_to(self.me)).write_text("conflicting content\n")
        git(self.bot, "add", "-A"); git(self.bot, "commit", "-qm", "clash"); git(self.bot, "push", "-q")
        out = sync.push(self.me, retries=0, sleep=lambda s: None)
        self.assertNotEqual(out, "pushed", out)


if __name__ == "__main__":
    unittest.main()
