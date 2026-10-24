#!/usr/bin/env python3
"""Build an isolated judging packet so a judge agent sees only what it should.

Usage:
  build_packet.py <run-dir> <out.md> [--ids I-02,I-09] [--no-synthesis] [--facts facts.md]

The packet contains: the founder brief, the synthesis (unless --no-synthesis, e.g. for a
fresh-context red team), the neutral pitches (no ideator lens, no scores, no status) and the
full text of every cited evidence item. Append verified competitive facts with --facts.
Give each judge agent ONLY this packet plus the role and rubric files — never scores.json,
other judges' files, or the ideator's reasoning. That separation is what makes judging
independent.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from council_common import load_evidence, load_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("out")
    ap.add_argument("--ids", help="comma-separated idea ids (default: all)")
    ap.add_argument("--no-synthesis", action="store_true")
    ap.add_argument("--facts", help="markdown file of verified facts to append (facts only, no verdicts)")
    a = ap.parse_args()

    ideas = load_json(os.path.join(a.run_dir, "ideas.json"), [])
    if a.ids:
        wanted = set(a.ids.split(","))
        ideas = [i for i in ideas if i["id"] in wanted]
    if not ideas:
        sys.exit("no ideas selected")
    evidence = load_evidence(a.run_dir)

    def read(name):
        with open(os.path.join(a.run_dir, name), encoding="utf-8") as f:
            return f.read()

    lines = ["# Judging packet", "", "## Founder brief", "", read("brief.md")]
    if not a.no_synthesis:
        lines += ["", "## Evidence-base synthesis (shared context)", "", read("synthesis.md")]
    lines += ["", "## Ideas to judge", "",
              "Ideas are identified only by neutral id. Evidence text is verbatim from public sources.", ""]
    for idea in ideas:
        lines.append(f"### {idea['id']} — {idea['name']}")
        lines.append("")
        for key in ("customer", "job", "wedge", "price", "price_usd_month", "v1", "riskiest_assumption"):
            if key in idea:
                lines.append(f"- **{key}:** {idea[key]}")
        lines.append(f"- **eliminate/reduce/raise/create:** {idea.get('errc')}")
        lines.append("- **cited evidence:**")
        for cite in idea.get("evidence", []):
            ev = evidence.get(cite["id"])
            if ev:
                lines.append(f"  - `{cite['id']}` ({ev.get('source')}, {ev.get('date')}, {ev.get('score')}★): "
                             f"{(ev.get('text') or '')[:700]!r}")
        lines.append("")
    if a.facts:
        with open(a.facts, encoding="utf-8") as f:
            lines += ["", "## Verified competitive facts (facts only; no scores or verdicts)", "", f.read()]
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {a.out}: {len(ideas)} ideas, ~{sum(len(x) for x in lines) // 4} tokens")


if __name__ == "__main__":
    main()
