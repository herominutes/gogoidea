# Depth modes

Pick one with the user before starting. The point of three modes is honesty about effort: a quick run is a good gut-check, an exhaustive run is a decision-grade study, and neither should pretend to be the other.

## Settings by mode

| Setting | quick | standard | exhaustive |
|---|---|---|---|
| Evidence items read | ~100 | ~500 | 1,000+ |
| Source families (see `sources.md`) | 2 | 3+ | 5+ |
| Collection budget per `fetch_sources.py` call (always pass `--signal --max-items N`) | N=25, ≤4 calls per family | N=40, ≤8 calls per family | N=60, ≤12 calls per family |
| Sufficiency gate: pain / spend / switch items | 15 / 3 / 2 | 80 / 15 / 8 | 200 / 40 / 20 |
| Territories | 4 | 8 | 10–12 |
| Search angles per territory | 2 | 4 | 6+ |
| Scout types | complaint | complaint, pricing | complaint, pricing, timing, analogous |
| Ideator lenses used | 3 (best fit) | 6 | all 10 |
| Ideas into intake | ~8 | 15–20 | 30+ |
| Gauntlet rounds | 1 | 3 | 5 |
| Judge roles scoring each survivor (total) | 2 | 6 | 10 |
| Funnel target | 8 → 3 → 1 | 18 → 10 → 5 → 3 → 1 | 32 → 20 → 12 → 6 → 3 → 1 |
| Source-family gate for the winner | 1 | 2 | 3 |
| Journey / service blueprint | no | winner only | each finalist |
| Red team | no | light (one paragraph) | full, fresh context |
| Chairs | 1 | 1 | 2 independent |
| Weight sensitivity check | no | yes | yes + alternate weightings |
| Experiments designed | 1 | 2 | 3 (desirability, price, feasibility) |
| Deliverables | memo | memo + report | memo + report + assumption register + parked-ideas ledger |

Funnel targets are ceilings. Cut below them when kills are unanswered.

## Round composition

**quick — 1 round:** skeptic + builder together score every idea; chair keeps the top 3, then picks one.

**standard — 3 rounds**
1. *Market:* skeptic, economist, incumbent strategist
2. *Human + reality:* customer advocate, taste editor, builder
3. *Finals:* distribution strategist, risk & ethics, premortem; light red team on the leader; chair decides

**exhaustive — 5 rounds**
1. *Market:* skeptic, economist, incumbent strategist
2. *Human:* customer advocate, taste editor, design strategist
3. *Reality:* builder, distribution strategist, risk & ethics
4. *Finals:* premortem on each finalist, then steelman vs. red team
5. *Chair(s):* two independent chairs; report disagreement; run the sensitivity check with alternate weightings

## Running it efficiently

- **Parallelise by independence.** Scouts per source family, ideators per lens, judges per role are all independent — run them concurrently as subagents when available.
- **Batch judging.** One judge call can score up to ~6 ideas in a row. Randomise the order per judge to avoid order bias, and still keep each judge's scores private from the others.
- **Cheap models for collection, strong models for judgement.** Scouting and mining are extraction work; skeptic, strategy partner, red team and chair deserve the strongest model available.
- **State the effort up front.** For exhaustive, say roughly how many subagent calls to expect and confirm before launching.
- **Treat a quick-mode winner as a screen, not a decision.** Quick runs skip the economist, incumbent strategist, customer advocate and red team. In testing, a quick-mode winner (a paid migration utility) was killed in standard mode once the incumbent strategist found free tools already did the job. Say this in a quick memo's confidence line.
- **Resume, don't restart.** `state.json` records the finished stage; each stage's output is a file, so a failed run continues from the last file.
- **No subagents?** Play the roles sequentially yourself, but write each role's output to its file *before* starting the next role, and don't reread earlier judges' scores while scoring. It's weaker than true isolation; say so in the report's limitations.
