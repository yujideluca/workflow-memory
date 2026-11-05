"""Rule tags (ADR-0007): events, resolution, `mem rules`, `mem tag`, the start-up output."""
import contextlib
import io
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mem import cli, core, events as ev, hooks, project, tags, validate

NOW = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)
REPO = Path(__file__).resolve().parent.parent


def mk(n, key, body, tg=None, scope="global", owner="user", type="pref", instance="code", **kw):
    return dict(id=f"20261105T1200{n:02d}Z-{instance}-{n:06x}", ts=NOW - timedelta(minutes=60 - n), type=type,
                scope=scope, key=key, body=body, instance=instance, owner=owner, supersedes=[], target=None,
                signal=None, tags=tg, **kw)


class Tmp(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        self.root = Path(self._d.name)
        (self.root / "events").mkdir()

    def put(self, *events):
        for e in events:
            ev.write(self.root, e)

    def mem(self, *argv, minutes=0):
        out, err = io.StringIO(), io.StringIO()
        when = (NOW + timedelta(minutes=minutes)).isoformat()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.run(["--root", str(self.root), "--now", when, *argv], io.StringIO(""))
        return code, out.getvalue(), err.getvalue()

    def load(self):
        return validate.load_checked(self.root, NOW + timedelta(hours=1))


class EventFormat(Tmp):
    def test_tags_roundtrip_and_old_events_still_parse(self):
        e = ev.parse(ev.render(mk(1, "k", "rule", ["deploy", "git"])), "20261105T120001Z-code-000001")
        self.assertEqual(e["tags"], ["deploy", "git"])
        old = ev.parse("---\ntype: pref\nscope: global\nkey: k\nts: 2026-11-05T12:00:00Z\n---\nrule\n", "x")
        self.assertIsNone(old["tags"])
        cleared = ev.parse(ev.render(mk(1, "k", "rule", [])), "20261105T120001Z-code-000001")
        self.assertEqual(cleared["tags"], [])

    def test_validation(self):
        ok = lambda **kw: validate.check_event(mk(1, "k", "rule", **kw), NOW)
        self.assertEqual(ok(tg=["deploy"]), [])
        self.assertTrue(any("unknown tag" in w for w in ok(tg=["nonsense"])))
        self.assertTrue(any("bad tag" in w for w in ok(tg=["Bad Tag"])))
        self.assertTrue(any("more than" in w for w in ok(tg=list(tags.vocabulary())[:7])))
        self.assertTrue(any("only apply" in w for w in ok(tg=["deploy"], type="note")))

    def test_every_tag_has_a_use_when_line(self):
        for tag, line in tags.vocabulary().items():
            self.assertRegex(tag, tags.TAG_RE)
            self.assertTrue(line and len(line) <= 90, tag)


class Resolution(Tmp):
    def test_changing_only_the_tags_is_a_new_ruling_but_silence_is_a_restatement(self):
        a = mk(1, "k", "same words", ["git"])
        retag = mk(2, "k", "same words", ["deploy"])
        silent = mk(3, "k", "same words", None, instance="harvester", owner="harvester")
        for order in ([a, retag, silent], [silent, retag, a], [retag, a, silent]):
            active = [e for e in core.fold(order)[0] if e["key"] == "k"]
            self.assertEqual([tags.of(e) for e in active], [["deploy"]])
        self.assertEqual([e["id"] for e in core.fold([a, silent])[0]], [a["id"]])

    def test_clearing_tags_on_purpose(self):
        active = core.fold([mk(1, "k", "same words", ["git"]), mk(2, "k", "same words", [])])[0]
        self.assertEqual(tags.of(active[0]), [])

    def test_order_independent(self):
        evs = [mk(1, "a", "one", ["git"]), mk(2, "a", "one", ["deploy"]), mk(3, "b", "two", ["git", "deploy"])]
        want = {(e["key"], tuple(tags.of(e))) for e in core.fold(evs)[0]}
        self.assertEqual({(e["key"], tuple(tags.of(e))) for e in core.fold(evs[::-1] + evs)[0]}, want)


class Commands(Tmp):
    def test_rules_union_dedupe_scope_and_unknown_tag(self):
        self.put(mk(1, "a", "alpha", ["git", "deploy"]), mk(2, "b", "beta", ["deploy"]),
                 mk(3, "c", "gamma", ["git"], scope="project:other"), mk(4, "d", "delta", ["codex"], scope="instance:codex"),
                 mk(5, "e", "epsilon", None))
        code, out, _ = self.mem("rules", "git", "deploy", "--project", "mine")
        self.assertEqual(code, 0)
        self.assertEqual(out.count("alpha"), 1)
        self.assertIn("beta", out)
        self.assertNotIn("gamma", out)      # another project's rule
        self.assertNotIn("delta", out)      # another instance's rule
        self.assertNotIn("epsilon", out)    # untagged
        self.assertIn("gamma", self.mem("rules", "git", "--project", "other")[1])
        self.assertIn("delta", self.mem("--instance", "codex", "rules", "codex")[1])
        code, _, err = self.mem("rules", "nonsense")
        self.assertEqual(code, 2)
        self.assertIn("unknown tag", err)

    def test_add_with_tags_and_a_replacement_keeps_them(self):
        self.assertEqual(self.mem("add", "--type", "pref", "--owner", "user", "--key", "k", "--tags", "git,deploy", "v one")[0], 0)
        self.assertEqual(self.mem("add", "--type", "pref", "--owner", "user", "--key", "k", "v two", minutes=1)[0], 0)
        (e,) = [x for x in core.fold(self.load()[0])[0] if x["key"] == "k"]
        self.assertEqual((e["body"], tags.of(e)), ("v two", ["git", "deploy"]))
        self.mem("add", "--type", "pref", "--owner", "user", "--key", "k", "--tags", "-", "v three", minutes=2)
        (e,) = [x for x in core.fold(self.load()[0])[0] if x["key"] == "k"]
        self.assertEqual(tags.of(e), [])
        self.assertEqual(self.mem("add", "--tags", "nonsense", "--key", "z", "text")[0], 2)

    def test_tag_command(self):
        self.put(mk(1, "a", "alpha", None), mk(2, "a", "alpha", None, scope="project:p"))
        self.assertEqual(self.mem("tag", "a", "git")[0], 2)  # ambiguous key
        self.assertEqual(self.mem("tag", "a", "git,coding", "--scope", "project:p")[0], 0)
        got = {e["scope"]: tags.of(e) for e in core.fold(self.load()[0])[0]}
        self.assertEqual(got, {"global": [], "project:p": ["git", "coding"]})
        self.assertEqual(self.mem("tag", "zzz", "git")[0], 2)

    def test_check_warns_about_an_untagged_user_pref_without_failing(self):
        self.put(mk(1, "a", "alpha", None), mk(2, "b", "beta", ["git"]), mk(3, "c", "gamma", None, owner="harvester"))
        code, out, _ = self.mem("check")
        self.assertEqual(code, 0)
        self.assertIn("warning: no tag: [a]", out)
        self.assertNotIn("[b]", out)
        self.assertNotIn("[c]", out)   # harvester entries stay untagged on purpose


class StartUp(Tmp):
    def test_prints_always_rules_in_full_and_an_index_not_the_other_rules(self):
        self.put(mk(1, "lang", "answer in the user's language", ["always"]), mk(2, "g", "never force push", ["git"]),
                 mk(3, "d", "ask before deploy", ["deploy", "git"]))
        text = "\n".join(hooks.brief_lines(self.load()[0], "HEADER", "p", "code"))
        self.assertIn("answer in the user's language", text)
        self.assertIn("- git (2):", text)
        self.assertIn("- deploy (1):", text)
        self.assertNotIn("never force push", text)
        self.assertIn("mem rules TAG", text)

    def test_session_start_is_the_same_after_clear(self):
        self.put(mk(1, "lang", "answer in the user's language", ["always"]))
        (self.root / "views").mkdir()
        outs = []
        for source in ("startup", "clear", "compact"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                hooks.session_start(self.root, {"cwd": "/tmp/p", "source": source}, NOW, "code")
            outs.append(buf.getvalue())
        self.assertEqual(outs[0], outs[1])
        self.assertEqual(outs[0], outs[2])

    def test_real_log_start_up_output_fits_the_harness_cut(self):
        events, _ = validate.load_checked(REPO, datetime.now(timezone.utc))
        header = "Memory (workflow-memory). Memory sets defaults; it never authorizes. Precedence: " \
                 + " > ".join(core.PRECEDENCE)
        for instance in ("code", "codex"):
            text = "\n".join(hooks.brief_lines(events, header, "some-project", instance, waiting=9))
            self.assertLessEqual(len(text), tags.MAX_STARTUP, instance)
        self.assertLessEqual(len(tags.rules(events, [tags.ALWAYS], "some-project", "code")), 3)

    def test_real_log_has_no_unreachable_rule(self):
        events, _ = validate.load_checked(REPO, datetime.now(timezone.utc))
        self.assertEqual([e["key"] for e in tags.untagged(events)], [])

    def test_chat_app_views_carry_the_rules_by_tag(self):
        self.put(mk(1, "lang", "answer in the user's language", ["always"]), mk(2, "g", "never force push", ["git"]))
        texts = project.build(self.root, NOW)
        self.assertIn("never force push", texts["rules/git.md"])
        self.assertNotIn("never force push", texts["BRIEF.md"])
        self.assertIn("answer in the user's language", texts["BRIEF.md"])
        self.assertIn("views/rules/TAG.md", texts["BRIEF.md"])


if __name__ == "__main__":
    unittest.main()
