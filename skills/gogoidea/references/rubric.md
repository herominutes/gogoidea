# Scoring rubric, hard gates and schemas

Scores come from independent judges, are combined by the median, and are weighted. The scoreboard informs the chair; it doesn't replace judgement — but it makes the reasoning inspectable and keeps a good story from beating thin evidence.

Contents: [Criteria and anchors](#criteria-and-anchors) · [Default weights](#default-weights) · [Hard gates](#hard-gates) · [Protocol](#scoring-protocol) · [Schemas](#schemas)

## Criteria and anchors

Score 0–5. Anchors show what a 1, 3 and 5 look like; use the whole range, and justify any score ≤1 or ≥4 in writing.

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| **pain_severity** | Mild annoyance, easily lived with | Costs real time or money regularly | Blocking or emotionally charged; people vent publicly |
| **money_evidence** | No spend shown | One or two stated spends or paid alternatives | Many independent voices with named amounts and recurring spend |
| **switch_intent** | Complaints only | A few "looking at alternatives" | Explicit cancelling/switching, recent, across sources |
| **wedge_sharpness** | "Cheaper/better" | A clear reason, but the incumbent could match it in months | One-sentence reason to switch now; hard for the incumbent to copy quickly |
| **shippability** | Needs skills/time beyond the brief | Doable with scope cuts | v1 well inside the brief's time and skills |
| **distribution_access** | Buyers unreachable without budget | Reachable via one or two channels with effort | Founder already reaches them, or a cheap repeatable loop exists |
| **reach_at_price** | Needs >10% of the reachable pool to hit the money floor | ~3–5% required | <1% required; plenty of headroom |
| **defensibility** | Incumbent copies in a week | Copy takes months; some switching cost | Structural reason incumbents won't or can't follow |
| **timing** | "Someday" idea; no trigger | A trend that helps | A dated trigger (price hike, shutdown, platform shift) happening now |
| **craft_potential** | Needs a paragraph to explain; clutter-prone | Clear core with a few extras | One-sentence product, obvious delighter, "show a friend" moment |
| **support_burden** *(5 = light)* | Heavy support, compliance or payments exposure | Manageable with docs and boundaries | Near-zero support; self-serve and forgiving |

## Default weights

| Criterion | Weight |
|---|---|
| money_evidence | 3 |
| wedge_sharpness | 3 |
| pain_severity | 2 |
| switch_intent | 2 |
| shippability | 2 |
| distribution_access | 2 |
| reach_at_price | 2 |
| defensibility | 1 |
| timing | 1 |
| craft_potential | 1 |
| support_burden | 1 |

Total 20; the script normalises the weighted median to 0–100. Override with `weights.json` (`{"criterion": number}`) from the brief's Weights section. Omitted criteria keep their defaults.

## Hard gates

A failed gate cuts the idea regardless of score. The chair can override only by writing why. If G2 fails because no second source family is reachable (for example the buyers talk on Reddit or Facebook groups you can't read), say so, cap the idea's confidence at Low, and add collecting a second family to the first test.

| Gate | Rule |
|---|---|
| **G1 voices** | ≥3 independent voices across cited evidence (distinct authors/threads) |
| **G2 families** | Cited evidence spans ≥1 / ≥2 / ≥3 source families (quick / standard / exhaustive) |
| **G3 money** | At least one cited item showing money already spent in this space |
| **G4 shippable** | No judge verdict of `TOO BIG` |
| **G5 constraints** | No `VETO` from risk & ethics; no violation of the brief's constraints |
| **G6 no unanswered kill** | Status isn't marked `killed` by the chair |

## Scoring protocol

1. **Blind.** Judges see pitches under neutral ids (`I-01`…), in a per-judge random order, without ideator identity or others' scores.
2. **Independent.** Each judge writes scores before reading anyone else's.
3. **Evidence for extremes.** Any ≤1 or ≥4 needs a one-line reason citing evidence ids or brief fields.
4. **Median, not mean.** The script uses the median across roles per criterion so one outlier can't swing a result.
5. **Disagreement is information.** A spread ≥3 between roles on a criterion is flagged; the chair must say what the split reveals before ruling.
6. **Sensitivity.** The script re-ranks while perturbing each weight ±50%. A leader that holds in most scenarios is robust; one that flips deserves a closer look at the weights the founder really means.
7. **Later rounds add judges.** `scores.json` accumulates; each role's latest entry for an idea counts.

## Schemas

### `ideas.json`
```json
[
  {
    "id": "I-01",
    "name": "Receipt Sorter for Sole Traders",
    "lens": "productize a workaround",
    "customer": "sole traders who sort receipts by hand every month",
    "job": "When month-end arrives, I want my receipts sorted and totalled, so I can hand my accountant one file — but today I use a spreadsheet and an hour of my evening.",
    "wedge": "Photograph receipts all month; get one sorted, totalled file at month end.",
    "errc": {"eliminate": "manual sorting", "reduce": "month-end effort", "raise": "accuracy", "create": "one-file handoff to the accountant"},
    "price": {"amount": 24, "model": "monthly"},
    "v1": "photo inbox + category rules + monthly CSV and PDF export",
    "riskiest_assumption": "People will leave a spreadsheet they already own and trust.",
    "evidence": [{"id": "hackernews-0012", "quote": "exact verbatim span"}, {"id": "appstore-0033", "quote": "exact verbatim span"}],
    "status": "active",
    "cut_reason": null
  }
]
```
`status` is `active | cut | killed | parked | winner`. The chair sets it before the final scoring run; `killed` triggers gate G6. `price.model` is `monthly | annual | one-time | per-use` — state it explicitly, because the economist computes recurring and one-time revenue differently and will otherwise have to guess. `evidence[].quote` must appear verbatim in that item's `text` — `verify_quotes.py` checks it.

### `scores.json`
```json
{
  "I-01": {
    "skeptic":  {"scores": {"wedge_sharpness": 3, "money_evidence": 4, "pain_severity": 4, "switch_intent": 4, "distribution_access": 2}, "verdict": "SURVIVES", "note": "…"},
    "builder":  {"scores": {"shippability": 3, "support_burden": 2}, "verdict": "SHIPPABLE IF scope cut", "note": "e-sign is the hard part"},
    "economist":{"scores": {"reach_at_price": 3, "money_evidence": 4, "support_burden": 3}, "verdict": "VIABLE IF", "note": "…"}
  }
}
```
Verdict vocabulary: `KILL`, `SURVIVES`, `SHIPPABLE`, `SHIPPABLE IF …`, `TOO BIG`, `VIABLE`, `VIABLE IF …`, `NOT VIABLE`, `CLEAR`, `CLEAR IF …`, `VETO`.

### `mined.jsonl` (one line per tagged item)
```json
{"id": "hackernews-0012", "situation": "renewal email", "job": {"type": "functional", "outcome": "send contracts without a suite"}, "complaint": "price jumped", "who": "solo photographer", "workaround": "paid suite", "spend_usd_month": 129, "spend_text": "$129 month", "switch_intent": true, "severity": 3, "grade": "A", "quote": "exact verbatim span"}
```
