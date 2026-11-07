"""A leaked GIT_DIR must not let the tests touch another repository (the 2026-11-07 incident)."""
import os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def state(repo):
    refs = subprocess.run(["git", "-C", repo, "for-each-ref"], capture_output=True, text=True, check=True).stdout
    return refs, (Path(repo) / ".git" / "config").read_text(encoding="utf-8")


class Hermetic(unittest.TestCase):
    def test_a_leaked_git_dir_leaves_that_repository_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            victim = os.path.join(d, "victim")
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            env.update(GIT_AUTHOR_NAME="v", GIT_AUTHOR_EMAIL="v@v", GIT_COMMITTER_NAME="v", GIT_COMMITTER_EMAIL="v@v")
            subprocess.run(["git", "init", "-q", "-b", "main", victim], check=True, env=env)
            subprocess.run(["git", "-C", victim, "commit", "-q", "--allow-empty", "-m", "victim"], check=True, env=env)
            before = state(victim)
            env["GIT_DIR"] = os.path.join(victim, ".git")
            run = subprocess.run([sys.executable, "-m", "unittest", "-q", "tests.test_sync_views"], cwd=ROOT, env=env,
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr[-2000:])
            self.assertEqual(state(victim), before, "the sync tests changed the repository named by GIT_DIR")


if __name__ == "__main__":
    unittest.main()
