# Evidence sources

Free, public sources only. No logins, no paid APIs, no scraping behind walls. Be gentle: a few requests per second at most, a descriptive User-Agent, stop on 429s, and respect each site's terms and robots rules. When a site disallows automated access, skip it or read a handful of pages manually via WebFetch and quote sparingly.

## Source families

The council triangulates across **families**, not individual sites — three subreddits are still one family (forum). `scripts/evidence_stats.py` maps sources to families automatically.

| Family | Sources | Good for | How |
|---|---|---|---|
| **forum** | Hacker News, Reddit, Indie Hackers, niche communities | Niche-profession pain, "alternatives to X", pricing rants | `fetch_sources.py hn` / `reddit`; Reddit is often blocked → WebSearch with `site:reddit.com` |
| **reviews** | App Store, Google Play, Trustpilot, G2, Capterra, Chrome Web Store | Price complaints, churn reasons, "switching" | `fetch_sources.py appstore`; others via WebSearch/WebFetch |
| **qa** | Stack Exchange network | Workarounds = unmet needs ("how do I do X in Excel/Zapier") | `fetch_sources.py stackexchange` |
| **code** | GitHub issues and discussions | Missing features in open-source tools; "I'd pay for hosted…" | `fetch_sources.py github` (unauthenticated search is rate-limited) |
| **spend** | Public freelance job posts, job ads for manual roles, marketplace bestseller lists, template/course sales pages | Proof that people already pay for the workaround | WebSearch/WebFetch, read lightly |
| **market** | Competitor pricing pages and changelogs, price-hike/shutdown announcements, Product Hunt launches, Google Trends | Incumbent weaknesses, copy speed, switching moments | WebSearch/WebFetch |

Exhaustive mode needs five or more families; standard three or more.

## What worked and what didn't (from a test run)

- **App Store reviews were the most productive verbatim source.** Find app ids with `fetch_sources.py appsearch`, pull 3 pages per app with `--signal`, then mine the 1–3★ reviews that mention a price or a switch. Reviews skew toward angry leavers and iOS users, so say so in the limitations.
- **Hacker News search is noisy** (about 1 usable item in 50 for broad queries): use `--signal`, specific incumbent names, and treat HN as a supporting family.
- **Reddit is usually unreachable.** The script gets HTTP 403 and WebSearch's `site:reddit.com` returned no Reddit threads. Don't plan a run around Reddit; if the user can export or paste threads, use those.
- **WebSearch returns summaries, not quotable text.** Use it for the pricing/competitor and timing scouts (price hikes, alternatives lists), mark the results *secondhand, possibly vendor-biased*, and never count them toward voices, families or `verify_quotes.py`. Only text you retrieved verbatim is evidence.

## Scout types and the angles they use

- **Complaint scout** — people describing a problem: "too expensive", "price increase", "cancelled my subscription", "gave up on", "so clunky".
- **Pricing/competitor scout** — incumbent pricing pages, plan changes, feature removals, review-site 1–3★ clusters, "alternative to <incumbent>" search results.
- **Timing/trend scout** — what changed recently that opens a window: price hikes, acquisitions and shutdowns, new platform APIs or policies, regulation, a new cheap capability.
- **Analogous scout** — how a *different* industry solved a structurally similar problem (e.g. how dental clinics handle recalls → ideas for pet groomers). Record the analogy, source URL and what transfers.
- Mix in: **switching intent** ("switching from", "looking for something cheaper than"), **workaround spend** ("I pay a VA to", "I hired a freelancer for", "I use a spreadsheet to"), **wish phrases** ("wish there was", "why doesn't <tool> support").

## Evidence item format (JSONL, one per line)

```json
{"id": "hackernews-0042", "source": "hackernews", "url": "https://…", "date": "2026-03-02", "author": "public handle or null", "title": "…", "text": "verbatim passage", "score": 31}
```

Rules:
- `text` is verbatim. Trim for length; never paraphrase into it.
- `id` is stable, so ideas and kills can cite it.
- Drop exact duplicates and obvious spam or promotional posts.
- Note what you could **not** reach (blocked or thin sources) — it goes in the report's limitations.

## Evidence grades

Miners assign each tagged item a grade; the synthesis weights by it.

| Grade | Meaning |
|---|---|
| **A** | A named dollar amount or explicit switching action ("cancelled", "moved to X") in the person's own words, recent (≈ last 24 months) |
| **B** | Specific, first-hand complaint with a workaround but no money or action stated |
| **C** | General grumbling, second-hand claim, old, or unclear customer |

## Quote hygiene

Quote the shortest span that proves the point. Keep quotes verbatim so `verify_quotes.py` can match them. Cite the public handle only when needed to distinguish voices; the evidence is about the complaint, not the person.
