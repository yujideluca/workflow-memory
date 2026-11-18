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

    def test_a_branch_left_on_the_remote_only_is_reported_unless_declared(self):
        sh(self.repo, 'git', 'remote', 'add', 'origin', str(self.remote))
        sh(self.repo, 'git', 'push', '-q', '-u', 'origin', 'main')
        sh(self.repo, 'git', 'push', '-q', 'origin', 'main:ci-try')
        self.assertIn('extra remote branch origin/ci-try', ' '.join(rs.check(self.repo)))
        sh(self.repo, 'git', 'config', '--add', 'repo-sync.branch', 'ci-try')
        self.assertEqual(rs.check(self.repo), [])

    def test_main_that_follows_no_remote_branch_is_reported(self):
        sh(self.repo, 'git', 'remote', 'add', 'origin', str(self.remote))
        sh(self.repo, 'git', 'push', '-q', 'origin', 'main')          # pushed once, but without -u
        (self.repo / 'f').write_text('2')
        sh(self.repo, 'git', 'commit', '-qam', 'two')
        self.assertIn('main follows no remote branch', ' '.join(rs.check(self.repo)))

    def test_a_repository_git_cannot_read_is_reported_not_skipped_and_never_crashes(self):
        root = Path(self.tmp.name) / 'root'
        (root / 'broken' / '.git').mkdir(parents=True)                 # a .git folder that is not a repository
        r = rs.report(root)
        self.assertIn('broken', r)
        self.assertIn('git did not answer', ' '.join(r['broken']))

    def test_the_stop_hook_tells_once_per_session_as_a_message_the_user_sees(self):
        import io, json, os
        from unittest import mock
        root = Path(self.tmp.name) / 'root'
        root.mkdir()
        self.repo.rename(root / 'work')
        state = Path(self.tmp.name) / 'state'
        with mock.patch.object(rs, 'ROOT', root), mock.patch.object(rs, 'STATE', state):
            outs = []
            for _ in range(2):
                with mock.patch('sys.stdin', io.StringIO('{"session_id": "s1"}')), mock.patch('sys.stdout', io.StringIO()) as out:
                    self.assertEqual(rs.hook_stop(), 0)
                outs.append(out.getvalue())
        self.assertIn('no remote', json.loads(outs[0])['systemMessage'])
        self.assertEqual(outs[1], '')

    def test_a_repository_declared_local_only_is_not_asked_for_a_remote(self):
        sh(self.repo, 'git', 'config', 'repo-sync.local', 'temporary experiment')
        self.assertEqual(rs.check(self.repo), [])
        (self.repo / 'f').write_text('2')
        self.assertTrue(any('uncommitted' in p for p in rs.check(self.repo)), 'the other checks still apply')



class StopHookLog(unittest.TestCase):
    """The memory Stop hook cannot speak (exit 0, no output), so every result that is not a success must reach its log."""

    def test_a_conflict_or_a_failed_push_is_logged_and_a_success_is_not(self):
        from unittest import mock
        from mem import hooks
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(hooks, 'STATE', Path(d)):
                for result in ('pushed', 'nothing to push'):
                    with mock.patch.object(hooks.sync, 'push', return_value=result):
                        self.assertEqual(hooks.stop(Path(d), {}, None, None), 0)
                self.assertFalse((Path(d) / 'hook.log').exists())
                for result in ('conflict after pull, nothing pushed: x', 'push failed; events stay', 'commit failed: y'):
                    with mock.patch.object(hooks.sync, 'push', return_value=result):
                        self.assertEqual(hooks.stop(Path(d), {}, None, None), 0)
                    self.assertIn(result, (Path(d) / 'hook.log').read_text())

    def test_the_hook_log_is_cut_to_its_newest_part_when_it_grows_past_the_limit(self):
        from unittest import mock
        from mem import hooks
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(hooks, 'STATE', Path(d)), mock.patch.object(hooks, 'LOG_MAX', 2000):
                for i in range(200):
                    hooks._log(f'line {i:04d} ' + 'x' * 40)
                text = (Path(d) / 'hook.log').read_text()
        self.assertLessEqual(len(text), 2000 + 200)
        self.assertIn('line 0199', text)
        self.assertNotIn('line 0000', text)
        self.assertTrue(text.splitlines()[0].startswith('20') or text.startswith('...'), 'it starts at a whole line')
