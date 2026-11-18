import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import repo_sync as rs  # noqa: E402


def sh(cwd, *a):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)


class RepoSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.remote = t / 'remote.git'
        sh(t, 'git', 'init', '-q', '--bare', '-b', 'main', str(self.remote))
        self.repo = t / 'work'
        self.repo.mkdir()
        sh(self.repo, 'git', 'init', '-q', '-b', 'main')
        sh(self.repo, 'git', 'config', 'user.email', 'a@b')
        sh(self.repo, 'git', 'config', 'user.name', 'a')
        (self.repo / 'f').write_text('1')
        sh(self.repo, 'git', 'add', 'f')
        sh(self.repo, 'git', 'commit', '-qm', 'one')

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_remote_is_reported(self):
        self.assertTrue(any('no remote' in p for p in rs.check(self.repo)))

    def test_synced_repo_is_clean_and_each_problem_is_named(self):
        sh(self.repo, 'git', 'remote', 'add', 'origin', str(self.remote))
        sh(self.repo, 'git', 'push', '-q', '-u', 'origin', 'main')
        self.assertEqual(rs.check(self.repo), [])
        (self.repo / 'f').write_text('2')
        self.assertTrue(any('uncommitted' in p for p in rs.check(self.repo)))
        sh(self.repo, 'git', 'commit', '-qam', 'two')
        self.assertTrue(any('not pushed' in p for p in rs.check(self.repo)))
        sh(self.repo, 'git', 'branch', 'side')
        sh(self.repo, 'git', 'worktree', 'add', '-q', str(Path(self.tmp.name) / 'wt'), 'side')
        probs = ' '.join(rs.check(self.repo))
        self.assertIn('extra branch side', probs)
        self.assertIn('extra worktree', probs)
