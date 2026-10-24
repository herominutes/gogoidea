#!/usr/bin/env python3
"""Turn Gate findings and lens scores into a recommendation, priority list and decision input.

Usage:
  gate_score.py <gate-dir> [--profile consumer-app|saas|regulated|internal|prototype]
                [--weights weights.json] [--mode quick|standard|exhaustive]
                [--go-score 80] [--cond-score 65] [--max-s2 3]

Reads findings.json and scores.json (and verify-results.json if present). Writes
decision-input.md and decision-input.json in <gate-dir>. The recommendation is deterministic
and follows references/gate/decision-rules.md; the chair can argue with it but not override an
open blocker without an owned, dated risk acceptance (and S1 findings can't be accepted).
Standard library only; Python 3.8+.
"""
import argparse
import json
import os
import statistics
import sys

LENSES = ["strategy", "security", "privacy", "auth", "functionality", "quality", "journey", "ux", "data", "release"]
CRITICAL = {"security", "privacy", "auth", "data"}
PROFILES = {
    "consumer-app": dict(strategy=3, security=3, privacy=3, auth=2, functionality=3, quality=2, journey=2, ux=2, data=3, release=1),
    "saas":         dict(strategy=2, security=3, privacy=3, auth=3, functionality=3, quality=2, journey=2, ux=1, data=3, release=2),
    "regulated":    dict(strategy=1, security=4, privacy=4, auth=3, functionality=3, quality=2, journey=1, ux=1, data=4, release=2),
    "internal":     dict(strategy=3, security=2, privacy=1, auth=2, functionality=3, quality=3, journey=1, ux=1, data=3, release=1),
    "prototype":    dict(strategy=4, security=1, privacy=1, auth=1, functionality=3, quality=1, journey=3, ux=2, data=2, release=1),
}
SEV_POINTS = {"S1": 100, "S2": 40, "S3": 10, "S4": 2}
IMPACT = {"core": 3, "supporting": 2, "peripheral": 1}
EXPOSURE = {"all": 3, "segment": 2, "few": 1}


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def priority(f):
    return SEV_POINTS.get(f.get("severity"), 0) * IMPACT.get(f.get("strategic_impact"), 2) * EXPOSURE.get(f.get("exposure"), 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gate_dir")
    ap.add_argument("--profile", default="consumer-app", choices=sorted(PROFILES))
    ap.add_argument("--weights")
    ap.add_argument("--mode", default="standard", choices=["quick", "standard", "exhaustive"])
    ap.add_argument("--go-score", type=float, default=80)
    ap.add_argument("--cond-score", type=float, default=65)
    ap.add_argument("--max-s2", type=int, default=3)
    a = ap.parse_args()

    findings = load(os.path.join(a.gate_dir, "findings.json"), [])
    scores = load(os.path.join(a.gate_dir, "scores.json"), {})
    verify = load(os.path.join(a.gate_dir, "verify-results.json"), None)
    weights = dict(PROFILES[a.profile])
    if a.weights:
        weights.update(load(a.weights, {}))

    # ---- lens scores
    lens_rows, reviewed, unreviewed = [], {}, []
    for lens in LENSES:
        entries = scores.get(lens) or {}
        vals = [e.get("score") for e in entries.values() if isinstance(e, dict) and isinstance(e.get("score"), (int, float))]
        if vals:
            reviewed[lens] = statistics.median(vals)
            lens_rows.append((lens, weights[lens], reviewed[lens], len(vals), min(vals)))
        else:
            unreviewed.append(lens)
            lens_rows.append((lens, weights[lens], None, 0, None))
    wsum = sum(weights[l] for l in reviewed)
    weighted = round(100.0 * sum(weights[l] * reviewed[l] for l in reviewed) / (5.0 * wsum), 1) if wsum else 0.0

    # ---- findings
    open_f, valid_accepted, invalid_accepted, closed, wontfix = [], [], [], [], []
    for f in findings:
        st = f.get("status", "open")
        if st == "open":
            open_f.append(f)
        elif st == "accepted":
            if f.get("owner") and f.get("due") and f.get("severity") != "S1":
                valid_accepted.append(f)
            else:
                invalid_accepted.append(f)
                open_f.append(f)  # an accepted risk without an owner and expiry still counts as open
        elif st == "wont_fix":
            wontfix.append(f)
        else:
            closed.append(f)
    blockers = [f for f in open_f if f.get("severity") == "S1" or f.get("blocker") is True]
    s2_open = [f for f in open_f if f.get("severity") == "S2"]
    s2_total = len(s2_open) + len([f for f in valid_accepted if f.get("severity") == "S2"])
    s2_no_owner = [f for f in s2_open + [x for x in valid_accepted if x.get("severity") == "S2"] if not f.get("owner")]
    sev_counts = {s: len([f for f in open_f if f.get("severity") == s]) for s in ("S1", "S2", "S3", "S4")}

    # ---- verification state
    failed_verify = sorted(verify.get("failed", {}).keys()) if verify else []
    unverified_high = []
    for f in findings:
        if f.get("severity") in ("S1", "S2") and f.get("status", "open") == "open":
            has_file = any(e.get("type") in ("file", "count") for e in (f.get("evidence") or []))
            if not has_file:
                unverified_high.append(f.get("id"))

    # ---- decision
    reasons = []
    low2 = [l for l, m in reviewed.items() if m < 2]
    low3_critical = [l for l in CRITICAL if l in reviewed and reviewed[l] < 3]
    low3_any = [l for l, m in reviewed.items() if m < 3]
    if blockers:
        decision = "NO-GO"
        reasons.append("%d open blocker(s): %s" % (len(blockers), ", ".join(str(f.get("id")) for f in blockers)))
    elif unreviewed:
        decision = "INCOMPLETE"
        reasons.append("Lenses not yet reviewed: " + ", ".join(unreviewed))
    elif failed_verify:
        decision = "INCOMPLETE"
        reasons.append("Findings failed evidence verification: %s. Fix or drop them and re-run verify_findings.py." % ", ".join(failed_verify))
    elif verify is None and findings:
        decision = "INCOMPLETE"
        reasons.append("verify_findings.py has not been run (no verify-results.json).")
    else:
        problems = []
        if low2:
            problems.append("lens(es) below 2: " + ", ".join(low2))
        if low3_critical:
            problems.append("critical lens(es) below 3: " + ", ".join(sorted(low3_critical)))
        if s2_total > a.max_s2:
            problems.append("%d open or accepted S2 findings (limit %d)" % (s2_total, a.max_s2))
        if s2_no_owner:
            problems.append("S2 finding(s) without an owner: " + ", ".join(str(f.get("id")) for f in s2_no_owner))
        if weighted < a.cond_score:
            problems.append("weighted score %.1f is below %.0f" % (weighted, a.cond_score))
        if problems:
            decision = "NO-GO"
            reasons.extend(problems)
        elif weighted >= a.go_score and s2_total == 0 and not low3_any:
            decision = "GO"
            reasons.append("No blockers, no open S2, every lens ≥ 3, weighted score %.1f ≥ %.0f." % (weighted, a.go_score))
        else:
            decision = "GO WITH CONDITIONS"
            why = []
            if s2_total:
                why.append("%d S2 finding(s) need owners, mitigations and verification" % s2_total)
            if low3_any:
                why.append("lens(es) at 2: " + ", ".join(sorted(low3_any)))
            if weighted < a.go_score:
                why.append("weighted score %.1f is below the GO line of %.0f" % (weighted, a.go_score))
            reasons.append("; ".join(why) or "Score below the GO line.")
    if unreviewed and decision == "NO-GO":
        reasons.append("Also incomplete: lenses not yet reviewed: " + ", ".join(unreviewed))
    if "strategy" in reviewed and reviewed["strategy"] < 2:
        reasons.append("Strategy lens is below 2: consider ARCHIVE WITHOUT SHIP — the build may not serve the current direction.")
    if invalid_accepted:
        reasons.append("Accepted risks without an owner and expiry (or accepted S1) are treated as open: " +
                       ", ".join(str(f.get("id")) for f in invalid_accepted))
    if unverified_high:
        reasons.append("S1/S2 findings with no file evidence (reproduce before relying on them): " + ", ".join(map(str, unverified_high)))

    # ---- priority buckets
    ranked = sorted(open_f, key=lambda f: (-priority(f), str(f.get("id"))))
    fix_before = [f for f in ranked if f in blockers or (f.get("severity") == "S2" and f.get("strategic_impact") == "core")]
    carry = [f for f in ranked if f not in fix_before]

    result = {"decision": decision, "reasons": reasons, "profile": a.profile, "mode": a.mode, "weighted_score": weighted,
              "lens_scores": {l: reviewed.get(l) for l in LENSES}, "weights": weights, "unreviewed_lenses": unreviewed,
              "open_by_severity": sev_counts, "blockers": [f.get("id") for f in blockers],
              "accepted_valid": [f.get("id") for f in valid_accepted],
              "accepted_invalid": [f.get("id") for f in invalid_accepted],
              "fix_before_ship": [f.get("id") for f in fix_before], "carry_over": [f.get("id") for f in carry],
              "failed_verification": failed_verify, "unverified_high_severity": unverified_high,
              "thresholds": {"go_score": a.go_score, "cond_score": a.cond_score, "max_s2": a.max_s2}}
    with open(os.path.join(a.gate_dir, "decision-input.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    def row(f):
        ev = [e for e in (f.get("evidence") or []) if e.get("type") in ("file", "count")]
        where = ("%s%s" % (ev[0].get("path"), (":%s" % ev[0].get("line")) if ev[0].get("line") else "")) if ev else "(no file evidence)"
        return "| %d | %s | %s | %s | %s | %s | %s |" % (priority(f), f.get("id"), f.get("severity"), f.get("lens"),
                                                         str(f.get("title", ""))[:70].replace("|", "/"), where, f.get("owner") or "—")

    md = ["# Gate decision input", "",
          "Profile **%s** · mode **%s** · weighted score **%.1f/100**" % (a.profile, a.mode, weighted), "",
          "## Recommendation: **%s**" % decision, ""]
    md += ["- " + r for r in reasons]
    md += ["", "_The chair may argue with this, but cannot override an open blocker without an owned, dated risk acceptance; S1 findings can't be accepted._",
           "", "## Lens scores (median across reviewers)", "", "| Lens | Weight | Score | Reviewers | Lowest | Note |", "|---|---|---|---|---|---|"]
    for lens, w, m, n, mn in lens_rows:
        note = "UNREVIEWED" if m is None else ("critical lens" if lens in CRITICAL else "")
        if m is not None and m < 2:
            note = "below 2 — " + note
        md.append("| %s | %s | %s | %s | %s | %s |" % (lens, w, "—" if m is None else ("%g" % m), n, "—" if mn is None else ("%g" % mn), note))
    md += ["", "## Counts", "",
           "Open findings — S1: %d · S2: %d · S3: %d · S4: %d · blockers: %d · accepted risks (valid): %d" %
           (sev_counts["S1"], sev_counts["S2"], sev_counts["S3"], sev_counts["S4"], len(blockers), len(valid_accepted)),
           "Evidence — verification %s · failed: %d · open S1/S2 with no file evidence: %d" %
           ("run" if verify is not None else "NOT RUN", len(failed_verify), len(unverified_high))]
    head = "| Priority | ID | Sev | Lens | Title | Where | Owner |\n|---|---|---|---|---|---|---|"
    md += ["", "## Blockers", ""] + ([head] + [row(f) for f in blockers] if blockers else ["None."])
    md += ["", "## Fix before ship", ""] + ([head] + [row(f) for f in fix_before] if fix_before else ["None."])
    md += ["", "## Carry over (priority order)", ""] + ([head] + [row(f) for f in carry[:20]] if carry else ["None."])
    if len(carry) > 20:
        md.append("")
        md.append("_%d more in decision-input.json._" % (len(carry) - 20))
    md += ["", "## Accepted risks", ""]
    if valid_accepted or invalid_accepted:
        md.append("| ID | Sev | Owner | Expires | Valid |\n|---|---|---|---|---|")
        for f in valid_accepted:
            md.append("| %s | %s | %s | %s | yes |" % (f.get("id"), f.get("severity"), f.get("owner"), f.get("due")))
        for f in invalid_accepted:
            md.append("| %s | %s | %s | %s | **no** (needs owner and expiry; S1 can't be accepted) |" %
                      (f.get("id"), f.get("severity"), f.get("owner") or "—", f.get("due") or "—"))
    else:
        md.append("None.")
    if wontfix:
        md += ["", "## Won't fix", ""] + ["- %s %s" % (f.get("id"), f.get("title")) for f in wontfix]
    with open(os.path.join(a.gate_dir, "decision-input.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print("decision: %s · score %.1f · blockers %d · open S2 %d · unreviewed lenses %d" %
          (decision, weighted, len(blockers), len(s2_open), len(unreviewed)))
    for r in reasons:
        print("  -", r)


if __name__ == "__main__":
    main()
