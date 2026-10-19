import random
import unittest
from datetime import datetime, timedelta, timezone

from mem import core as r

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def ev(id, type="fact", days_ago=0, scope="global", key=None, body="x",
       instance="code", supersedes=(), **extra):
    return dict(id=id, type=type, ts=NOW - timedelta(days=days_ago), scope=scope,
                key=key, body=body, instance=instance, supersedes=list(supersedes),
                **extra)


def use(target, days_ago=0):
    return dict(target=target, ts=NOW - timedelta(days=days_ago))


class FoldTests(unittest.TestCase):
    def test_order_independent_and_idempotent(self):
        events = [ev("a", key="k", days_ago=3, body="old"),
                  ev("b", key="k", days_ago=1, body="new"),
                  ev("c", days_ago=2)]
        want = [e["id"] for e in r.fold(events)[0]]
        for _ in range(20):
            random.shuffle(events)
            self.assertEqual([e["id"] for e in r.fold(events)[0]], want)
            self.assertEqual([e["id"] for e in r.fold(events + events)[0]], want)

    def test_key_and_explicit_supersede(self):
        events = [ev("a", key="k", days_ago=3, body="one"),
                  ev("b", key="k", days_ago=1, body="two"),
                  ev("c", days_ago=5), ev("d", days_ago=1, supersedes=["c"])]
        self.assertEqual({e["id"] for e in r.fold(events)[0]}, {"b", "d"})

    def test_conflict_only_across_instances_within_a_day(self):
        a = ev("a", key="k", days_ago=0.5, body="one", instance="app")
        b = ev("b", key="k", days_ago=0.1, body="two", instance="code")
        self.assertEqual(r.fold([a, b])[1], [("a", "b")])
        b["instance"] = "app"
        self.assertEqual(r.fold([a, b])[1], [])
        far = ev("f", key="k", days_ago=0.1, body="two", instance="code")
        self.assertEqual(r.fold([ev("a", key="k", days_ago=9, body="one",
                                    instance="app"), far])[1], [])


class BriefTests(unittest.TestCase):
    def test_pinned_never_dropped_and_warns(self):
        events = [ev("p", "pref", body="y" * 50, key="lang")]
        out = r.brief(events, [], NOW, budget=10)
        self.assertEqual(out["included"], ["p"])
        self.assertTrue(out["warnings"])

    def test_budget_respected_for_unpinned(self):
        events = [ev(f"f{i}", body="z" * 30) for i in range(10)]
        out = r.brief(events, [], NOW, budget=100)
        self.assertLessEqual(out["chars"], 100)
        self.assertTrue(out["over_budget"])

    def test_decay_and_use_reinforcement(self):
        events = [ev("cold", "note", days_ago=60), ev("fresh", "note", days_ago=1),
                  ev("used", "note", days_ago=40)]
        usage = [use("used", d) for d in (30, 20, 10, 3, 1)]
        out = r.brief(events, usage, NOW)
        self.assertIn("fresh", out["included"])
        self.assertIn("used", out["included"])
        self.assertIn("cold", out["cold"])

    def test_scope_filter(self):
        events = [ev("g"), ev("p1", scope="project:a"), ev("p2", scope="project:b"),
                  ev("i", scope="instance:code")]
        out = r.brief(events, [], NOW, project="a", instance="code")
        self.assertEqual(set(out["included"]), {"g", "p1", "i"})

    def test_golden_recall(self):
        events = [
            ev("lang", "pref", key="idioma", body="answer in message language"),
            ev("why", "decision", days_ago=90, body="log is master because drift"),
            ev("stale", "note", days_ago=120, body="tmp scratch"),
            ev("task", "task", days_ago=2, body="migrate memory"),
        ]
        out = r.brief(events, [], NOW)
        for must in ("lang", "why", "task"):
            self.assertIn(must, out["included"])
        self.assertNotIn("stale", out["included"])


class CompactionTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            ev("n1", "note", 60, body="Looked around. Fixed /etc/foo.conf, error E-42."),
            ev("n2", "note", 70, body="Chatted a bit. Nothing else."),
            ev("keep", "note", 1),
        ]

    def test_digest_supersedes_without_deleting(self):
        digests = r.compaction_proposals(self.events, [], NOW)
        self.assertEqual(len(digests), 1)
        d = digests[0]
        self.assertEqual(sorted(d["supersedes"]), ["n1", "n2"])
        self.assertIn("/etc/foo.conf", d["body"])
        merged = self.events + digests
        self.assertEqual(len(merged), 4)  # nothing removed from the log
        active = {e["id"] for e in r.fold(merged)[0]}
        self.assertEqual(active, {"keep", d["id"]})
        self.assertNotIn("n1", r.brief(merged, [], NOW)["included"])

    def test_idempotent_and_reversible(self):
        d1 = r.compaction_proposals(self.events, [], NOW)
        d2 = r.compaction_proposals(self.events, [], NOW)
        self.assertEqual(d1[0]["id"], d2[0]["id"])
        # dropping the digest event restores the sources
        self.assertEqual({e["id"] for e in r.fold(self.events)[0]}, {"n1", "n2", "keep"})

    def test_pinned_never_compacted(self):
        events = [ev("p", "pref", 400, key="k", body="old pref")]
        self.assertEqual(r.compaction_proposals(events, [], NOW), [])


class DuplicateTests(unittest.TestCase):
    def test_flags_near_duplicates_only(self):
        events = [ev("a", body="use the full path for sync.sh always"),
                  ev("b", body="always use the full path for sync.sh"),
                  ev("c", body="german quiz has three modes")]
        self.assertEqual(r.near_duplicates(events), [("a", "b")])


if __name__ == "__main__":
    unittest.main()


class RefAndUseTests(unittest.TestCase):
    def test_short_ref_names_the_event_and_ambiguous_refs_do_nothing(self):
        events = [ev("20261018T120000Z-code-aaaaaa", "fact", 1, key="k", body="one"),
                  ev("20261018T120001Z-code-bbbbbb", "fact", 1, body="two")]
        gone = dict(id="f", type="forget", scope="global", key=None, body="", instance="code",
                    ts=NOW, supersedes=[], target="aaaaaa")
        self.assertEqual([e["id"] for e in r.fold(events + [gone])[0]], ["20261018T120001Z-code-bbbbbb"])
        dup = events + [ev("20261019T120000Z-app-aaaaaa", "fact", 1, body="three"), gone]
        self.assertEqual(len(r.fold(dup)[0]), 3)  # "aaaaaa" now matches two ids: nothing is forgotten

    def test_use_events_keep_an_entry_alive_and_accept_several_targets(self):
        events = [ev("20260901T120000Z-code-aaaaaa", "note", 40, body="old but used"),
                  ev("20260901T120001Z-code-bbbbbb", "note", 40, body="old, never used")]
        uses = [dict(id=f"u{i}", type="use", scope="global", key=None, body="applied", instance="app",
                     ts=NOW - timedelta(days=d), supersedes=[], target="aaaaaa, bbbbbb" if i == 0 else "aaaaaa")
                for i, d in enumerate((20, 10, 4, 1))]
        out = r.brief(events[:1] + uses, [], NOW)
        self.assertIn("20260901T120000Z-code-aaaaaa", out["included"])
        self.assertIn("20260901T120001Z-code-bbbbbb", r.brief(events, [], NOW)["cold"])
        self.assertEqual(len(r.uses_from(uses)), 5)


class DeclaredReplacementTests(unittest.TestCase):
    def test_restating_with_a_supersedes_reference_does_not_erase_the_entry(self):
        events = [ev("a", "pref", 5, key="k", body="use pnpm"),
                  ev("b", "pref", 1, key="k", body="always use pnpm", supersedes=["a"])]
        self.assertEqual([e["id"] for e in r.fold(events)[0]], ["a"])

    def test_declared_replacement_by_another_writer_is_not_a_conflict(self):
        old = ev("a", key="k", days_ago=0.5, body="one", instance="migration")
        new = ev("b", key="k", days_ago=0.1, body="two", instance="code", supersedes=["a"])
        self.assertEqual(r.fold([old, new]), ([new], []))
