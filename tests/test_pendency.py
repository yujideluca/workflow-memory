"""Open items (pendencies): shown in every chat until solved, archived or deleted; scope only on request.

Every place that used to see tasks is covered here, so a change in one cannot silently break another:
brief budget, views, compaction, search, events format, validation, hooks, CLI and calibration.
"""
import contextlib
import importlib.util
import io
import unittest
from datetime import timedelta
from pathlib import Path

from mem import cli, core, events as ev, hooks, pendency as pd, project, search, validate
from tests.test_system import Tmp, ISO, NOW, mk

ROOT = Path(__file__).resolve().parent.parent


def task(n, ts=NOW, scope="global", body=None, check=True, category=None):
    text = body or f"item {n}"
    if check:
        text += " | check: look at it"
    return mk(id=f"20261018T120000Z-code-t{n:05d}", type="task", key=None, body=text, scope=scope,
              ts=ts, category=category)


def control(kind, n, target=None, ts=NOW, scope="global", category=None, body=""):
    return mk(id=f"20261018T120000Z-code-{kind[:3]}{n:04d}", type=kind, key=None, body=body, scope=scope,
              target=target["id"] if target else None, ts=ts, category=category)


def shown(events, project=None, instance=None):
    return [l.rsplit("#", 1)[1].rstrip(")") for l in pd.section(events, project, instance)["lines"]]


def refs(*tasks):
    return [t["id"].rsplit("-", 1)[1] for t in tasks]


class Lifecycle(unittest.TestCase):
    def test_an_open_item_never_lapses(self):
        t = task(1, ts=NOW - timedelta(days=400))
        self.assertEqual(shown([t]), refs(t))

    def test_done_closes_it_everywhere(self):
        t = task(1)
        events = [t, control("done", 1, t)]
        self.assertEqual(pd.items(events), [])
        self.assertEqual(shown(events), [])

    def test_forget_deletes_it_from_views_and_search(self):
        t = task(1, body="rebuild the zebra index")
        events = [t, control("forget", 1, t)]
        self.assertEqual(pd.items(events), [])
        self.assertEqual(search.Index(events).search("zebra"), [])

    def test_archive_hides_it_but_keeps_it_listed_and_searchable(self):
        t = task(1, body="rebuild the zebra index")
        events = [t, control("archive", 1, t, ts=NOW + timedelta(hours=1))]
        self.assertEqual(shown(events), [])
        self.assertEqual([i["archived"] for i in pd.items(events)], [True])
        self.assertEqual(search.Index(events).search("zebra"), [t["id"]])

    def test_reopen_brings_it_back_and_the_latest_mark_wins(self):
        t = task(1)
        a = control("archive", 1, t, ts=NOW + timedelta(hours=1))
        r = control("reopen", 1, t, ts=NOW + timedelta(hours=2))
        a2 = control("archive", 2, t, ts=NOW + timedelta(hours=3))
        self.assertEqual(shown([t, a, r]), refs(t))
        self.assertEqual(shown([t, a, r, a2]), [])
        self.assertEqual(shown([a2, r, a, t]), [])             # order of arrival does not matter

    def test_a_check_records_when_but_changes_nothing_else(self):
        t = task(1)
        u = control("use", 1, t, ts=NOW + timedelta(days=5), body="verified")
        line = pd.section([t, u])["lines"][0]
        self.assertIn("checked 2026-10-23", line)
        self.assertEqual(shown([t, u]), refs(t))

    def test_use_of_another_entry_is_not_a_check(self):
        t, other = task(1), mk(id="20261018T120000Z-code-aaaaaa")
        u = control("use", 1, other, body="x")
        self.assertNotIn("checked", pd.section([t, other, u])["lines"][0])


class Scope(unittest.TestCase):
    def test_global_items_show_in_every_project_instance_and_chat(self):
        t = task(1)
        for project_, instance in ((None, None), ("QuizApp", "code"), ("Other", "app"), (None, "app")):
            self.assertEqual(shown([t], project_, instance), refs(t))

    def test_a_scoped_item_shows_only_in_its_scope(self):
        t = task(1, scope="project:QuizApp")
        self.assertEqual(shown([t], "QuizApp", "code"), refs(t))
        self.assertEqual(shown([t], "Other", "code"), [])
        self.assertEqual(shown([t], None, "app"), [])           # a chat has no project

    def test_rescope_one_item_by_reference(self):
        a, b = task(1), task(2)
        r = control("rescope", 1, a, scope="project:QuizApp", ts=NOW + timedelta(minutes=1))
        self.assertEqual(shown([a, b, r], "Other", "code"), refs(b))
        self.assertEqual(sorted(shown([a, b, r], "QuizApp", "code")), sorted(refs(a, b)))

    def test_rescope_a_category_covers_present_and_future_items(self):
        old = task(1, category="quiz", ts=NOW)
        new = task(2, category="quiz", ts=NOW + timedelta(days=3))
        other = task(3, category="memory")
        r = control("rescope", 1, scope="project:QuizApp", category="quiz", ts=NOW + timedelta(days=1))
        events = [old, new, other, r]
        self.assertEqual(shown(events, "Other", "code"), refs(other))
        self.assertEqual(sorted(shown(events, "QuizApp", "code")), sorted(refs(old, new, other)))

    def test_the_latest_applicable_rescope_wins_and_global_undoes_it(self):
        t = task(1, category="quiz")
        r1 = control("rescope", 1, scope="project:QuizApp", category="quiz", ts=NOW + timedelta(days=1))
        r2 = control("rescope", 2, t, scope="project:Other", ts=NOW + timedelta(days=2))
        r3 = control("rescope", 3, t, scope="global", ts=NOW + timedelta(days=3))
        self.assertEqual(shown([t, r1], "Other", "code"), [])
        self.assertEqual(shown([t, r1, r2], "Other", "code"), refs(t))
        self.assertEqual(shown([t, r1, r2], "QuizApp", "code"), [])
        self.assertEqual(shown([t, r1, r2, r3], "Whatever", "code"), refs(t))

    def test_the_line_shows_category_and_scope(self):
        t = task(1, category="quiz", scope="project:QuizApp")
        self.assertIn("[open item quiz project:QuizApp]", pd.section([t], "QuizApp", "code")["lines"][0])

    def test_rescope_does_not_leak_into_the_entry_brief(self):
        t = task(1)
        r = control("rescope", 1, t, scope="project:QuizApp")
        self.assertEqual(core.brief([t, r], [], NOW)["included"], [])


class Budget(unittest.TestCase):
    def test_budget_is_2000_tokens(self):
        self.assertEqual(pd.BUDGET_TOKENS, 2000)
        self.assertEqual(pd.BUDGET_CHARS, int(2000 * pd.CHARS_PER_TOKEN))

    def test_overflow_drops_the_oldest_activity_and_says_so(self):
        events = [task(i, ts=NOW + timedelta(minutes=i), body="x" * 380) for i in range(1, 41)]
        s = pd.section(events)
        self.assertLessEqual(s["chars"], pd.BUDGET_CHARS)
        self.assertGreater(s["hidden"], 0)
        self.assertEqual(s["shown"] + s["hidden"], 40)
        self.assertTrue(any("budget" in w and "mem archive" in w for w in s["warnings"]))
        text = "\n".join(s["lines"])
        self.assertIn("t00040", text)
        self.assertNotIn("t00001", text)

    def test_archived_items_do_not_take_budget(self):
        events = [task(i, ts=NOW + timedelta(minutes=i), body="x" * 380) for i in range(1, 41)]
        events += [control("archive", i, events[i - 1], ts=NOW + timedelta(hours=1)) for i in range(1, 38)]
        s = pd.section(events)
        self.assertEqual((s["shown"], s["hidden"]), (3, 0))

    def test_budgets_are_independent(self):
        prefs = [mk(id=f"20261018T120000Z-code-p{i:05d}", key=f"k.{i}", body="y" * 200) for i in range(30)]
        tasks = [task(i, body="z" * 300) for i in range(1, 6)]
        alone = core.brief(prefs, [], NOW, ids=True)
        both = core.brief(prefs + tasks, [], NOW, ids=True)
        self.assertEqual((alone["lines"], alone["included"], alone["chars"]),
                         (both["lines"], both["included"], both["chars"]))
        self.assertEqual(pd.section(tasks)["lines"], pd.section(prefs + tasks)["lines"])

    def test_nothing_to_show_prints_nothing(self):
        self.assertEqual(pd.render(pd.section([])), [])
        t = task(1)
        self.assertEqual(pd.render(pd.section([t, control("archive", 1, t)])), [])


class Quality(unittest.TestCase):
    def test_missing_check_is_flagged_not_hidden(self):
        s = pd.section([task(1, check=False)])
        self.assertEqual(s["shown"], 1)
        self.assertIn("no check recorded", s["lines"][0])
        self.assertTrue(any("without a check" in w for w in s["warnings"]))

    def test_line_shows_when_it_was_opened_and_its_ref(self):
        line = pd.section([task(1)])["lines"][0]
        self.assertIn("[open item]", line)
        self.assertIn("since 2026-10-18", line)
        self.assertIn("#t00001", line)

    def test_a_long_item_is_cut_and_still_has_its_ref(self):
        line = pd.section([task(1, body="q" * 2000)])["lines"][0]
        self.assertLessEqual(len(line), pd.MAX_LINE + 80)
        self.assertIn("#t00001", line)


class OtherModulesDoNotSeeTasks(unittest.TestCase):
    def test_compaction_ignores_old_tasks(self):
        self.assertEqual(core.compaction_proposals([task(1, ts=NOW - timedelta(days=300))], [], NOW), [])

    def test_brief_excludes_tasks(self):
        self.assertEqual(core.brief([task(1)], [], NOW)["included"], [])

    def test_control_events_are_never_shown_as_entries(self):
        t = task(1)
        events = [t, control("archive", 1, t), control("reopen", 2, t), control("rescope", 3, t, scope="global")]
        self.assertEqual([e["id"] for e in core.fold(events)[0]], [t["id"]])

    def test_search_finds_a_live_item(self):
        t = task(1, body="rebuild the zebra index")
        self.assertEqual(search.Index([t]).search("zebra"), [t["id"]])


class EventFormat(unittest.TestCase):
    def test_category_roundtrip(self):
        e = task(1, category="quiz")
        self.assertEqual(ev.parse(ev.render(e), e["id"])["category"], "quiz")
        self.assertIsNone(ev.parse(ev.render(task(2)), "20261018T120000Z-code-t00002")["category"])

    def test_rescope_roundtrip_keeps_scope_target_and_category(self):
        t = task(1)
        r = control("rescope", 1, t, scope="project:QuizApp", category="quiz")
        back = ev.parse(ev.render(r), r["id"])
        self.assertEqual((back["scope"], back["target"], back["category"]), ("project:QuizApp", t["id"], "quiz"))

    def test_validation(self):
        t = task(1)
        self.assertEqual(validate.check_event(control("archive", 1, t), NOW), [])
        self.assertEqual(validate.check_event(control("reopen", 1, t), NOW), [])
        self.assertTrue(validate.check_event(control("archive", 1), NOW))            # needs a target
        self.assertTrue(validate.check_event(control("reopen", 1), NOW))
        self.assertTrue(validate.check_event(control("rescope", 1, scope="project:X"), NOW))   # target or category
        self.assertEqual(validate.check_event(control("rescope", 1, t, scope="project:X"), NOW), [])
        self.assertEqual(validate.check_event(control("rescope", 1, scope="project:X", category="quiz"), NOW), [])
        self.assertTrue(validate.check_event(control("rescope", 1, t, scope="nonsense"), NOW))
        self.assertTrue(validate.check_event(mk(category="quiz"), NOW))             # only task / rescope
        self.assertTrue(validate.check_event(task(1, category="Bad Category"), NOW))
        self.assertEqual(validate.check_event(task(1, category="quiz"), NOW), [])


class Cli(Tmp):
    def stored(self, kind):
        return [e for e in ev.load(self.root)[0] if e["type"] == kind]

    def make(self, text="fix it", *extra):
        self.assertEqual(self.run_cli("task", text, "--check", "run the tests", *extra)[0], 0)
        return [t for t in self.stored("task") if t["body"].startswith(text)][0]["id"]

    def test_task_requires_a_check(self):
        with self.assertRaises(SystemExit):
            self.run_cli("task", "fix the thing")
        self.assertEqual(self.stored("task"), [])

    def test_there_is_no_days_option_any_more(self):
        with self.assertRaises(SystemExit):
            self.run_cli("task", "x", "--check", "y", "--days", "3")

    def test_task_stores_check_and_category(self):
        self.make("fix it", "--category", "quiz")
        t = self.stored("task")[0]
        self.assertIn("fix it | check: run the tests", t["body"])
        self.assertEqual(t["category"], "quiz")
        self.assertEqual(self.run_cli("task", "x", "--check", "y", "--category", "Bad One")[0], 2)

    def at(self, minutes, *argv):
        """Run a command `minutes` after the base time: 'latest wins' needs distinct moments."""
        stamp = (NOW + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.run_cli("--now", stamp, *argv)

    def test_archive_reopen_forget_done(self):
        tid = self.make()
        pending = lambda *a: self.at(60, "pending", *a)[1]
        self.assertIn("fix it", pending())
        self.at(1, "archive", tid)
        self.assertNotIn("fix it", pending())
        self.assertIn("ARCHIVED", pending("--archived"))
        self.assertIn("fix it", pending("--all"))
        self.at(2, "reopen", tid)
        self.assertIn("OPEN", pending())
        self.at(3, "forget", tid)
        self.assertNotIn("fix it", pending("--all"))
        tid2 = self.make("second")
        self.at(4, "done", tid2)
        self.assertNotIn("second", pending("--all"))

    def test_scope_by_item_and_by_category(self):
        a = self.make("alpha", "--category", "quiz")
        self.make("beta", "--category", "memory")
        self.assertEqual(self.at(1, "scope", "project:QuizApp", a)[0], 0)
        self.assertEqual(self.at(2, "scope", "project:Mem", "--category", "memory")[0], 0)
        out = self.at(60, "pending")[1]
        self.assertIn("[quiz project:QuizApp]", out)
        self.assertIn("[memory project:Mem]", out)
        self.at(3, "scope", "global", "--category", "memory")
        self.assertNotIn("project:Mem", self.at(60, "pending")[1])

    def test_scope_needs_exactly_one_target(self):
        a = self.make()
        self.assertEqual(self.run_cli("scope", "project:X")[0], 2)
        self.assertEqual(self.run_cli("scope", "project:X", a, "--category", "quiz")[0], 2)
        self.assertEqual(self.stored("rescope"), [])

    def test_brief_command_shows_the_section(self):
        self.make()
        self.assertIn("[open item]", self.run_cli("brief")[1])


class Hooks(Tmp):
    def start(self, payload=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            hooks.session_start(self.root, payload or {}, NOW, "code")
        return out.getvalue()

    def make(self, text, *extra):
        self.run_cli("task", text, "--check", "x", *extra)
        return [e for e in ev.load(self.root)[0] if e["type"] == "task" and e["body"].startswith(text)][0]["id"]

    def test_creation_rule_is_always_there_the_section_only_when_needed(self):
        empty = self.start()
        for word in ("mem task", "mem done", "mem archive", "mem forget", "mem scope"):
            self.assertIn(word, empty)
        self.assertNotIn("Open items (", empty)
        self.assertNotIn("run its check", empty)
        self.make("fix it")
        full = self.start()
        self.assertIn("Open items (", full)
        self.assertIn("fix it", full)
        self.assertIn("run its check", full)

    def test_every_project_sees_global_items_and_only_its_own_scoped_ones(self):
        self.make("everywhere")
        self.make("quiz only", "--scope", "project:QuizApp")
        elsewhere = self.start({"cwd": "/tmp/projA"})
        self.assertIn("everywhere", elsewhere)
        self.assertNotIn("quiz only", elsewhere)
        inside = self.start({"cwd": "/home/x/QuizApp"})
        self.assertIn("everywhere", inside)
        self.assertIn("quiz only", inside)

    def test_archived_items_are_not_announced(self):
        tid = self.make("parked item")
        self.run_cli("archive", tid)
        text = self.start()
        self.assertNotIn("parked item", text)
        self.assertNotIn("Open items (", text)


class Views(Tmp):
    def test_brief_view_has_the_section_before_recording_only_when_there_are_items(self):
        self.assertNotIn("## Open items", project.build(self.root, NOW, "app")["BRIEF.md"])
        self.run_cli("task", "fix it", "--check", "run the tests")
        text = project.build(self.root, NOW, "app")["BRIEF.md"]
        self.assertIn("## Open items", text)
        self.assertLess(text.index("## Open items"), text.index("## Recording"))

    def test_chat_view_hides_scope_dependent_items(self):
        self.run_cli("task", "everywhere", "--check", "x")
        self.run_cli("task", "quiz only", "--check", "x", "--scope", "project:QuizApp")
        text = project.build(self.root, NOW, "app")["BRIEF.md"]
        self.assertIn("everywhere", text)
        self.assertNotIn("quiz only", text)

    def test_review_warns_when_over_budget(self):
        for i in range(30):
            self.run_cli("task", "w" * 380 + str(i), "--check", "x")
        self.assertIn("open items exceed", project.build(self.root, NOW, "app")["REVIEW.md"])

    def test_howto_teaches_chats_the_whole_flow(self):
        how = project._howto(self.root)
        for word in ("type: task", "check:", "category", "type: done", "type: archive", "reopen", "type: forget"):
            self.assertIn(word, how)

    def test_views_are_stable_when_nothing_changes(self):
        self.run_cli("task", "fix it", "--check", "run the tests")
        self.assertEqual(project.build(self.root, NOW, "app"), project.build(self.root, NOW, "app"))


class Calibration(unittest.TestCase):
    def test_entry_lines_are_counted_before_the_first_section_only(self):
        spec = importlib.util.spec_from_file_location("calibrate", ROOT / "scripts" / "calibrate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        brief = "# Memory brief\n\nstamp\n\n- a entry\n- b entry\n\n## Open items\n- [open item] long long long\n\n## Recording\n- x\n"
        self.assertEqual(mod.entry_lines_chars(brief), len("- a entry") + 1 + len("- b entry") + 1)
        self.assertEqual(mod.open_items_chars(brief),
                         len("## Open items") + 1 + len("- [open item] long long long") + 1 + 1)


if __name__ == "__main__":
    unittest.main()
