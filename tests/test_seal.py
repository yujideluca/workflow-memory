"""Private entries: the text of an open item, a use note or a note is encrypted in its file (ADR-0009).

The repository is public. What must hold: the plain text never reaches a file under events/ or views/; a reader
without the key (the CI job, the chat app) still gets a valid entry with a placeholder text; and the views are the
same whether or not the builder has the key, so the laptop and the CI job never disagree about them.
"""
import importlib.util
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from mem import core, events as ev, pendency as pd, project, validate
from tests.test_system import Tmp, NOW, mk

HAVE = importlib.util.find_spec("cryptography") is not None
SECRET = "Call the translator about the sworn translation | check: look in the mail"


@unittest.skipUnless(HAVE, "the cryptography package is not installed here")
class Seal(Tmp):
    def setUp(self):
        super().setUp()
        self.key = Path(self._d.name) / "key"
        self.none = Path(self._d.name) / "no-key-here"
        self.use_key(self.key)
        self.assertEqual(self.run_cli("key", "init")[0], 0)
        (self.root / "mem.json").write_text(json.dumps({"seal": ["task", "use", "note"]}))

    def use_key(self, path):
        p = mock.patch.dict(os.environ, {"MEM_KEY_FILE": str(path)})
        p.start()
        self.addCleanup(p.stop)

    def files(self, sub="events"):
        return "\n".join(p.read_text() for p in sorted((self.root / sub).rglob("*.md")))

    def test_key_init_makes_a_private_file_once(self):
        self.assertEqual(self.key.stat().st_mode & 0o777, 0o600)
        before = self.key.read_bytes()
        self.assertEqual(self.run_cli("key", "init")[0], 0)
        self.assertEqual(self.key.read_bytes(), before, "an existing key is never replaced")

    def test_a_task_is_written_encrypted_and_read_back_with_the_key(self):
        code, _, err = self.run_cli("task", "--check", "look in the mail", "Call the translator about the sworn translation")
        self.assertEqual(code, 0, err)
        self.assertIn("sealed: v1", self.files())
        self.assertNotIn("translator", self.files())
        events, bad = ev.load(self.root)
        self.assertEqual(bad, [])
        self.assertIn("translator", events[0]["body"])
        self.assertTrue(events[0]["sealed"])
        self.assertIn("translator", self.run_cli("pending")[1])

    def test_a_rule_stays_readable_by_everyone(self):
        self.assertEqual(self.run_cli("add", "--type", "pref", "--key", "pm", "use pnpm")[0], 0)
        self.assertIn("use pnpm", self.files())
        self.assertNotIn("sealed", self.files())

    def test_without_the_key_the_entry_is_valid_and_shows_a_placeholder(self):
        self.run_cli("task", "--check", "look in the mail", "Call the translator")
        for other in (self.none, None):
            if other is None:  # a different key: must not crash, must not decrypt
                other = Path(self._d.name) / "other"
                self.use_key(other)
                self.run_cli("key", "init")
            self.use_key(other)
            events, invalid = validate.load_checked(self.root, NOW)
            self.assertEqual(invalid, [])
            self.assertEqual(events[0]["body"], ev.MASK)
            self.assertEqual(pd.section(events)["warnings"], [])

    def test_without_the_key_nothing_private_is_written(self):
        self.use_key(self.none)
        code, out, err = self.run_cli("task", "--check", "x", "Call the translator")
        self.assertEqual(code, 2)
        self.assertIn("key", err)
        self.assertEqual(self.files(), "")

    def test_views_never_hold_the_text_and_do_not_depend_on_the_key(self):
        self.run_cli("task", "--check", "look in the mail", "Call the translator")
        self.run_cli("task", "--check", "look in the mail", "Call the translator again")
        self.run_cli("add", "--type", "pref", "--key", "pm", "use pnpm")
        with_key = project.build(self.root, NOW)
        self.assertNotIn("translator", "\n".join(with_key.values()))
        self.assertIn(ev.MASK.split(" | ")[0], with_key["BRIEF.md"])
        self.assertNotIn("Near-duplicate", with_key["REVIEW.md"])
        self.use_key(self.none)
        self.assertEqual(project.build(self.root, NOW), with_key)

    def test_a_private_entry_is_never_copied_into_a_digest_or_compared(self):
        old = NOW.replace(year=NOW.year - 1)
        notes = [dict(mk(id=f"20251018T120000Z-code-n{n:05d}", type="note", key=None, body=SECRET, ts=old), sealed=True)
                 for n in range(2)]
        self.assertEqual(core.compaction_proposals(notes, [], NOW), [])
        self.assertEqual(core.near_duplicates(notes), [])
        plain = [dict(n, sealed=False) for n in notes]
        self.assertTrue(core.compaction_proposals(plain, [], NOW))

    def test_a_private_entry_cannot_carry_a_key(self):
        e = dict(mk(type="task", key="translation", body=SECRET), sealed=True)
        self.assertTrue(any("private" in w for w in validate.check_event(e, NOW)))

    def test_a_use_note_is_encrypted_too(self):
        self.run_cli("add", "--type", "pref", "--key", "pm", "use pnpm")
        ref = core.ref(ev.load(self.root)[0][0]["id"])
        code, _, err = self.run_cli("use", ref, "--note", "asked the translator")
        self.assertEqual(code, 0, err)
        self.assertNotIn("translator", self.files())


class WithoutTheLibrary(Tmp):
    def test_a_sealed_file_is_read_as_a_placeholder_where_nothing_can_decrypt(self):
        text = "---\ntype: task\nsealed: v1\nts: 2026-10-18T12:00:00Z\n---\ngAAAAABnot-a-real-token\n"
        with mock.patch.dict(os.environ, {"MEM_KEY_FILE": str(Path(self._d.name) / "none")}):
            e = ev.parse(text, "20261018T120000Z-code-aaaaaa")
        self.assertEqual((e["body"], e["sealed"]), (ev.MASK, True))
        self.assertEqual(validate.check_event(dict(e, owner="agent"), NOW), [])

    def test_a_memory_that_seals_nothing_writes_plain_files_as_before(self):
        self.assertEqual(self.run_cli("task", "--check", "x", "plain item")[0], 0)
        self.assertIn("plain item", "\n".join(p.read_text() for p in (self.root / "events").rglob("*.md")))
