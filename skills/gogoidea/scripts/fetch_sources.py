#!/usr/bin/env python3
"""Collect public posts/reviews as normalized JSONL for the Idea Council.

Free, unauthenticated endpoints only. Standard library only.

Usage:
  fetch_sources.py hn            --query "alternative to <product>" [--limit 50]
  fetch_sources.py stackexchange --query "invoice clients" --site webapps [--limit 50]
  fetch_sources.py github        --query "wish hosted version" [--limit 30]
  fetch_sources.py reddit        --query "<product> expensive" [--subreddit <name>] [--limit 50]
  fetch_sources.py appstore      --app-id 1234567890 [--country us] [--pages 3]
  fetch_sources.py appsearch     --query "<product>"     (prints id, name, price, rating count)

Every command prints one JSON object per line:
  {"id","source","url","date","author","title","text","score"}
Append to evidence/<source>.jsonl with >> and re-number ids with --prefix/--start.
Add --signal to drop items with no money/pricing/switching/wish language (search APIs
are fuzzy; in testing most raw hits were irrelevant, so use it on broad queries) and
--max-items N to stop after N items. In testing, an uncapped quick-mode run collected
~1,100 rows against a target of ~100, so always pass both.
Errors (rate limits, blocks) go to stderr and exit code 0 so a blocked source
doesn't abort a run; note them in the report.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "gogoidea/1.0 (public-research tool; no personal data collected)"
TAG_RE = re.compile(r"<[^>]+>")


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {url}", file=sys.stderr)
    except Exception as e:  # network down, bad JSON, timeout
        print(f"[error] {url}: {e}", file=sys.stderr)
    return None


def clean(text, limit=1500):
    text = html.unescape(TAG_RE.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def iso(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None


# Cheap relevance prefilter for --signal: keep items that mention money, pricing,
# cancelling/switching or an unmet wish. Search APIs are fuzzy, so most raw hits are noise.
SIGNAL_RE = re.compile(
    r"(\$\s?\d|\b\d+\s?(usd|dollars|/mo|per month|a month|/month|/yr)\b|price|pricing|expensive|"
    r"overpriced|subscription|cancel|switch(ed|ing)?\b|alternative|migrat|wish (there|it)|"
    r"looking for|too (much|costly)|fees?\b|churn|workaround|spreadsheet|manually)", re.I)


class Emitter:
    def __init__(self, source, prefix, start, signal=False, cap=0):
        self.source, self.prefix, self.n, self.signal = source, prefix or source, start, signal
        self.cap, self.emitted = cap, 0

    @property
    def full(self):
        return bool(self.cap) and self.emitted >= self.cap

    def emit(self, **kw):
        if not kw.get("text"):
            return
        if self.signal and not SIGNAL_RE.search(kw["text"]):
            return
        if self.full:
            return
        self.n += 1
        self.emitted += 1
        rec = {"id": f"{self.prefix}-{self.n:04d}", "source": self.source,
               "url": kw.get("url"), "date": kw.get("date"), "author": kw.get("author"),
               "title": kw.get("title"), "text": kw["text"], "score": kw.get("score")}
        print(json.dumps(rec, ensure_ascii=False))


def hn(a, em):
    q = urllib.parse.quote(a.query)
    for tags in ("story", "comment"):
        if em.full:
            break
        d = get_json(f"https://hn.algolia.com/api/v1/search?query={q}&tags={tags}&hitsPerPage={min(a.limit, 100)}")
        for h in (d or {}).get("hits", []):
            text = clean(h.get("comment_text") or h.get("story_text") or h.get("title"))
            em.emit(url=f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    date=(h.get("created_at") or "")[:10], author=h.get("author"),
                    title=h.get("title") or h.get("story_title"), text=text, score=h.get("points"))
        time.sleep(0.5)


def stackexchange(a, em):
    q = urllib.parse.quote(a.query)
    d = get_json("https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance"
                 f"&q={q}&site={a.site}&pagesize={min(a.limit, 100)}&filter=withbody")
    for it in (d or {}).get("items", []):
        em.emit(url=it.get("link"), date=iso(it.get("creation_date")),
                author=(it.get("owner") or {}).get("display_name"),
                title=html.unescape(it.get("title", "")), text=clean(it.get("body")),
                score=it.get("score"))


def github(a, em):
    q = urllib.parse.quote(f"{a.query} is:issue")
    d = get_json(f"https://api.github.com/search/issues?q={q}&per_page={min(a.limit, 100)}",
                 headers={"Accept": "application/vnd.github+json"})
    for it in (d or {}).get("items", []):
        em.emit(url=it.get("html_url"), date=(it.get("created_at") or "")[:10],
                author=(it.get("user") or {}).get("login"), title=it.get("title"),
                text=clean(f"{it.get('title', '')}. {it.get('body') or ''}"),
                score=it.get("reactions", {}).get("total_count"))


def reddit(a, em):
    q = urllib.parse.quote(a.query)
    base = f"https://www.reddit.com/r/{a.subreddit}/search.json?restrict_sr=1&" if a.subreddit \
        else "https://www.reddit.com/search.json?"
    d = get_json(f"{base}q={q}&limit={min(a.limit, 100)}&sort=relevance")
    if d is None:
        print("Reddit blocked or unavailable; fall back to WebSearch with site:reddit.com", file=sys.stderr)
    for c in ((d or {}).get("data") or {}).get("children", []):
        p = c.get("data", {})
        em.emit(url="https://www.reddit.com" + p.get("permalink", ""), date=iso(p.get("created_utc")),
                author=p.get("author"), title=p.get("title"),
                text=clean(f"{p.get('title', '')}. {p.get('selftext', '')}"), score=p.get("score"))


def appsearch(a, em):
    """Look up App Store ids for appstore reviews. Prints TSV, not evidence."""
    q = urllib.parse.quote(a.query)
    d = get_json(f"https://itunes.apple.com/search?term={q}&entity=software&limit={min(a.limit, 10)}"
                 f"&country={a.country}")
    for r in (d or {}).get("results", []):
        print("\t".join(str(x) for x in (r.get("trackId"), r.get("trackName"), r.get("price"),
                                          r.get("userRatingCount"))))


def appstore(a, em):
    for page in range(1, a.pages + 1):
        if em.full:
            break
        d = get_json(f"https://itunes.apple.com/{a.country}/rss/customerreviews/page={page}"
                     f"/id={a.app_id}/sortby=mostrecent/json")
        entries = ((d or {}).get("feed") or {}).get("entry") or []
        for e in entries:
            if "im:rating" not in e:  # first entry is app metadata
                continue
            title = (e.get("title") or {}).get("label", "")
            body = (e.get("content") or {}).get("label", "")
            em.emit(url=(e.get("author") or {}).get("uri", {}).get("label"),
                    date=((e.get("updated") or {}).get("label") or "")[:10],
                    author=((e.get("author") or {}).get("name") or {}).get("label"),
                    title=title, text=clean(f"{title}. {body}"),
                    score=int(e["im:rating"]["label"]))
        time.sleep(0.5)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", choices=["hn", "stackexchange", "github", "reddit", "appstore", "appsearch"])
    p.add_argument("--query")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--site", default="stackoverflow", help="stackexchange site")
    p.add_argument("--subreddit")
    p.add_argument("--app-id")
    p.add_argument("--country", default="us")
    p.add_argument("--pages", type=int, default=3)
    p.add_argument("--prefix", help="id prefix, default = source name")
    p.add_argument("--start", type=int, default=0, help="id counter start (to append to existing file)")
    p.add_argument("--max-items", type=int, default=0,
                   help="stop after this many items (0 = no cap); use it to respect the mode's collection budget")
    p.add_argument("--signal", action="store_true",
                   help="keep only items mentioning money, pricing, cancelling/switching or an unmet wish")
    a = p.parse_args()

    if a.source == "appstore" and not a.app_id:
        p.error("--app-id is required for appstore")
    if a.source != "appstore" and not a.query:
        p.error("--query is required")

    names = {"hn": "hackernews", "stackexchange": "stackexchange", "github": "github",
             "reddit": "reddit", "appstore": "appstore", "appsearch": "appsearch"}
    em = Emitter(names[a.source], a.prefix, a.start, a.signal, a.max_items)
    {"hn": hn, "stackexchange": stackexchange, "github": github, "reddit": reddit,
     "appstore": appstore, "appsearch": appsearch}[a.source](a, em)


if __name__ == "__main__":
    main()
