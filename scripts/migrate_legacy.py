"""One-time import of what is still true from the old workflow's live memory.

Idempotent: ids come from the key and the date, and `ev.write` never overwrites.
Run from the repo root: python3 scripts/migrate_legacy.py
"""
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mem import events as ev, validate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime(2026, 10, 18, 23, 0, tzinfo=timezone.utc)


def day(d):
    return datetime.fromisoformat(d).replace(hour=12, tzinfo=timezone.utc)


# (type, scope, key, owner, date, text)
ENTRIES = [
    ("pref", "global", "style.plain-language", "user", "2026-10-17",
     "Explain in plain language: define every technical or pipeline term the first time it appears and give "
     "the human-level meaning before the details. Never assume Giovanni knows something that was only "
     "mentioned in passing. Reason: they had to ask repeatedly ('your answer is very obscure from a human "
     "standpoint')."),
    ("pref", "global", "language.reply", "user", "2026-10-16",
     "Giovanni writes in English or Portuguese: answer in the language of the message. Use they/them for "
     "Giovanni."),
    ("pref", "global", "work.setup-end-to-end", "user", "2026-10-16",
     "Do installs and setup end to end. Hand over only the steps that need sudo or Giovanni's own approval."),
    ("pref", "global", "work.test-yourself", "user", "2026-10-16",
     "After coding anything, do a first debugging pass and test reversible features yourself (for example on "
     "the phone) instead of asking. Giovanni called excess caution unfounded."),
    ("pref", "global", "work.encode-decisions", "user", "2026-10-17",
     "A decision Giovanni states once must be encoded where it takes effect, not only written in a log. They "
     "should never have to repeat it."),
    ("pref", "global", "work.build-then-ask", "user", "2026-10-18",
     "When a project and plan are approved, build it end to end without stopping to report progress. Collect "
     "questions and decisions that depend on Giovanni and ask them at the end. A day lost waiting on a minor "
     "question is wasted time."),
    ("pref", "global", "work.verified-by", "user", "2026-10-16",
     "Report work as done only with proof: end with 'Verified by:' saying what was run and what could not be "
     "checked."),
    ("pref", "global", "git.no-force-push", "user", "2026-10-16", "Never force-push."),
    ("pref", "global", "safety.ask-before-outward", "user", "2026-10-16",
     "Ask before anything outward-facing (sending email, accepting events, purchases) or destructive, unless "
     "Giovanni has explicitly said to proceed."),
    ("pref", "instance:assistant", "style.phone", "user", "2026-10-11",
     "Replies are read on a phone: short, lead with the answer, no wide tables."),
    ("pref", "global", "policy.third-party-data", "user", "2026-10-18",
     "Never store clinical, secret or contact data about other people in memory. Giovanni does not name "
     "people in clinical situations; if a case ever needs it, they will ask for a specific procedure."),
    ("fact", "global", "person.profile", "migration", "2026-10-16",
     "Giovanni is a pre-hospital emergency physician (SAMU/APH) in Brazil, preparing the Goethe B2 exam "
     "(Nov 2026) and the FSP to work in Germany."),
    ("fact", "global", "host.nitro", "migration", "2026-10-15",
     "Giovanni's laptop is an Acer Nitro (host yuji-nitro, Kubuntu 24.04, X11, Nvidia): RTX 3050 with 6 GB "
     "VRAM, 23 GB RAM. A spare 512 GB NVMe is mounted only temporarily (no fstab entry)."),
    ("fact", "global", "device.phone", "migration", "2026-10-16",
     "Giovanni's phone is a Motorola edge 50 fusion, driven over adb for app tests."),
    ("fact", "global", "service.claude-assistant", "migration", "2026-10-11",
     "Service claude-assistant (systemd user service, linger on, starts at boot) runs 'claude remote-control' "
     "in tmux socket 'claude', home ~/assistant, and shows in the app as yuji-nitro-assistant. Giovanni chose "
     "bypassPermissions themself on 2026-10-11: do not change the mode without asking. Watch it with "
     "'claude-assistant attach' (Ctrl+b d leaves); restart with systemctl --user restart claude-assistant."),
    ("fact", "global", "project.quizapp", "migration", "2026-10-16",
     "QuizApp lives in ~/dev/QuizApp (Kotlin, local git only, no remote): a German B2 quiz with 3 modes and "
     "Anki-style scheduling, tested on the phone over adb."),
    ("fact", "global", "tool.local-qwen", "migration", "2026-10-17",
     "Local Qwen3.5-9B Q4 runs through llama-server on 127.0.0.1:8080 (16k context, about 5.4 GB VRAM); "
     "pkill -f llama-server stops it. Study: ~/Documents/Qwen-delegation-study-report.md. Pseudo-code specs "
     "work best, delegating small functions saves no Claude tokens, and the gate is only as good as the tests."),
    ("decision", "global", "decision.memory-v3", "user", "2026-10-18",
     "The old claude-workflow-backup protocol (logbooks, SEEN cursors, sync, heartbeat, nightly review) is "
     "abandoned. This project, workflow-memory, is the new workflow: an append-only event log, state computed "
     "from it, views generated by a GitHub Action."),
    ("decision", "global", "decision.ai-memory-inspiration", "user", "2026-10-18",
     "ai-memory (akitaonrails) is inspiration only: relevance by use, supersede instead of delete, handoffs "
     "claimed once. It is not installed and not a dependency."),
]


def main():
    wrote = 0
    for kind, scope, key, owner, date, text in ENTRIES:
        ts = day(date)
        digest = hashlib.sha1(f"{key}|{date}".encode()).hexdigest()[:6]
        e = dict(id=f"{ts:%Y%m%dT%H%M%SZ}-migration-{digest}", ts=ts, type=kind, scope=scope, key=key,
                 body=text, instance="migration", owner=owner, supersedes=[], target=None, signal=None)
        why = validate.check_event(e, NOW)
        if why:
            sys.exit(f"{key}: {'; '.join(why)}")
        path = ev.path_for(ROOT, e)
        wrote += not path.exists()
        ev.write(ROOT, e)
    print(f"{wrote} new, {len(ENTRIES) - wrote} already present")


if __name__ == "__main__":
    main()
