import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mem import cli, events as ev, harvest, hooks, install, project, sync, validate

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)
ISO = "2026-10-18T12:00:00Z"


def mk(id="20261018T120000Z-code-aaaaaa", type="pref", body="use pnpm", **kw):
    base = dict(id=id, ts=NOW, type=type, scope="global", key="pm", body=body,
                instance="code", owner="user", supersedes=[], target=None, signal=None)
    return {**base, **kw}


class Tmp(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        self.root = Path(self._d.name) / "repo"
        for d in ("events", "usage", "views", "quarantine"):
            (self.root / d).mkdir(parents=True)

    def run_cli(self, *argv, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.run(["--root", str(self.root), "--now", ISO, *argv], io.StringIO(stdin))
        return code, out.getvalue(), err.getvalue()


class EventFileTests(Tmp):
    def test_roundtrip_and_offset_normalised(self):
        text = ev.render(mk(supersedes=["a", "b"]))
        got = ev.parse(text, "20261018T120000Z-code-aaaaaa")
        self.assertEqual((got["type"], got["key"], got["supersedes"]), ("pref", "pm", ["a", "b"]))
        off = ev.parse("---\ntype: note\nts: 2026-10-18T09:00:00-03:00\n---\nx", "n")
        self.assertEqual(off["ts"], NOW)

    def test_defaults_from_file_name_and_unknown_keys_ignored(self):
        got = ev.parse("---\ntype: note\nfuture_field: 1\n---\nhello", "20261018T120000Z-app-ab12cd")
        self.assertEqual((got["instance"], got["ts"], got["scope"]), ("app", NOW, "global"))

    def test_unreadable_files_raise(self):
        for text in ("no frontmatter", "---\nnot a pair\n---\nx", "---\ntype: note\n---\nx"):
            with self.assertRaises(ValueError):
                ev.parse(text, "plain")

    def test_write_is_atomic_and_idempotent(self):
        path = ev.write(self.root, mk())
        self.assertEqual(path.parent, self.root / "events/2026/10")
        before = path.read_text()
        ev.write(self.root, mk(body="different"))
        self.assertEqual(path.read_text(), before)
        self.assertEqual([p.name for p in path.parent.iterdir()], [path.name])

    def test_bad_usage_line_never_blocks_the_rest(self):
        (self.root / "usage/2026-10-18-code.jsonl").write_text(
            'garbage\n{"target": "a", "ts": "2026-10-18T12:00:00Z"}\n{"x": 1}\n')
        self.assertEqual([u["target"] for u in ev.load_usage(self.root)], ["a"])


class ValidateTests(Tmp):
    def reasons(self, **kw):
        return validate.check_event(mk(**kw), NOW)

    def test_clean_event_passes(self):
        self.assertEqual(self.reasons(), [])

    def test_privacy_boundary(self):
        cases = {
            "ghp_" + "a" * 30: "secret",
            "write to giovanni@example.com": "email",
            "ligue +55 11 91234-5678": "phone",
            "cpf 123.456.789-09": "CPF",
            "o paciente chegou": "health",
            "patient history": "health",
        }
        for body, label in cases.items():
            self.assertTrue(any(label in r for r in self.reasons(body=body)), body)

    def test_technical_words_and_plain_numbers_pass(self):
        for body in ("run the diagnostics tool", "date 20261018 and id 12345678", "use bun, not pnpm"):
            self.assertEqual(self.reasons(body=body), [], body)

    def test_structure_rules(self):
        self.assertTrue(self.reasons(type="bogus"))
        self.assertTrue(self.reasons(key="Bad Key"))
        self.assertTrue(self.reasons(scope="nowhere"))
        self.assertTrue(self.reasons(body=""))
        self.assertTrue(self.reasons(body="x" * 1300))
        self.assertTrue(self.reasons(ts=NOW + timedelta(days=3)))
        self.assertTrue(self.reasons(type="feedback", body="", target=None))
        self.assertTrue(self.reasons(type="feedback", body="", target="a", signal="great"))
        self.assertEqual(self.reasons(type="feedback", body="", target="a", signal="stale"), [])

    def test_quarantine_moves_files_wherever_they_were_written(self):
        ev.write(self.root, mk())
        ev.write(self.root, mk(id="20261018T120001Z-app-bbbbbb", body="the paciente list"))
        odd = self.root / "events/misplaced/20261018T120002Z-app-cccccc.md"
        odd.parent.mkdir()
        odd.write_text("---\ntype: pref\nts: 2026-10-18T12:00:02Z\n---\nghp_" + "b" * 30 + "\n")
        (self.root / "events/broken.md").write_text("not an event")
        moved = validate.quarantine(self.root, NOW)
        self.assertEqual(len(moved), 3)
        self.assertEqual(len(list((self.root / "quarantine").glob("*.reason"))), 3)
        events, invalid = validate.load_checked(self.root, NOW)
        self.assertEqual((len(events), invalid), (1, []))


class ProjectTests(Tmp):
    def seed(self):
        ev.write(self.root, mk())
        ev.write(self.root, mk(id="20261018T120001Z-code-bbbbbb", type="fact", key=None,
                               body="the sync script lives at tools/sync.sh", owner="agent"))
        (self.root / "mem.json").write_text(json.dumps({"repo": "me/mem"}))

    def test_build_is_deterministic_and_stable_once_written(self):
        self.seed()
        texts = project.build(self.root, NOW)
        self.assertEqual(texts, project.build(self.root, NOW))
        self.assertEqual(sorted(project.write_views(self.root, texts)),
                         ["BRIEF.md", "PREFERENCES.md", "REVIEW.md"])
        self.assertEqual(project.write_views(self.root, texts), [])
        self.assertEqual(self.run_cli("build", "--check")[0], 0)

    def test_check_fails_when_a_view_was_edited_by_hand(self):
        self.seed()
        project.write_views(self.root, project.build(self.root, NOW))
        (self.root / "views/BRIEF.md").write_text("tampered")
        code, out, _ = self.run_cli("build", "--check")
        self.assertEqual(code, 1)
        self.assertIn("views/BRIEF.md", out)
        self.run_cli("build")
        self.assertEqual(self.run_cli("build", "--check")[0], 0)

    def test_brief_content(self):
        self.seed()
        brief = project.build(self.root, NOW)["BRIEF.md"]
        self.assertIn("never authorizes", brief)
        self.assertIn("[pm] use pnpm", brief)
        self.assertIn("`me/mem`", brief)
        self.assertIn("get_file_contents", brief)
        self.assertNotIn("20261018T120000Z-code-aaaaaa", brief)  # ids only for Code

    def test_brief_says_when_entries_did_not_fit(self):
        for i in range(6):
            ev.write(self.root, mk(id=f"2026101812000{i}Z-code-aaaaa{i}", type="fact", key=None,
                                   owner="agent", body=f"fact number {i} " + "x" * 600))
        brief = project.build(self.root, NOW, budget=1500)["BRIEF.md"]
        self.assertRegex(brief, r"\(\d+ more entries did not fit")

    def test_review_is_empty_then_lists_quarantine(self):
        self.seed()
        self.assertIn("Nothing needs a decision", project.build(self.root, NOW)["REVIEW.md"])
        (self.root / "events/broken.md").write_text("junk")
        review = project.build(self.root, NOW)["REVIEW.md"]
        self.assertIn("Quarantined events", review)
        self.assertIn("events/broken.md", review)

    def test_preferences_view_shows_restatements(self):
        ev.write(self.root, mk())
        ev.write(self.root, mk(id="20261018T120005Z-code-bbbbbb", body="I always use pnpm"))
        self.assertIn("restated 1x", project.build(self.root, NOW)["PREFERENCES.md"])


class PromoteTests(Tmp):
    def harvested(self, project_name, hours, text="Always use pnpm.", minutes=0):
        c = harvest.candidates([dict(text=text, ts=NOW - timedelta(hours=hours, minutes=-minutes),
                                     project=project_name, source="user")])[0]
        return dict(id=harvest.event_id(c), ts=c["ts"], type="pref", scope=f"project:{project_name}",
                    key=c["key"], body=c["text"], instance="harvester", owner="harvester",
                    supersedes=[], target=None, signal=None)

    def test_two_projects_promote_once(self):
        for e in (self.harvested("a", 50), self.harvested("b", 5)):
            ev.write(self.root, e)
        self.assertEqual(self.run_cli("promote")[0], 0)
        events, _ = validate.load_checked(self.root, NOW)
        glob = [e for e in events if e["scope"] == "global"]
        self.assertEqual(len(glob), 1)
        self.assertEqual(self.run_cli("promote")[1], "")
        self.assertEqual(len(list((self.root / "events").rglob("*.md"))), 3)

    def test_same_sentence_in_one_hour_is_one_project(self):
        for e in (self.harvested("a", 3), self.harvested("b", 3, minutes=20)):
            ev.write(self.root, e)
        self.assertEqual(harvest.promote(validate.load_checked(self.root, NOW)[0], NOW), [])

    def test_existing_global_entry_blocks_promotion(self):
        for e in (self.harvested("a", 50), self.harvested("b", 5)):
            ev.write(self.root, e)
        key = self.harvested("a", 1)["key"]
        ev.write(self.root, mk(key=key, body="use pnpm"))
        self.assertEqual(harvest.promote(validate.load_checked(self.root, NOW)[0], NOW), [])


class HookTests(Tmp):
    def call(self, fn, payload, **kw):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = fn(self.root, payload, NOW, "code", **kw)
        return code, out.getvalue()

    def test_prompt_hook_captures_a_preference_silently(self):
        payload = {"prompt": "From now on always use the full path for sync.sh.",
                   "cwd": str(self.root / "projA")}
        code, out = self.call(hooks.prompt, payload)
        self.assertEqual((code, out), (0, ""))
        events, _ = validate.load_checked(self.root, NOW)
        self.assertEqual([(e["scope"], e["instance"]) for e in events], [("project:projA", "harvester")])
        self.call(hooks.prompt, payload)  # firing twice writes the same file
        self.assertEqual(len(ev.load(self.root)[0]), 1)

    def test_prompt_hook_global_when_explicit(self):
        self.call(hooks.prompt, {"prompt": "In all my projects, always use pnpm.", "cwd": "/tmp/x"})
        self.assertEqual(ev.load(self.root)[0][0]["scope"], "global")

    def test_prompt_hook_ignores_noise_and_private_text_and_never_fails(self):
        for payload in ({"prompt": "What time is it?"}, {"prompt": "Always send it to bob@example.com."},
                        {}, {"prompt": None}, {"prompt": 5}):
            self.assertEqual(self.call(hooks.prompt, payload)[0], 0)
        self.assertEqual(ev.load(self.root)[0], [])

    def test_session_start_prints_brief_and_how_to_record(self):
        ev.write(self.root, mk())
        code, out = self.call(hooks.session_start, {"cwd": "/tmp/projA"})
        self.assertEqual(code, 0)
        self.assertIn("[pm] use pnpm (20261018T120000Z-code-aaaaaa)", out)
        self.assertIn("mem add --type pref --owner user", out)
        self.assertIn("memory may be stale", out)  # not a git clone: pull is skipped

    def test_session_start_flags_pending_decisions(self):
        (self.root / "events/broken.md").write_text("junk")
        self.assertIn("1 item(s) wait for Giovanni", self.call(hooks.session_start, {})[1])

    def test_read_payload_tolerates_garbage(self):
        self.assertEqual(hooks.read_payload(io.StringIO("not json")), {})
        self.assertEqual(hooks.read_payload(io.StringIO("[1]")), {})


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        base = Path(self._d.name)
        self.remote, self.a, self.b = base / "r.git", base / "a", base / "b"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.remote), str(self.a)], check=True,
                       capture_output=True)
        for d in ("events", "usage"):
            (self.a / d).mkdir()
            (self.a / d / ".gitkeep").write_text("")
        git(self.a, "config", "user.email", "t@t")
        git(self.a, "config", "user.name", "t")
        git(self.a, "add", ".")
        git(self.a, "commit", "-qm", "init")
        git(self.a, "push", "-q", "-u", "origin", "HEAD:main")
        subprocess.run(["git", "clone", "-q", str(self.remote), str(self.b)], check=True,
                       capture_output=True)
        git(self.b, "config", "user.email", "t@t")
        git(self.b, "config", "user.name", "t")

    def test_event_travels_between_clones_without_force(self):
        ev.write(self.a, mk())
        self.assertEqual(sync.push(self.a), "pushed")
        self.assertEqual(sync.pull(self.b), "pulled")
        self.assertEqual(len(ev.load(self.b)[0]), 1)
        self.assertEqual(sync.push(self.a), "nothing to push")

    def test_both_sides_add_events_and_push_rebases(self):
        ev.write(self.a, mk())
        ev.write(self.b, mk(id="20261018T120009Z-app-bbbbbb", key="other", body="b side"))
        self.assertEqual(sync.push(self.a), "pushed")
        self.assertEqual(sync.push(self.b), "pushed")
        git(self.a, "pull", "-q", "--ff-only")
        self.assertEqual(len(ev.load(self.a)[0]), 2)

    def test_offline_keeps_the_commit_and_does_not_raise(self):
        ev.write(self.a, mk())
        git(self.a, "remote", "set-url", "origin", str(self.remote) + "-gone")
        self.assertTrue(sync.push(self.a, retries=1, sleep=lambda s: None).startswith("push failed"))
        git(self.a, "remote", "set-url", "origin", str(self.remote))
        self.assertEqual(sync.push(self.a), "pushed")

    def test_sync_never_forces(self):
        source = Path(sync.__file__).read_text()
        self.assertNotIn("--force", source)
        self.assertNotIn("-f\"", source)

    def test_pull_outside_a_clone_is_skipped_not_raised(self):
        self.assertTrue(sync.pull(self.a.parent / "missing").startswith("pull skipped"))


class InstallTests(Tmp):
    def test_merge_idempotent_and_removable(self):
        settings = self.root / "settings.json"
        settings.write_text(json.dumps({"model": "x", "hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "other-tool"}]}]}}))
        install.apply(settings, "/m/bin/mem")
        install.apply(settings, "/m/bin/mem")
        data = json.loads(settings.read_text())
        self.assertEqual(data["model"], "x")
        stop = [h["command"] for e in data["hooks"]["Stop"] for h in e["hooks"]]
        self.assertEqual(sorted(stop), ["other-tool", "python3 /m/bin/mem hook-stop"])
        self.assertEqual(set(data["hooks"]), {"Stop", "SessionStart", "UserPromptSubmit"})
        self.assertTrue(list(self.root.glob("settings.json.bak-*")))
        install.apply(settings, "/m/bin/mem", remove=True)
        data = json.loads(settings.read_text())
        self.assertEqual(data["hooks"], {"Stop": [{"hooks": [{"type": "command", "command": "other-tool"}]}]})

    def test_creates_settings_and_cleans_up_when_empty(self):
        settings = self.root / "new" / "settings.json"
        install.apply(settings, "/m/bin/mem")
        self.assertIn("hook-session-start", settings.read_text())
        install.apply(settings, "/m/bin/mem", remove=True)
        self.assertEqual(json.loads(settings.read_text()), {})


class CliFlowTests(Tmp):
    def ids(self):
        return sorted(p.stem for p in (self.root / "events").rglob("*.md"))

    def test_add_refuses_private_text(self):
        code, _, err = self.run_cli("add", "--key", "k", "call 11 91234-5678 now")
        self.assertEqual(code, 2)
        self.assertIn("phone number", err)
        self.assertEqual(self.ids(), [])

    def test_stdin_task_claim_done_and_use(self):
        self.assertEqual(self.run_cli("add", "--type", "fact", "-", stdin="from stdin\n")[0], 0)
        self.run_cli("task", "migrate memory")
        task = [e for e in ev.load(self.root)[0] if e["type"] == "task"][0]["id"]
        self.assertEqual(self.run_cli("claim", task)[0], 0)
        self.assertEqual(self.run_cli("use", task)[0], 0)
        self.assertTrue(list((self.root / "usage").glob("2026-10-18-code.jsonl")))
        self.assertIn("migrate memory", self.run_cli("brief")[1])
        self.run_cli("done", task)
        self.assertNotIn("migrate memory", self.run_cli("brief")[1])

    def test_feedback_forget_and_search(self):
        self.run_cli("add", "--type", "fact", "--key", "qwen", "Qwen runs on llama-server port 8080")
        target = ev.load(self.root)[0][0]["id"]
        self.assertEqual(self.run_cli("search", "llama")[1].split(), [target])
        self.run_cli("feedback", target, "wrong")
        self.assertNotIn("Qwen", self.run_cli("brief")[1])
        self.assertIn(target, project.build(self.root, NOW)["REVIEW.md"])
        self.run_cli("forget", target)
        self.assertEqual(self.run_cli("search", "llama")[1], "")

    def test_check_and_quarantine_commands(self):
        (self.root / "events/broken.md").write_text("junk")
        self.assertEqual(self.run_cli("check")[0], 1)
        self.assertIn("quarantined", self.run_cli("quarantine")[1])
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_quarantined_files_stay_visible_until_dismissed(self):
        (self.root / "events/broken.md").write_text("junk")
        self.run_cli("quarantine")
        self.assertEqual(self.run_cli("check")[0], 0)  # the log itself is clean again
        self.assertIn("broken.md", project.build(self.root, NOW)["REVIEW.md"])
        self.assertEqual(self.run_cli("dismiss", "broken")[0], 0)
        self.assertIn("Nothing needs a decision", project.build(self.root, NOW)["REVIEW.md"])
        self.assertEqual(self.run_cli("dismiss", "broken")[0], 1)

    def test_compact_proposes_then_applies(self):
        old = mk(id="20260801T120000Z-code-aaaaaa", type="note", key=None, owner="agent",
                 ts=datetime(2026, 8, 1, 12, tzinfo=timezone.utc), body="Fixed /etc/foo.conf because E-42.")
        ev.write(self.root, old)
        self.assertIn("would write", self.run_cli("compact")[1])
        self.assertEqual(len(list((self.root / "events").rglob("*.md"))), 1)
        self.assertIn("wrote", self.run_cli("compact", "--apply")[1])
        self.assertEqual(len(list((self.root / "events").rglob("*.md"))), 2)
        self.assertEqual(self.run_cli("compact", "--apply")[1], "")


if __name__ == "__main__":
    unittest.main()
