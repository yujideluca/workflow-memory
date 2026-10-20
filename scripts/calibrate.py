"""Recommend the memory constants from Giovanni's real Claude Code usage.

Reads the transcripts in ~/.claude/projects (read-only) and prints measurements, the rule that turns each
into a constant, the recommendation and the value currently in the code. Changes nothing.

    python3 scripts/calibrate.py [--projects DIR]

Rules (the only judgement calls, stated so they can be argued with):
- Brief budget: the brief may cost at most SHARE of the median first-turn context, because that context is
  paid again on every turn (cache write once, cache reads after).
- Note half-life: an unused note goes cold after K_NOTE times the 90th-percentile gap between sessions of
  the same project. Tasks do not decay (open items). Cold means the score fell under COLD_THRESHOLD.
- Facts and decisions describe a stable setup and cannot be calibrated from days of history; they keep their
  value until enough history exists (the script says when it does).
"""
import argparse
import glob
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mem import core, project  # noqa: E402

SHARE = 0.025
CHARS_PER_TOKEN = 3.6  # mixed Portuguese and English; an assumption, not measured
K_NOTE = 8
MIN_WINDOW_DAYS, MIN_GAPS = 30, 100


def sessions(projects_dir):
    out = []
    for path in glob.glob(str(Path(projects_dir) / "*" / "*.jsonl")):
        stamps, first = [], None
        for line in open(path, errors="ignore"):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("timestamp"):
                stamps.append(datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")))
            usage = (row.get("message") or {}).get("usage") if row.get("type") == "assistant" else None
            if usage and first is None:
                first = sum(usage.get(k, 0) for k in
                            ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        if len(stamps) > 1 and first:
            out.append(dict(project=Path(path).parent.name, start=min(stamps), first=first))
    return out


def percentile(values, p):
    values = sorted(values)
    return values[min(int(len(values) * p), len(values) - 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=str(Path.home() / ".claude/projects"))
    rows = sessions(ap.parse_args().projects)
    if len(rows) < 5:
        sys.exit("not enough sessions to calibrate")
    window = (max(r["start"] for r in rows) - min(r["start"] for r in rows)).days
    by_project = {}
    for r in rows:
        by_project.setdefault(r["project"], []).append(r["start"])
    gaps = [(b - a).total_seconds() / 86400 for v in by_project.values()
            for a, b in zip(sorted(v), sorted(v)[1:])]
    baseline = statistics.median(r["first"] for r in rows)
    gap90 = percentile(gaps, 0.9)
    cold = core.COLD_THRESHOLD

    sample = project.build(Path(__file__).resolve().parent.parent, datetime.now().astimezone())
    brief = sample["BRIEF.md"]
    lines_chars = sum(len(x) + 1 for x in brief.splitlines() if x.startswith("- "))
    overhead = len(brief) - lines_chars
    total = baseline * SHARE * CHARS_PER_TOKEN
    note_cold = K_NOTE * gap90
    rec = {
        "brief file chars (lines + how-to)": (round(total), project.BRIEF_BUDGET + overhead),
        "brief lines budget": (round(total - overhead), project.BRIEF_BUDGET),
        "note half-life (days)": (round(note_cold / math.log2(core.TIERS["note"][1] / cold), 1),
                                  core.TIERS["note"][0]),
        "compact cold entries older than (days)": (round(2 * note_cold), 30),
    }
    print(f"sessions {len(rows)}, window {window} days, gaps {len(gaps)}")
    print(f"median first-turn context {baseline:,.0f} tokens; p90 gap between sessions of a project "
          f"{gap90:.2f} days")
    print(f"brief share {SHARE:.1%} of baseline = {baseline * SHARE:,.0f} tokens "
          f"= {total:,.0f} chars at {CHARS_PER_TOKEN} chars/token; fixed part of BRIEF.md {overhead} chars")
    print(f"{'constant':42} {'recommended':>12} {'in code':>9}")
    for name, (new, old) in rec.items():
        print(f"{name:42} {new:>12} {old:>9}")
    if window < MIN_WINDOW_DAYS or len(gaps) < MIN_GAPS:
        print(f"LOW CONFIDENCE: window {window} < {MIN_WINDOW_DAYS} days or gaps {len(gaps)} < {MIN_GAPS}. "
              "Fact (180 d) and decision (180 d) half-lives are not calibrated; re-run later.")


if __name__ == "__main__":
    main()
