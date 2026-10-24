#!/usr/bin/env python3
"""Check that every quote cited by the council appears verbatim in its evidence item.

Usage: verify_quotes.py <run-dir>

Checks `quote` in mined.jsonl and `evidence[].quote` in ideas.json against the
`text` of the evidence item with the same id (evidence/*.jsonl). Matching ignores
case, curly-vs-straight quotes/dashes and whitespace. A quote written with "…"
or "..." is split into fragments and each fragment must appear.

Exit code 1 if any quote fails, so a run can't proceed on invented evidence.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from council_common import load_evidence, load_json, read_jsonl  # noqa: E402

TRANSLATE = {ord(c): t for c, t in {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ",
}.items()}


def norm(s):
    s = (s or "").translate(TRANSLATE).lower()
    return re.sub(r"\s+", " ", s).strip(" \"'")


def matches(quote, text):
    text_n = norm(text)
    fragments = [f for f in re.split(r"…|\.\.\.", quote or "")]
    fragments = [norm(f) for f in fragments if len(norm(f)) >= 8]
    if not fragments:
        return False
    return all(f in text_n for f in fragments)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = sys.argv[1]
    evidence = load_evidence(run)
    if not evidence:
        sys.exit(f"No evidence found in {run}/evidence/*.jsonl")

    checked = failed = 0
    problems = []

    for row in read_jsonl(os.path.join(run, "mined.jsonl")):
        checked += 1
        ev = evidence.get(row.get("id"))
        if ev is None:
            failed += 1
            problems.append(f"mined {row.get('id')}: no such evidence id")
        elif not matches(row.get("quote"), ev.get("text")):
            failed += 1
            problems.append(f"mined {row.get('id')}: quote not found verbatim: {row.get('quote')!r}")

    for idea in load_json(os.path.join(run, "ideas.json"), []) or []:
        for cite in idea.get("evidence", []):
            checked += 1
            ev = evidence.get(cite.get("id"))
            label = f"idea {idea.get('id')} cites {cite.get('id')}"
            if ev is None:
                failed += 1
                problems.append(f"{label}: no such evidence id")
            elif not matches(cite.get("quote"), ev.get("text")):
                failed += 1
                problems.append(f"{label}: quote not found verbatim: {cite.get('quote')!r}")

    print(f"Checked {checked} quotes: {checked - failed} verified, {failed} failed.")
    for p in problems:
        print("  FAIL", p)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
