#!/usr/bin/env python3
"""Summarise the evidence base and the mined tags for an Idea Council run.

Usage: evidence_stats.py <run-dir> [--mode quick|standard|exhaustive]

Reads evidence/*.jsonl and (optionally) mined.jsonl. Prints markdown and writes
<run-dir>/evidence-stats.md. Use the numbers in the report instead of estimates.
With mined.jsonl present it also runs the evidence-sufficiency check for the mode:
if it fails, gather more evidence before ideating (see SKILL.md stage 3).
"""
import argparse
import os
import sys
from collections import Counter

# Minimum evidence before ideation is worth doing: pain items, spend items,
# switch-intent items, source families.
SUFFICIENCY = {
    "quick": {"pain": 15, "spend": 3, "switch": 2, "families": 2},
    "standard": {"pain": 80, "spend": 15, "switch": 8, "families": 3},
    "exhaustive": {"pain": 200, "spend": 40, "switch": 20, "families": 5},
}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from council_common import load_evidence, read_jsonl, voice_key  # noqa: E402


def table(title, counter, total=None):
    lines = [f"### {title}", "", "| value | count |", "|---|---|"]
    for k, v in counter.most_common():
        lines.append(f"| {k} | {v} |")
    if total is not None:
        lines.append(f"| **total** | **{total}** |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--mode", default="standard", choices=SUFFICIENCY)
    args = ap.parse_args()
    run = args.run_dir
    evidence = load_evidence(run)
    if not evidence:
        sys.exit(f"No evidence found in {run}/evidence/*.jsonl")

    out = ["# Evidence stats", ""]
    out.append(table("Items by source", Counter(r.get("source") for r in evidence.values()), len(evidence)))
    out.append(table("Items by family", Counter(r["family"] for r in evidence.values())))
    voices = {voice_key(r) for r in evidence.values()}
    out.append(f"Distinct voices (source+author, or URL if anonymous): **{len(voices)}**\n")

    mined = read_jsonl(os.path.join(run, "mined.jsonl"))
    if mined:
        spend = [m for m in mined if m.get("spend_usd_month") is not None or m.get("spend_text")]
        switch = [m for m in mined if m.get("switch_intent")]
        out.append("## Mined tags\n")
        out.append(f"- Items with a pain signal: **{len(mined)}** of {len(evidence)} read "
                   f"({100 * len(mined) / len(evidence):.0f}%)")
        out.append(f"- With dollar spend: **{len(spend)}**")
        out.append(f"- With explicit switch intent: **{len(switch)}**")
        both = [m for m in mined if m in spend and m in switch]
        out.append(f"- With both spend and switch intent: **{len(both)}**\n")
        out.append(table("Evidence grade", Counter(m.get("grade", "?") for m in mined)))
        out.append(table("Severity", Counter(m.get("severity", "?") for m in mined)))
        def top(field):
            return Counter(dict(Counter(m.get(field) for m in mined if m.get(field)).most_common(10)))

        out.append(table("Top customer types", top("who")))
        out.append(table("Top workarounds", top("workaround")))
        amounts = sorted(m["spend_usd_month"] for m in mined if isinstance(m.get("spend_usd_month"), (int, float)))
        if amounts:
            mid = amounts[len(amounts) // 2]
            out.append(f"Stated monthly spend: n={len(amounts)}, min ${amounts[0]:g}, "
                       f"median ${mid:g}, max ${amounts[-1]:g}\n")

        need = SUFFICIENCY[args.mode]
        have_families = len({r["family"] for r in evidence.values() if r["family"] != "analogous"})
        checks = [("pain items", len(mined), need["pain"]), ("items with spend", len(spend), need["spend"]),
                  ("items with switch intent", len(switch), need["switch"]),
                  ("source families", have_families, need["families"])]
        out.append(f"## Sufficiency check ({args.mode})\n")
        for name, have, req in checks:
            out.append(f"- {'PASS' if have >= req else 'FAIL'} · {name}: {have} / {req}")
        if all(h >= r for _, h, r in checks):
            out.append("\n**READY** — enough evidence to ideate.\n")
        else:
            out.append("\n**NOT READY** — gather more evidence (new angles, more source families) before "
                       "ideating. If it stays thin after a second pass, report that honestly instead of "
                       "inventing ideas.\n")
    else:
        out.append("_No mined.jsonl yet — run the miners._\n")

    text = "\n".join(out)
    print(text)
    with open(os.path.join(run, "evidence-stats.md"), "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
