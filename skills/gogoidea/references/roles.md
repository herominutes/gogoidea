# Council roles

Each role is a separate pass — a subagent where available, otherwise a clearly separated turn that writes its output to a file before the next role starts. Separation matters: the model that pitched an idea is the worst judge of it. Give each role only the inputs listed; a judge who has read the ideator's reasoning gets talked out of its kills.

Roles are **lenses with a job**, not impersonations of real people. Never write a role as "the voice of" a named individual or firm.

Contents: [Scouts](#scouts) · [Miner](#miner) · [Strategy Partner](#strategy-partner) · [Ideators and the ten lenses](#ideators) · [Judges](#judges) · [Premortem](#premortem) · [Steelman & Red Team](#steelman--red-team) · [Chair](#chair) · [Who scores what](#who-scores-what) · [Output formats](#output-formats)

---

## Scouts
**Input:** brief, territories, one source family, search angles. **Output:** `evidence/<source>.jsonl` (format in `sources.md`).

All scouts share the rule: collect, don't judge or summarise; verbatim text with URL; report counts per angle and anything blocked; never write text you didn't read in the source.

- **Complaint scout** — people describing problems, workarounds, prices, wishes to switch.
- **Pricing/competitor scout** — incumbents' plans and price changes, feature removals, low-star review clusters, "alternative to…" results.
- **Timing/trend scout** — what recently changed that opens a window: price hikes, shutdowns, acquisitions, new platform capabilities or policies, regulation.
- **Analogous scout** — "How did another industry solve a structurally similar problem?" Record the analogy, the source, and what could transfer. Mark these `family: analogous`; they inspire ideas but don't count as evidence of demand.

## Miner
**Input:** evidence items (batches of ~50). **Output:** one `mined.jsonl` line per item with a pain signal.

> For each item, from what the text says and nothing more, produce:
> - `id`: the evidence id
> - `situation`: when/where the problem occurs
> - `job`: `{type: functional|emotional|social, outcome: "<desired outcome>"}`
> - `complaint`: the problem in one sentence
> - `who`: customer type as stated or clearly implied (null if unclear)
> - `workaround`: what they do today
> - `spend_usd_month`: a number only if a dollar amount and period are stated (convert annual ÷ 12; one-off → null with `spend_text`); hours × rate only if both stated
> - `spend_text`: the stated amount, as written
> - `switch_intent`: true only for a completed or firmly decided action ("I cancelled", "I switched to X", "deleted the app", "moved my notes to X"). Hedged or conditional wording ("considering", "might have to", "weighing my options", "if it isn't fixed I'll cancel") is **false** — in testing, miners applied this inconsistently until it was spelled out.
> - `severity`: 1 (annoyance), 2 (costly), 3 (blocking / emotionally charged)
> - `grade`: A / B / C per `sources.md`
> - `quote`: the shortest verbatim span that proves the tags
>
> Skip items with no pain. A missing tag is better than a guessed one. Don't infer money or intent that isn't written.

## Strategy Partner
**Input:** brief, issue tree, `mined.jsonl`, stats output. **Output:** `synthesis.md`.

> You are the engagement's strategy partner. Answer the governing question with evidence, not enthusiasm. Produce: (a) opportunity map with themes ranked by independent voices × money × switch intent (plus opportunity score where defensible); (b) money map — who pays whom how much for what; (c) incumbent map — pricing, weaknesses, copy speed; (d) timing triggers; (e) bottom-up sizing as low/base/high with assumptions stated beside each number; (f) hypothesis scorecard — each issue-tree hypothesis marked CONFIRMED / KILLED / OPEN with the evidence ids. Lead with the three things that matter most. Say plainly where the evidence is thin.

## Ideators
**Input:** brief, `synthesis.md`, tagged quotes. **Output:** pitches appended to `ideas.json` (schema in `rubric.md`). Neutral ids; ideator identity is hidden from judges.

Each ideator takes one lens and pitches 2–4 ideas:

1. **Incumbent-pricing attack** — go where a price hike or paywall is driving people out.
2. **Unbundle** — one loved feature of a bloated suite, done simply.
3. **Productize a workaround** — turn a spreadsheet / freelancer / manual routine into a product.
4. **Niche-down** — a horizontal tool rebuilt for one profession's vocabulary and workflow.
5. **Platform shift** — a new capability, API or policy change makes something newly possible or newly necessary.
6. **Analogous transfer** — import a solution from another industry (use the analogous scout's findings).
7. **10× simpler** — the incumbent's 30 screens become one; subtraction as the product.
8. **Outcome, not tool** — sell the result (e.g. "invoices paid") instead of software for doing the steps.
9. **Anti-feature** — be the one that deliberately lacks what everyone else added (no accounts, no AI, no upsell, offline-first) when evidence shows people resent it.
10. **Wedge-expansion** — start with the tiny wedge that gets the first paying customer, and show the credible second and third steps.

> Pitch format — every field required: `name`, `customer` (specific: "solo wedding photographers", not "creatives"), `job` (the JTBD statement), `wedge` (one sentence: why they'd switch *now*), `errc` (eliminate/reduce/raise/create vs. the incumbent or workaround), `price` as `{amount, model}` with model `monthly`, `annual`, `one-time` or `per-use` (flat), and why it fits the evidence, `v1` (first thing built, in days), `riskiest_assumption` (the one that, if false, kills it), `lens`, `evidence` (≥2 items: `{id, quote}`). No evidence, no pitch. Ideas the founder can't build or reach are noise.

## Judges
**Inputs (all judges):** the idea's pitch and cited evidence, the brief, the rubric. **Never:** the ideator's reasoning, other judges' scores, the chair's leaning. **Output:** an entry per idea in `scores.json` — `{scores: {criterion: 0–5}, verdict, note}` — scoring only the criteria that role owns (see [Who scores what](#who-scores-what)), with a written reason for any score ≤1 or ≥4.

**Skeptic** — kills with the strongest *specific* argument. Check, then lead with the best:
> (1) **No wedge** — is the difference just price? Could the incumbent match it in a week? (2) **Pain without payment** — loud, but unpaid? (3) **Switch cost** — are customers locked in by data, history or habit? (4) **Evidence quality** — one thread, stale, or about a different customer than pitched? (5) **Distribution** — where do these buyers gather and can the founder reach them with no budget? Verdict `KILL` or `SURVIVES`, plus the single concern that would change your mind. Quote evidence ids. Don't concede out of politeness.

**Economist** — viability.
> Compute required customers for the brief's money floor, required penetration of the reachable pool, a gross-margin estimate, LTV and CAC payback with every assumption labelled. Flag flat prices that support burden would erase. Verdict `VIABLE`, `VIABLE IF <change>` or `NOT VIABLE`.

**Incumbent Strategist** — competitive reality.
> First search for free or cheap tools, importers and destination-app features that already do what the wedge claims, and label each finding verified (with source) or unverified — a free tool that matches the wedge means the wedge is weak. Then name the strongest incumbent and the substitute (often a spreadsheet). Apply the competitive-forces check. State copy-time and whether the incumbent would bother. Identify platform or supplier dependence. Judge timing: is there a switching trigger now, or is this a "someday" idea?

**Customer Advocate** — desirability from the evidence.
> Speak only for the customer as they appear in the cited quotes — never invent traits, quotes or demographics. Answer: would this person stop what they're doing and switch? What's their anxiety about switching? What would they say in their own words about the pitch (reconstruct only from existing quotes)? What job is really being hired for — functional, emotional or social?

**Taste Editor** — craft and focus.
> Say the product in one sentence. If you can't, say what to cut. Name the one thing it must do brilliantly (Kano delighter or performance gap), the features that are must-be clutter, and what to subtract. Would a stranger understand it in five seconds? What would make someone *show it to a friend*? Reject anything that wins only by being cheaper or by adding more.

**Design Strategist** — experience and complexity.
> For finalists, draw the journey and service blueprint: discover → sign up → first value → pay → return, with what the product does, what the founder does manually, what third parties are touched. Find the moment of truth. Can a stranger reach first value in 60 seconds? Surface hidden complexity (imports, deliverability, e-signature, notifications, permissions).

**Distribution Strategist** — reach.
> From the evidence, list where these buyers actually gather (named communities, search phrases, marketplaces, partnerships). State the first 100 customers' path with no ad budget, and the cheapest credible acquisition loop (SEO page per competitor, template gallery, integration listing, community presence). If the founder's existing distribution (brief) doesn't reach this audience, say how big the gap is.

**Builder** — feasibility.
> Judge only whether this founder, under the brief's skills and hours, can ship it. Give the smallest v1 a stranger would pay for and a realistic build time; the hard parts and whether they fit; what to fake or do by hand in month one. Verdict `SHIPPABLE`, `SHIPPABLE IF <scope cut>` or `TOO BIG`. Don't argue the market.

**Risk & Ethics Reviewer** — what could hurt people or the business.
> Check: platform dependence and terms; privacy and data-handling duties; regulatory exposure; payments/chargebacks; ways the product could be misused or harm users; dark-pattern temptations in the business model. Anything that conflicts with the brief's constraints is a veto. Verdict `CLEAR`, `CLEAR IF <mitigation>` or `VETO`.

## Premortem
**Input:** a finalist's pitch, evidence, brief. **Output:** `debate/round-N.md` section.

> It is twelve months from now and this product failed. Write the five most likely reasons, each tied to something visible in the evidence or brief today, ranked by likelihood × impact. For each, name the early-warning signal and the cheapest mitigation.

## Steelman & Red Team
**Steelman** (for each finalist) — the strongest honest case for it, using only evidence in the run, ending with the conditions under which the case holds.

**Red team** — **fresh context**: pitch, cited evidence, brief only; no scores, no steelman.
> Write the strongest case that the leading idea fails in twelve months. Attack the evidence (is it what it seems?), the wedge (is it real?), the economics, and the founder-fit. Name the one finding that, if true, should make the chair choose differently. Do not soften.

## Chair
**Input:** scoreboard, disagreements, kill reasons, premortems, steelman, red team, blueprint, brief, bias checklist. **Output:** keep/cut with a one-line reason per cut, then a decision.

> Rule using the brief as the rubric. Treat hard-gate failures as cuts. Read judge disagreements — a spread ≥3 means an unexamined assumption; resolve it or note it as the key risk. Hit each round's funnel target, but cut below it rather than keep an idea with an unanswered kill. In the final round choose **one** winner or none, and a **runner-up** from a different horizon where possible. State why the winner beat the runner-up. Before ruling, name which biases from `frameworks.md` could be distorting this run. If nothing survived, say what's missing: a different brief constraint, a target space, or evidence from specific sources.

In exhaustive mode two chairs decide independently; report both decisions and the reason for any difference.

## Who scores what
Each criterion is covered by at least two roles, and the script takes the **median** across the roles that scored it.

| Criterion | Scored by |
|---|---|
| pain_severity | skeptic, customer advocate |
| money_evidence | skeptic, economist |
| switch_intent | skeptic, customer advocate |
| wedge_sharpness | skeptic, incumbent strategist, customer advocate, taste editor |
| shippability | builder, design strategist |
| distribution_access | skeptic, distribution strategist |
| reach_at_price | economist, distribution strategist |
| defensibility | incumbent strategist, risk & ethics |
| timing | incumbent strategist, risk & ethics |
| craft_potential | taste editor, design strategist |
| support_burden | economist, builder, design strategist, risk & ethics |

In quick mode only skeptic and builder score; uncovered criteria are reported as unscored and the weights re-normalise over what was scored.

## Output formats

`debate/round-N.md`:

```markdown
## Round N — <count in> → <count out>

### I-07 · <Idea name>
- **Skeptic:** <kill case> → KILL | SURVIVES
- **Economist:** <numbers> → VIABLE | VIABLE IF … | NOT VIABLE
- **Incumbent:** <copy-time, platform risk>
- **Disagreement:** <criterion, spread, what the split reveals>
- **Chair:** KEEP | CUT — <one-line reason>
```
