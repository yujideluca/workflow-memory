"""Open items (pendencies): a task carries a Check line, never decays, and is verified before Giovanni is reminded."""
import contextlib, io, unittest
from datetime import timedelta
from pathlib import Path
import tempfile

from mem import cli, core, hooks, events as ev
from tests.test_system import Tmp, ISO, NOW


class Pendencies(Tmp):
    def call(self, fn, payload):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = fn(self.root, payload, NOW, "code")
        return code, out.getvalue()

    def task(self, text="fix the thing", check="look at the thing"):
        return self.run_cli("task", text, "--check", check)

    def tasks(self):
        return [e for e in ev.load(self.root)[0] if e["type"] == "task"]

    def test_task_requires_a_check_line(self):
        with self.assertRaises(SystemExit):
            self.run_cli("task", "fix the thing")
        self.assertEqual(self.tasks(), [])

    def test_check_is_stored_in_the_entry(self):
        self.assertEqual(self.task("fix the thing", "run the tests")[0], 0)
        body = self.tasks()[0]["body"]
        self.assertIn("fix the thing", body)
        self.assertIn("check: run the tests", body)

    def test_open_item_never_decays_and_is_labelled(self):
        self.task()
        events = ev.load(self.root)[0]
        later = ev.parse_ts("2027-12-31T00:00:00Z")
        out = core.brief(events, [], later, ids=True)
        line = [l for l in out["lines"] if "fix the thing" in l]
        self.assertEqual(len(line), 1, "an open item must still be in the brief 14 months later")
        self.assertIn("[open item]", line[0])

    def test_done_removes_it_from_the_brief(self):
        self.task()
        tid = self.tasks()[0]["id"]
        self.assertEqual(self.run_cli("done", tid)[0], 0)
        out = core.brief(ev.load(self.root)[0], [], ev.parse_ts(ISO), ids=True)
        self.assertFalse([l for l in out["lines"] if "fix the thing" in l])

    def test_session_start_tells_the_reader_to_verify_only_when_items_exist(self):
        self.assertNotIn("open item", self.call(hooks.session_start, {})[1].lower())
        self.task()
        text = self.call(hooks.session_start, {})[1]
        self.assertIn("fix the thing", text)
        self.assertIn("verify", text.lower())
        self.assertIn("mem done", text)

    def test_project_scoped_item_is_not_shown_elsewhere(self):
        self.run_cli("task", "quiz only", "--check", "x", "--scope", "project:QuizApp")
        self.assertNotIn("quiz only", self.call(hooks.session_start, {"cwd": "/tmp/projA"})[1])
        self.assertIn("quiz only", self.call(hooks.session_start, {"cwd": "/home/x/QuizApp"})[1])


if __name__ == "__main__":
    unittest.main()
