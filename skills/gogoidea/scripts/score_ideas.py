#!/usr/bin/env python3
"""Combine independent judge scores into a scoreboard with gates and sensitivity.

Usage:
  score_ideas.py <run-dir> [--mode quick|standard|exhaustive] [--weights weights.json]
                 [--sensitivity] [--all]

Reads ideas.json, scores.json, evidence/*.jsonl and (optionally) mined.jsonl.
For each criterion the score is the MEDIAN across the judge roles that scored it.
The weighted score is normalised to 0-100 over the criteria that were scored.
Hard gates (see references/rubric.md) are computed from the cited evidence and
the judges' verdicts. Writes <run-dir>/scoreboard.md and prints it.
"""
import argparse
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from council_common import load_evidence, load_json, read_jsonl, voice_key  # noqa: E402

DEFAULT_WEIGHTS = {
    "money_evidence": 3, "wedge_sharpness": 3, "pain_severity": 2, "switch_intent": 2,
    "shippability": 2, "distribution_access": 2, "reach_at_price": 2,
    "defensibility": 1, "timing": 1, "craft_potential": 1, "support_burden": 1,
}
MIN_FAMILIES = {"quick": 1, "standard": 2, "exhaustive": 3}
MIN_VOICES = 3


def criterion_medians(judges):
    """judges: {role: {scores:{crit:n}}} -> ({crit: median}, {crit: spread})."""
    by_crit = {}
    for entry in judges.values():
        for crit, val in (entry.get("scores") or {}).items():
            if isinstance(val, (int, float)):
                by_crit.setdefault(crit, []).append(val)
    return ({c: statistics.median(v) for c, v in by_crit.items()},
            {c: max(v) - min(v) for c, v in by_crit.items() if len(v) > 1})


def weighted(medians, weights):
    scored = {c: m for c, m in medians.items() if c in weights}
    total_w = sum(weights[c] for c in scored)
    if not total_w:
        return None
    return 100.0 * sum(weights[c] * m for c, m in scored.items()) / (5.0 * total_w)


def gates(idea, judges, evidence, mined_by_id, min_families):
    failures = []
    cited = [evidence[c["id"]] for c in idea.get("evidence", []) if c.get("id") in evidence]
    voices = {voice_key(r) for r in cited}
    families = {r["family"] for r in cited if r["family"] != "analogous"}
    if len(voices) < MIN_VOICES:
        failures.append(f"G1 voices ({len(voices)}<{MIN_VOICES})")
    if len(families) < min_families:
        failures.append(f"G2 families ({len(families)}<{min_families})")
    if mined_by_id is not None:
        paid = any(mined_by_id.get(r["id"], {}).get("spend_usd_month") is not None
                   or mined_by_id.get(r["id"], {}).get("spend_text") for r in cited)
        if not paid:
            failures.append("G3 money (no cited spend)")
    verdicts = " ".join(str(e.get("verdict", "")).upper() for e in judges.values())
    if "TOO BIG" in verdicts:
        failures.append("G4 shippable (TOO BIG)")
    if "VETO" in verdicts:
        failures.append("G5 constraints (VETO)")
    if idea.get("status") == "killed":
        failures.append("G6 unanswered kill")
    return failures, len(voices), len(families)


def rank(rows):
    return sorted(rows, key=lambda r: (-1 if r["score"] is None else r["score"]), reverse=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--mode", default="standard", choices=MIN_FAMILIES)
    ap.add_argument("--weights")
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--all", action="store_true", help="include ideas whose status is cut/parked")
    a = ap.parse_args()

    ideas = load_json(os.path.join(a.run_dir, "ideas.json"), [])
    scores = load_json(os.path.join(a.run_dir, "scores.json"), {})
    if not ideas:
        sys.exit("ideas.json is missing or empty")
    weights = dict(DEFAULT_WEIGHTS)
    if a.weights:
        weights.update(load_json(a.weights, {}))
    evidence = load_evidence(a.run_dir)
    mined = read_jsonl(os.path.join(a.run_dir, "mined.jsonl"))
    mined_by_id = {m["id"]: m for m in mined if "id" in m} if mined else None

    rows = []
    for idea in ideas:
        if not a.all and idea.get("status") in ("cut", "parked"):
            continue
        judges = scores.get(idea["id"], {})
        medians, spreads = criterion_medians(judges)
        fails, nv, nf = gates(idea, judges, evidence, mined_by_id, MIN_FAMILIES[a.mode])
        rows.append({"idea": idea, "medians": medians, "spreads": spreads, "score": weighted(medians, weights),
                     "fails": fails, "voices": nv, "families": nf, "judges": sorted(judges)})

    ranked = rank(rows)
    lines = ["# Scoreboard", "", f"Mode: **{a.mode}** · judged ideas: {len(rows)}", "",
             "Scores are comparable only between ideas with the same criteria coverage.", "",
             "| # | id | idea | score | criteria scored | judges | voices | families | gates |",
             "|---|----|------|-------|-----------------|--------|--------|----------|-------|"]
    for i, r in enumerate(ranked, 1):
        s = "unscored" if r["score"] is None else f"{r['score']:.0f}"
        gate = "pass" if not r["fails"] else "FAIL: " + "; ".join(r["fails"])
        cov = sum(1 for c in weights if c in r["medians"])
        lines.append(f"| {i} | {r['idea']['id']} | {r['idea'].get('name', '')} | {s} | {cov}/{len(weights)} | "
                     f"{len(r['judges'])} | {r['voices']} | {r['families']} | {gate} |")

    flagged = [(r["idea"]["id"], c, sp) for r in ranked for c, sp in sorted(r["spreads"].items()) if sp >= 3]
    lines += ["", "## Judge disagreements (spread ≥3)", ""]
    lines += [f"- {i} · {c}: spread {sp:g}" for i, c, sp in flagged] or ["- none"]

    partial = [(r["idea"]["id"], [c for c in weights if c not in r["medians"]]) for r in ranked
               if any(c not in r["medians"] for c in weights)]
    if partial:
        lines += ["", "## Unscored criteria", "",
                  "Weights re-normalise over the criteria each idea was scored on, so finish scoring before "
                  "comparing ideas."]
        if len({tuple(m) for _, m in partial}) == 1:
            lines.append(f"- all ideas: {', '.join(partial[0][1])}")
        else:
            lines += [f"- {i}: {', '.join(missing)}" for i, missing in partial]

    passing = [r for r in ranked if not r["fails"] and r["score"] is not None]
    if a.sensitivity and passing:
        base_leader = passing[0]["idea"]["id"]
        scenarios, flips = 0, []
        scored_crits = sorted({c for r in passing for c in r["medians"] if c in weights})
        for c in scored_crits:
            for factor in (0.5, 1.5):
                w = dict(weights)
                w[c] = weights[c] * factor
                best = max(passing, key=lambda r: weighted(r["medians"], w) or -1)
                scenarios += 1
                if best["idea"]["id"] != base_leader:
                    flips.append(f"{c}×{factor}: {best['idea']['id']} leads")
        stable = scenarios - len(flips)
        lines += ["", "## Weight sensitivity", "",
                  f"Leader **{base_leader}** stays first in {stable}/{scenarios} scenarios "
                  f"(each weight ×0.5 and ×1.5)."]
        if len(passing) == 1:
            lines.append("Only one idea passes the gates, so this check is trivially stable.")
        lines += [f"- flips when {f}" for f in flips]
    elif a.sensitivity:
        lines += ["", "## Weight sensitivity", "", "No gate-passing scored ideas to test."]

    text = "\n".join(lines) + "\n"
    print(text)
    with open(os.path.join(a.run_dir, "scoreboard.md"), "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
