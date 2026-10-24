"""Shared helpers for the Idea Council scripts (standard library only)."""
import glob
import json
import os
import sys

# Source name -> family. Unknown sources become their own family.
FAMILY = {
    "hackernews": "forum", "reddit": "forum", "indiehackers": "forum", "forum": "forum",
    "appstore": "reviews", "googleplay": "reviews", "trustpilot": "reviews",
    "g2": "reviews", "capterra": "reviews", "chromewebstore": "reviews",
    "stackexchange": "qa", "stackoverflow": "qa",
    "github": "code",
    "upwork": "spend", "fiverr": "spend", "jobads": "spend", "marketplace": "spend",
    "pricing": "market", "changelog": "market", "producthunt": "market",
    "trends": "market", "news": "market",
    "analogous": "analogous",
}


def family_of(source):
    return FAMILY.get((source or "").lower(), (source or "unknown").lower())


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warning: {path}:{n} is not valid JSON ({e})", file=sys.stderr)
    return rows


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_evidence(run_dir):
    """Return {id: record} across evidence/*.jsonl, with a 'family' field added."""
    out = {}
    for p in sorted(glob.glob(os.path.join(run_dir, "evidence", "*.jsonl"))):
        for r in read_jsonl(p):
            if "id" in r:
                r.setdefault("family", family_of(r.get("source")))
                out[r["id"]] = r
    return out


def voice_key(rec):
    """Independent voice = distinct (source, author) or, if anonymous, distinct URL."""
    who = rec.get("author")
    if who:
        return (rec.get("source"), who)
    return (rec.get("source"), rec.get("url"))
