# Idea track — what should I build?

This is the **Idea** track of GoGoIdea (see `SKILL.md` for the 5-step summary). It is a design-strategy process for founders: start from real people's problems, diverge on ideas, then converge with independent judgement. The detailed stages below expand the five steps: 1 Brief = stages 0–1; 2 Evidence = stages 2–3; 3 Ideas = stages 4–6; 4 Judge = stages 7–8; 5 Decide and test = stage 9.

Most idea generation fails because ideas come from vibes and are judged by whoever pitched them. This skill reverses both: ideas come from **public evidence**, and they are judged by **separate roles** that never saw the pitcher's reasoning. An idea survives only if the **pain**, the **money already spent**, and the **intent to switch** show up in the same places — and the founder can ship and reach it.

Two traditions are blended on purpose:

- **Design-strategy practice** (human-centred design, jobs-to-be-done, double-diamond divergence/convergence, journey and service blueprints, a discipline of subtraction): is it *desirable*, and does it feel inevitable?
- **Strategy-consulting practice** (hypothesis-first work, MECE issue trees, sizing with ranges, unit economics, competitive-force checks, answer-first communication): is it *viable*, and is the logic airtight enough to defend?

These are widely known lenses, not any firm's proprietary method; `references/frameworks.md` explains each and how the council uses it.

**"Nothing survived" is a valid and valuable result.** Never pad the list. A killed idea saves weeks, and the kill reasons are often the most useful output.

## Choose depth first

Read `references/modes.md`, then settle the mode with the user in one message (infer it when they've signalled; default **standard**):

| Mode | Evidence | Ideas in | Judge roles per idea | Gauntlet rounds | Typical use |
|---|---|---|---|---|---|
| quick | ~100 items | ~8 | 2 | 1 | "gut-check in minutes" |
| standard | ~500 | ~15–20 | 6 | 3 | the normal run |
| exhaustive | 1,000+ across 5+ source families | 30+ | 10 | 5 + red team | a decision worth weeks of building |

Exhaustive can mean dozens of subagent calls. Tell the user the rough count and get a yes before launching it.

## The pipeline

```
Brief → Issue tree & territories → Scouts → Miners → Synthesis → Ideators → Intake gate
      → Gauntlet (blind scoring + role attacks, N rounds) → Red team → Chair → Memo → 7-day tests
```

Work in `council-runs/<slug>/` so every stage is inspectable and resumable. Keep `state.json` (`{"mode","stage","completed":[...]}`) updated after each stage; on resume, read it and continue rather than restarting.

```
brief.md  issue-tree.md  territories.md  evidence/*.jsonl  mined.jsonl  synthesis.md
ideas.json  scores.json  scoreboard.md  debate/round-N.md  redteam.md
assumptions.md  report.md  council-memo.md
```

### 0 · Brief
Use `references/brief-template.md`. Draft it from the conversation when possible and confirm in one message instead of re-interviewing. The brief is the rubric: skills, hours, money floor, constraints, distribution, **taste** (what the founder would be proud to ship), and **weights** (what matters most). Push once for specifics — "ships a CRUD SaaS in two weeks, 10 hrs/week, no sales calls" lets the builder reject a hundred ideas instantly.

### 1 · Issue tree and territories
Write the governing question ("What is the single product this founder should test next, and why?") and decompose it into a **MECE issue tree** — branches that don't overlap and together cover the space (e.g. *where is there money* / *where is there pain* / *where can this founder win* / *why now*). State an initial **hypothesis** for each branch; the evidence will confirm or kill them. Then turn the brief into 6–12 **problem territories** phrased as "How might we…" questions so scouts cover distinct ground instead of one echo chamber. Save both.

### 2 · Scouts — collect public evidence
Read `references/sources.md`. Free, public sources only. Four scout types (`references/roles.md`): **complaint**, **pricing/competitor**, **timing/trend**, and **analogous inspiration** (how a different industry solved a similar problem — a design-research habit that finds wedges nobody in the niche has tried). Use `scripts/fetch_sources.py` where it covers a source, WebSearch/WebFetch elsewhere, and parallel subagents per source family when available. Every item: id, URL, verbatim text. State true counts in the report. **Respect the mode's collection budget** (`references/modes.md`): always pass `--signal` and `--max-items`, and stop when the target is met — over-collecting wastes effort and buries the signal.

### 3 · Miners — tag as jobs-to-be-done
Per `references/roles.md` → Miner: extract situation, job (functional/emotional/social), desired outcome, workaround, **dollars already spent**, switch intent, severity, and a verbatim quote. Drop items with no pain; never guess a tag. Then run `python scripts/verify_quotes.py <run-dir>` — fix or drop any quote that fails — and `python scripts/evidence_stats.py <run-dir> --mode <mode>` for counts, independent-voice tallies and the **sufficiency gate**.

**Sufficiency gate.** The stats end in READY or NOT READY (minimum pain items, spend items, switch-intent items and source families for the mode). Search APIs are fuzzy — in testing, most raw hits for broad queries were irrelevant — so thin results are normal on a first pass. If NOT READY, go back to the scouts with sharper angles and more source families (use `--signal` on `fetch_sources.py`, and WebSearch for sources it can't reach), then re-mine. If it is still thin after a second pass, stop and report that honestly: "not enough evidence to ideate", what was collected, and what to collect next. Ideating on thin evidence produces confident-sounding fiction, which is the failure this skill exists to prevent.

### 4 · Synthesis — the Strategy Partner's pass
Write `synthesis.md`:
(a) **opportunity map** ranked by independent voices × money × switch intent, with an importance-vs-satisfaction opportunity score where evidence supports one;
(b) **money map** — what people already pay, to whom, how much;
(c) **incumbent map** — who, price, evident weaknesses, how fast they could copy;
(d) **timing triggers** — price hikes, shutdowns, platform shifts that create switching moments;
(e) **sizing** — bottom-up reachable-buyers × price as a **range with stated assumptions**, never a single confident number;
(f) **hypothesis scorecard** — which issue-tree hypotheses the evidence confirmed, killed, or left open.

### 5 · Ideators — pitch through ten lenses
Pitch only as many ideas as the evidence supports — if the clusters yield ten distinct ideas, say so rather than padding to the mode's target. Per `references/roles.md` → Ideator lenses (incumbent-pricing attack, unbundle, productize a workaround, niche-down, platform shift, analogous transfer, 10× simpler, outcome-not-tool, anti-feature, wedge-expansion). Each lens pitches 2–4 ideas in the pitch format, with ≥2 cited evidence ids, an **eliminate/reduce/raise/create** line against the incumbent, and a stated **riskiest assumption**. Assign neutral ids (`I-01`…); ideator identity is hidden from judges. Schemas are in `references/rubric.md`.

### 6 · Intake gate
Dedupe; run `verify_quotes.py`; reject pitches with no evidence, constraint violations, or a customer too vague to name. Hard gates live in `references/rubric.md`.

### 7 · The gauntlet
Rounds, roles and the scorecard are in `references/roles.md` and `references/rubric.md`; round composition per mode is in `references/modes.md`. The shape in the deepest mode:

1. **Market** — skeptic, economist, incumbent strategist
2. **Human** — customer advocate, taste editor, design strategist
3. **Reality** — builder, distribution strategist, risk & ethics reviewer
4. **Finals** — premortem, then steelman vs. red team on each finalist
5. **Chair** decides

Each round, judges score every surviving idea **independently and blind** on the rubric (0–5 per criterion, with written evidence for any score ≤1 or ≥4), writing to `scores.json`. Run `python scripts/score_ideas.py <run-dir> --sensitivity` to compute medians, flag judge disagreement, apply hard gates, print the scoreboard and test whether the leader survives weight changes. The chair reads the scoreboard *and* the disagreements — a split verdict means an unexamined assumption, so resolve it before cutting or keeping. Save each round to `debate/round-N.md` including every kill reason.

Preserve independence: judges get the pitch and cited evidence, not the ideator's reasoning, other judges' scores, or the chair's leaning. Build each round's packet with `python scripts/build_packet.py <run-dir> <out> --ids …` and spawn each role as its own subagent using the templates in `references/judge-prompts.md`. Before the final scoring run the chair records each idea's `status` (`killed`, `parked`, `winner`) in `ideas.json`, and re-checks the load-bearing claims in judge notes rather than trusting them; scores alone can crown the wrong idea. The model that pitched an idea is the worst judge of it. For finalists, the design strategist also draws the **journey and service blueprint** (first 60 seconds → first value → paying → retaining), which exposes hidden complexity and the single moment that must feel great.

### 8 · Red team, then chair
An independent **red team** (fresh context: pitch + evidence + brief only) writes the strongest case for why the leading idea fails in 12 months. The **chair** then picks one winner, or none, plus a **runner-up** to park, and records why the winner beat the runner-up. In exhaustive mode two chairs decide independently and any disagreement is reported. The chair also writes `assumptions.md`: every assumption the winner depends on, ranked by (impact if wrong × uncertainty), with the test that would resolve each.

### 9 · Memo and tests
Use `references/report-template.md`: `council-memo.md` is **answer-first** (recommendation, three supporting reasons, key risk, ask — readable in 90 seconds) and `report.md` is the full backing. Design the experiments per `references/experiments.md`: tests aim at the **riskiest assumption**, are pre-registered with kill criteria *before* anyone runs them, and climb a commitment ladder (reply → call → waitlist email → pre-payment). Do not write a build plan; recommend building only after a stranger has paid or credibly committed.

## Containment and transparency

- **Say what will run before running it.** In one message, before the first command, list the scripts you'll use, the public sites they contact, and the single folder you'll write to.
- **Write only inside `council-runs/<slug>/`** under the current working directory. Never create folders elsewhere, and never touch `~/.claude`, settings, permissions, shell profiles or other projects' files.
- **Read-only and standard-library only.** Scripts make read-only requests to public APIs; no installs, no `sudo`, no downloaded executables, no logins.
- **Stay inside the budget.** Don't collect or run more than the mode calls for; if you need more, say so and ask.
- **Never copy run outputs into the plugin or skill folder.** They contain quoted third-party text.

## Principles that keep the output honest

- **No invented evidence.** Quotes are verbatim and verified by script. If a source blocks you, say so; thin evidence is reported as thin.
- **Hypothesis-first, evidence-decided.** State the hypothesis early so you know what would change your mind; then let the evidence kill it without ceremony.
- **Money beats volume.** One complaint with a dollar figure outweighs ten without. Count independent voices, not posts — ten replies in one thread are one voice.
- **Triangulate.** A winner needs evidence from at least two source families (standard) or three (exhaustive); a single forum is a single bubble.
- **Ranges, not point estimates.** Sizing and revenue claims carry low/base/high and the assumptions behind them.
- **Let the skeptic win.** Cut below the target count rather than keep an idea with an unanswered kill.
- **Separate roles.** Collect ≠ tag ≠ pitch ≠ score ≠ attack ≠ decide.
- **Subtract.** The taste editor removes features until the idea fits in one sentence. An idea that needs a paragraph to explain usually has no wedge yet.
- **Respect sources and people.** Public, free, rate-limited, no logins. Record the complaint, not the person; never surface private details about individuals.
- **Name the biases.** Before the chair decides, scan `references/frameworks.md` → bias checklist and say which biases could be distorting this run.
- **Scale honestly.** The number of agents isn't the point — the separation of roles is. Say what you actually did and how many items you actually read.
