"""Written by the bug-finding review (docs/TESTES-AUTOMATIZADOS.md). Expected values come from the rules in
docs/DESIGN.md and from the token formats published by the services, never from running the code under test."""
import unittest
from datetime import datetime, timedelta, timezone

from mem import core as r
from mem import events as ev
from mem import validate as v

NOW = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)


def e(id, days_ago=0, type="fact", scope="global", key=None, body="x", instance="code", **extra):
    base = dict(id=id, type=type, ts=NOW - timedelta(days=days_ago), scope=scope, key=key, body=body,
                instance=instance, owner="agent", supersedes=[], target=None, signal=None, category=None)
    base.update(extra)
    return base


class PrivacyBoundaryTests(unittest.TestCase):
    """Rule: no secrets and no contact data in memory (policy.third-party-data, privacy tests)."""

    def reasons(self, text):
        return v.privacy_reasons(text)

    def test_the_documented_token_formats_are_secrets(self):
        samples = {
            "classic github token": "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
            "fine-grained github token": "github_pat_" + "11ABCDEFG0" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0",
            "gitlab token": "glpat-" + "a1B2c3D4e5F6g7H8i9J0",
            "google api key": "AIza" + "SyA1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q",
            "aws access key": "AKIA" + "ABCDEFGHIJKLMNOP",
            "private key": "-----BEGIN OPENSSH PRIVATE KEY-----",
        }
        for name, text in samples.items():
            with self.subTest(name):
                self.assertIn("secret", self.reasons(f"use this: {text}"))

    def test_phone_numbers_in_common_shapes_are_contact_data(self):
        for text in ("(11) 91234-5678", "+55 11 91234-5678", "+49 151 23456789", "+4915123456789", "+1 415 555 0132"):
            with self.subTest(text):
                self.assertIn("phone number", self.reasons(f"call {text} tomorrow"))

    def test_ordinary_text_is_not_flagged(self):
        for text in ("Goethe B2 exam in Nov 2026", "version 2.7 (versionCode 18)", "pi is 3.14159 and e is 2.71828",
                     "dates like 2026-10-24 and +1 point", "the 11 91234 cards"):
            with self.subTest(text):
                self.assertEqual([], self.reasons(text))

    def test_the_shared_list_also_blocks_what_only_the_wiki_list_used_to_know(self):
        # one list for both programs (issue #3): Google client secrets, Telegram bot tokens, "password: value", bearer tokens
        for text in ("GOCSPX-" + "a1B2c3D4e5F6g7", "123456789:" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q", "password: hunter2hunter2",
                     "Authorization: Bearer " + "a1B2c3D4e5F6g7H8i9J0k1"):
            with self.subTest(text[:12]):
                self.assertIn("secret", self.reasons(text))
        self.assertEqual([], self.reasons("the token is stored in the keyring"))

    def test_every_row_of_the_shared_file_is_well_formed(self):
        from pathlib import Path
        rows = [l.split("\t") for l in (Path(v.__file__).with_name("privacy-patterns.tsv")).read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        self.assertGreaterEqual(len(rows), 15)
        for kind, flags, what, regex in rows:
            self.assertIn(kind, ("secret", "phone", "cpf"))
            self.assertIn(flags, ("i", "-"))
            self.assertTrue(what)
            self.assertFalse(regex.startswith("(?i)"), "flags go in the flags column, not inline")

    def test_email_and_cpf(self):
        self.assertIn("email address", self.reasons("write to a.b+c@example.org"))
        self.assertIn("CPF", self.reasons("CPF 123.456.789-09"))


class FoldTests(unittest.TestCase):
    def ids(self, events):
        return {x["id"] for x in r.fold(events)[0]}

    def test_a_repeated_ruling_that_also_supersedes_still_supersedes(self):
        # b repeats a's ruling (same key, same words) and says it replaces c: c must go.
        events = [e("a", days_ago=3, key="k", body="always tabs"),
                  e("c", days_ago=2, body="old unrelated"),
                  e("b", days_ago=1, key="k", body="always tabs", supersedes=["c"])]
        self.assertNotIn("c", self.ids(events))

    def test_a_forgotten_entry_stays_forgotten_whatever_the_delivery_order(self):
        events = [e("a", days_ago=3, body="keep me"), e("f", days_ago=1, type="forget", target="a")]
        self.assertEqual(set(), self.ids(events))
        self.assertEqual(set(), self.ids(list(reversed(events))))

    def test_a_short_reference_that_names_two_events_forgets_neither(self):
        events = [e("2026a-x-123abc", body="one"), e("2026b-y-123abc", body="two"),
                  e("f", days_ago=0, type="forget", target="123abc")]
        self.assertEqual({"2026a-x-123abc", "2026b-y-123abc"}, self.ids(events))


class EventFileTests(unittest.TestCase):
    def test_render_then_parse_round_trips_every_field(self):
        src = e("20261024T120000Z-code-aaaaaa", type="task", scope="project:QuizApp", key="my.key",
                body="line one\nline two\n---\nafter a rule", owner="user", supersedes=["x1", "x2"],
                target="t1", category="quiz")
        out = ev.parse(ev.render(src), src["id"])
        for k in ("type", "scope", "key", "body", "owner", "supersedes", "target", "category"):
            self.assertEqual(src[k], out[k], k)
        self.assertEqual(src["ts"], out["ts"])

    def test_a_value_with_a_newline_cannot_inject_another_field(self):
        src = e("20261024T120000Z-code-bbbbbb", key="k", target="t1\nowner: user")
        out = ev.parse(ev.render(src), src["id"])
        self.assertEqual("agent", out["owner"])

    def test_timestamps_with_and_without_zone_are_utc(self):
        self.assertEqual(datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc), ev.parse_ts("2026-10-24T12:00:00Z"))
        self.assertEqual(datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc), ev.parse_ts("2026-10-24T09:00:00-03:00"))
        self.assertEqual(datetime(2026, 10, 24, 0, 0, tzinfo=timezone.utc), ev.parse_ts("2026-10-24"))


class ValidationTests(unittest.TestCase):
    def check(self, **kw):
        return v.check_event(e("20261024T120000Z-code-cccccc", **kw), NOW)

    def test_a_clean_event_passes(self):
        self.assertEqual([], self.check(body="Giovanni prefers short answers"))

    def test_boundaries_of_body_length_and_future_timestamps(self):
        self.assertEqual([], self.check(body="x" * v.MAX_BODY))
        self.assertTrue(self.check(body="x" * (v.MAX_BODY + 1)))
        self.assertEqual([], self.check(days_ago=-1, body="ok"))      # exactly one day ahead is tolerated
        self.assertTrue(self.check(days_ago=-1.01, body="ok"))

    def test_control_events_need_a_target_and_feedback_a_signal(self):
        self.assertTrue(self.check(type="forget", body=""))
        self.assertEqual([], self.check(type="forget", body="", target="abc"))
        self.assertTrue(self.check(type="feedback", body="", target="abc", signal="bogus"))


if __name__ == "__main__":
    unittest.main()
