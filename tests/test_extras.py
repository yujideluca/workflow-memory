import random
import unittest
from datetime import datetime, timedelta, timezone

from mem import harvest, search
from mem import core as r
from tests.test_core import NOW, ev


def ctl(id, type, target=None, days_ago=0, instance="code", **kw):
    return dict(id=id, type=type, target=target, ts=NOW - timedelta(days=days_ago),
                scope="global", key=None, body="", instance=instance, supersedes=[], **kw)


def prompt(text, days_ago=0, project="a", source="user", hours=0):
    return dict(text=text, ts=NOW - timedelta(days=days_ago, hours=hours),
                project=project, source=source)


class FeedbackTests(unittest.TestCase):
    def test_helpful_raises_and_stale_lowers_score(self):
        e = ev("a", "note", 10)
        base = r.score(e, [], NOW)
        up = r.score(e, [], NOW, r._feedback([ctl("f", "feedback", "a", signal="helpful")]).get("a"))
        down = r.score(e, [], NOW, r._feedback([ctl("f", "feedback", "a", signal="stale")]).get("a"))
        self.assertGreater(up, base)
        self.assertLess(down, base)

    def test_stale_pushes_entry_out_of_brief(self):
        events = [ev("a", "fact", 150), ctl("f1", "feedback", "a", signal="stale"),
                  ctl("f2", "feedback", "a", signal="stale"),
                  ctl("f3", "feedback", "a", signal="stale")]
        self.assertIn("a", r.brief(events, [], NOW)["cold"])

    def test_wrong_leaves_brief_for_review(self):
        events = [ev("a", "fact", 1), ctl("f", "feedback", "a", signal="wrong")]
        out = r.brief(events, [], NOW)
        self.assertEqual(out["review"], ["a"])
        self.assertNotIn("a", out["included"])

    def test_feedback_is_per_version(self):
        events = [ev("v1", key="k", days_ago=3, body="one"),
                  ev("v2", key="k", days_ago=1, body="two"),
                  ctl("f", "feedback", "v1", signal="wrong")]
        out = r.brief(events, [], NOW)
        self.assertEqual(out["review"], [])  # v1 is superseded; v2 is clean
        self.assertIn("v2", out["included"])


class EvidenceTests(unittest.TestCase):
    def test_same_ruling_adds_evidence_not_a_new_line(self):
        events = [ev("a", "pref", 5, key="pm", body="use pnpm"),
                  ev("b", "pref", 1, key="pm", body="I always use pnpm")]
        state = r.resolve(events)
        self.assertEqual([e["id"] for e in state["active"]], ["a"])
        self.assertEqual(len(state["evidence"]["a"]), 1)
        self.assertEqual(r.brief(events, [], NOW)["lines"], ["- [pm] use pnpm"])

    def test_negation_is_a_change(self):
        events = [ev("a", "pref", 5, key="pm", body="use pnpm"),
                  ev("b", "pref", 1, key="pm", body="never use pnpm")]
        self.assertEqual([e["id"] for e in r.resolve(events)["active"]], ["b"])

    def test_evidence_counts_as_use(self):
        events = [ev("a", "fact", 200, key="k", body="same thing"),
                  ev("b", "fact", 1, key="k", body="same thing")]
        self.assertIn("a", r.brief(events, [], NOW)["included"])


class OwnershipTests(unittest.TestCase):
    def test_harvester_never_rewrites_user_owned_entry(self):
        events = [ev("u", "pref", 5, key="k", body="use bun", owner="user"),
                  ev("h", "pref", 1, key="k", body="use pnpm", instance="harvester")]
        out = r.brief(events, [], NOW)
        self.assertEqual(out["lines"], ["- [k] use bun"])
        self.assertEqual(out["proposals"], ["h"])

    def test_user_can_overrule_harvester(self):
        events = [ev("h", "pref", 5, key="k", body="use pnpm", instance="harvester"),
                  ev("u", "pref", 1, key="k", body="use bun", owner="user")]
        self.assertEqual(r.brief(events, [], NOW)["lines"], ["- [k] use bun"])

    def test_forgotten_entry_not_recreated_from_same_evidence(self):
        h1 = ev("h1", "pref", 9, key="k", body="use pnpm", instance="harvester")
        events = [h1, ctl("fg", "forget", "h1", days_ago=5),
                  ev("h2", "pref", 1, key="k", body="I always use pnpm", instance="harvester")]
        self.assertEqual(r.brief(events, [], NOW)["lines"], [])

    def test_forgotten_returns_if_user_states_it_again(self):
        h1 = ev("h1", "pref", 9, key="k", body="use pnpm", instance="harvester")
        events = [h1, ctl("fg", "forget", "h1", days_ago=5),
                  ev("u", "pref", 1, key="k", body="use pnpm", owner="user")]
        self.assertEqual(r.brief(events, [], NOW)["lines"], ["- [k] use pnpm"])

    def test_forget_is_order_independent(self):
        events = [ev("h1", "pref", 9, key="k", body="use pnpm", instance="harvester"),
                  ctl("fg", "forget", "h1", days_ago=5),
                  ev("h2", "pref", 1, key="k", body="use pnpm", instance="harvester")]
        for _ in range(10):
            random.shuffle(events)
            self.assertEqual(r.brief(events, [], NOW)["lines"], [])


class ClaimTests(unittest.TestCase):
    def test_earliest_claim_wins_whatever_the_delivery_order(self):
        events = [ev("t", "task", 3), ctl("c2", "claim", "t", 1, instance="app"),
                  ctl("c1", "claim", "t", 2, instance="code")]
        for _ in range(10):
            random.shuffle(events)
            self.assertEqual(r.claim_winner(events, "t"), ("code", ["app"]))

    def test_no_claim_and_same_instance_twice(self):
        self.assertEqual(r.claim_winner([ev("t", "task")], "t"), (None, []))
        two = [ctl("c1", "claim", "t", 2), ctl("c2", "claim", "t", 1)]
        self.assertEqual(r.claim_winner(two, "t"), ("code", []))

    def test_done_closes_task_and_control_events_stay_hidden(self):
        events = [ev("t", "task", 3), ctl("c", "claim", "t", 2), ctl("d", "done", "t", 1)]
        self.assertEqual(r.brief(events, [], NOW)["included"], [])


class HarvestTests(unittest.TestCase):
    def kinds(self, text):
        return [c["text"] for c in harvest.candidates([prompt(text)])]

    def test_detects_en_and_pt_preferences(self):
        self.assertEqual(self.kinds("Always use pnpm."), ["Always use pnpm."])
        self.assertEqual(self.kinds("Sempre responda em português."),
                         ["Sempre responda em português."])
        self.assertEqual(self.kinds("Prefiro usar o caminho completo."),
                         ["Prefiro usar o caminho completo."])

    def test_ignores_non_preferences(self):
        for text in ("The build always fails.", "Should I always use pnpm?",
                     "**Always use pnpm** per relevance.py:12.",
                     "```\nalways use pnpm\n```"):
            self.assertEqual(self.kinds(text), [], text)

    def test_only_the_users_own_words(self):
        agent = prompt("Always use pnpm.", source="tool")
        self.assertEqual(harvest.candidates([agent]), [])

    def test_single_project_stays_project_scoped(self):
        events = harvest.converge(harvest.candidates([prompt("Always use pnpm.")]))
        self.assertEqual(events[0]["scope"], "project:a")

    def test_two_projects_go_global(self):
        cands = harvest.candidates([prompt("Always use pnpm.", 5, "a"),
                                    prompt("I always use pnpm.", 1, "b")])
        self.assertEqual({e["scope"] for e in harvest.converge(cands)}, {"global"})

    def test_fanout_within_an_hour_counts_once(self):
        cands = harvest.candidates([prompt("Always use pnpm.", 0, "a"),
                                    prompt("Always use pnpm.", 0, "b")])
        self.assertEqual({e["scope"] for e in harvest.converge(cands)},
                         {"project:a", "project:b"})

    def test_explicit_scope_goes_global(self):
        cands = harvest.candidates([prompt("In all my projects, always use pnpm.")])
        self.assertEqual(harvest.converge(cands)[0]["scope"], "global")

    def test_pipeline_latest_ruling_wins_and_is_idempotent(self):
        prompts = [prompt("Use pnpm in all my projects.", 9),
                   prompt("I always use pnpm in all my projects.", 6),
                   prompt("Never use pnpm in all my projects.", 1)]
        events = harvest.converge(harvest.candidates(prompts))
        out = r.brief(events + events, [], NOW)
        self.assertEqual(len(out["lines"]), 1)
        self.assertIn("Never use pnpm", out["lines"][0])


class SearchTests(unittest.TestCase):
    def test_cold_entries_are_searchable_but_not_in_brief(self):
        events = [ev("old", "note", 100, body="alemão: Konjunktiv II drills"),
                  ev("new", "note", 1, body="sync uses the full path")]
        self.assertIn("old", r.brief(events, [], NOW)["cold"])
        self.assertEqual(search.Index(events).search("Konjunktiv"), ["old"])

    def test_superseded_and_out_of_scope_not_found(self):
        events = [ev("a", key="k", days_ago=3, body="uses pnpm"),
                  ev("b", key="k", days_ago=1, body="uses bun"),
                  ev("p", scope="project:x", body="uses deno")]
        idx = search.Index(events, project="y")
        self.assertEqual(idx.search("pnpm"), [])
        self.assertEqual(idx.search("deno"), [])
        self.assertEqual(idx.search("bun"), ["b"])

    def test_accents_and_empty_query(self):
        events = [ev("a", body="preferência de resposta curta")]
        idx = search.Index(events)
        self.assertEqual(idx.search("preferencia"), ["a"])
        self.assertEqual(idx.search("???"), [])


class RuleTests(unittest.TestCase):
    def test_brief_states_memory_never_authorizes(self):
        header = r.brief([], [], NOW)["header"]
        self.assertIn("never authorizes", header)
        self.assertLess(header.index("current instruction"), header.index("profile"))


if __name__ == "__main__":
    unittest.main()
