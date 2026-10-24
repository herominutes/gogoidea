# Report templates

Two documents. The **memo** is for deciding; the **report** is the proof behind it. Write the memo first — if you can't state the answer in a page, the analysis isn't done.

## `council-memo.md` — answer-first, one page

```markdown
# <Idea name> — Idea Council memo
<founder> · <date> · mode: <quick|standard|exhaustive>

## Recommendation
<One sentence: test <idea> for <customer> at $<price>/mo — or "No idea survived; here is what would change that.">

## Why (three reasons, each with evidence)
1. **Pain + money:** <the strongest A-grade quote, URL, spend figure>
2. **Wedge:** <the one-sentence reason to switch now; why the incumbent can't match it quickly>
3. **Fit:** <why this founder can ship and reach it — hours, skills, distribution>

## Size (range)
<low / base / high customers and MRR, with the pool and key assumptions>

## What would make us wrong
- <red team's top finding>
- <riskiest assumption and the test that resolves it>

## Next 7 days
<the pre-registered test: audience, volume, pass bar, kill criteria>

## Confidence
<Low | Medium | High> — <one line why; state evidence limits>
```

## `report.md` — the backing

Keep it scannable; link to run files for detail.

```markdown
# Idea Council report — <founder / date>

## 1. Verdict
<Same sentence as the memo. Winner, runner-up, and one line on each.>

## 2. Brief
<Condensed to 5 lines: who, can build, speed, money floor, constraints, distribution, taste.>

## 3. Method & what was actually done
- Mode, number of subagent roles run, whether judging was truly isolated
- Evidence read: <N> items by source and family; items with pain / dollar spend / switch intent; grade mix (A/B/C)
- Not reached or thin: <blocked or sparse sources>

## 4. Issue tree & hypothesis scorecard
| Branch | Hypothesis | Result | Evidence |
|--------|------------|--------|----------|

## 5. Opportunity, money and incumbent maps
- Top themes (independent voices · money · switch intent · opportunity score if used)
- Money map: who pays whom how much
- Incumbent map: pricing, weaknesses, copy-time
- Timing triggers

## 6. The funnel
`<N pitched> → <N> → … → <winner or none>`

| Idea | Lens | Died in | Kill reason | Score |
|------|------|---------|-------------|-------|

Scoreboard (from `scoreboard.md`): final ranking, gate failures, judge disagreements, sensitivity result (how often the leader stays first when weights change).

## 7. The survivor: <name>
- Customer · job · wedge · price
- ERRC line vs. the incumbent
- Why it won: 2–3 verbatim quotes with URLs
- Journey & service blueprint — moment of truth and hidden complexity
- Premortem top causes and early-warning signals
- Red team's strongest case and our answer
- Horizon (H1/H2/H3)

## 8. Runner-up and parked ideas
<Runner-up, why it lost, which horizon it sits in, what would revive it. One line per other parked idea.>

## 9. Assumption register
| # | Assumption | Impact if wrong | Uncertainty | Test |
|---|-----------|-----------------|-------------|------|

## 10. Pre-registered tests
<One block per test using the template in `experiments.md`.>

## 11. Biases and limitations
<Which biases from `frameworks.md` could be distorting this run; sources missed; sample sizes; any role that wasn't isolated.>
```

If nothing survived, replace section 7 with **Why nothing survived** (dominant kill reasons) and **What would change that** (a different constraint, a target space, specific extra evidence), and still keep the runner-up/parked ledger — the ideas are reusable.
