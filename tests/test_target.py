"""A command that acts on one entry (forget, done, archive, reopen, claim, feedback) must name exactly one.

Found 2026-11-18: `mem forget 9ba9a0` wrote a forget event although seven entries end with 9ba9a0, and
`mem forget 225bf6` wrote one although no entry has that reference. Both said nothing and changed nothing.
"""
from mem import events as ev
from tests.test_system import Tmp, NOW, mk


class Target(Tmp):
    def put(self, event_id, **kw):
        e = mk(id=event_id, **kw)
        p = self.root / "events" / "2026" / "10" / f"{event_id}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(ev.render(e))

    def count(self):
        return len(list((self.root / "events").rglob("*.md")))

    def test_an_unknown_reference_is_refused_and_writes_nothing(self):
        self.put("20261018T110000Z-code-aaaaaa", key="one")
        for cmd in (["forget", "zzzzzz"], ["done", "zzzzzz"], ["archive", "zzzzzz"], ["feedback", "zzzzzz", "wrong"]):
            code, _, err = self.run_cli(*cmd)
            self.assertEqual(code, 2, cmd)
            self.assertIn("no entry", err)
        self.assertEqual(self.count(), 1)

    def test_a_reference_shared_by_several_entries_is_refused_with_their_full_names(self):
        self.put("20261018T110000Z-harvester-aaaaaa", key="one", scope="project:a")
        self.put("20261018T110500Z-harvester-aaaaaa", key="one", scope="project:b")
        code, _, err = self.run_cli("forget", "aaaaaa")
        self.assertEqual(code, 2)
        self.assertIn("20261018T110000Z-harvester-aaaaaa", err)
        self.assertIn("20261018T110500Z-harvester-aaaaaa", err)
        self.assertEqual(self.count(), 2)

    def test_the_full_name_and_the_hash_form_still_work(self):
        self.put("20261018T110000Z-harvester-aaaaaa", key="one", scope="project:a")
        self.put("20261018T110500Z-harvester-aaaaaa", key="one", scope="project:b")
        self.put("20261018T110600Z-code-bbbbbb", key="two")
        self.assertEqual(self.run_cli("forget", "20261018T110000Z-harvester-aaaaaa")[0], 0)
        self.assertEqual(self.run_cli("forget", "#bbbbbb")[0], 0)
        self.assertEqual(self.count(), 5)
