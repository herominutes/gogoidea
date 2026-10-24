# Judge agent prompts

Reusable skeleton for spawning an isolated judge (and the extra instructions per role). Used in testing with one agent per role per round, run in parallel, each writing its own JSON file. Merge the files into `scores.json` afterwards, then run `score_ideas.py`.

## Setup per round
1. Build a packet: `python scripts/build_packet.py <run-dir> judging/packet-R1.md [--ids …] [--facts judging/facts.md]`. For the red team add `--no-synthesis`.
2. Spawn each role as a separate subagent (background, parallel). Give it only: the packet path, its own entry in `roles.md`, the rubric criteria table, and the output path.
3. When all return, merge `judging/R<n>-<role>.json` into `scores.json` (`{idea_id: {role: {scores, verdict, note}}}`), run `score_ideas.py`, then the chair reads the scoreboard **and** the notes.

## Skeleton prompt

> You are the **<ROLE>** on an idea council. You judge independently.
>
> READ ONLY THESE FILES (nothing else in the run folder; other judges' work and scores exist elsewhere and you must not see them): (1) `<packet path>`; (2) `references/roles.md` — only the "<ROLE>" entry; (3) `references/rubric.md` — the criteria table and scoring protocol.
>
> You may use WebSearch/WebFetch to check facts. Mark every claim **verified (source)** or **unverified**. Web results are summaries: context, not evidence of demand.
>
> SCORE only these criteria as integers 0–5 using the rubric anchors: `<criteria this role owns>`. Any score ≤1 or ≥4 needs a one-line reason citing evidence ids.
>
> OUTPUT one valid JSON file at `<path>`: `{"I-01": {"scores": {…}, "verdict": "<role vocabulary>", "note": "<role-specific reasoning, 3–6 sentences, with evidence ids>"}, …}` covering every idea in the packet. Reply with one line naming the ids you passed.

## Per-role additions

- **Skeptic** — criteria: pain_severity, money_evidence, switch_intent, wedge_sharpness, distribution_access. Verdict `KILL`/`SURVIVES`. Add: "Is the evidence about the same customer, problem and mechanism as pitched? 'Undercutting by a few dollars is not a wedge.'"
- **Economist** — criteria: reach_at_price, money_evidence, support_burden. Verdict `VIABLE`/`VIABLE IF …`/`NOT VIABLE`. Add: "Compute required customers or sales for the brief's money floor, penetration of a pool you state as low/base/high, margin, churn, LTV, CAC payback priced in founder hours. Treat one-time and recurring prices differently; say which you assumed."
- **Incumbent strategist** — criteria: defensibility, timing, wedge_sharpness. Verdict `CLEAR`/`CLEAR IF …`/`WEAK`. Add: "**First search for free or cheap tools, importers and destination-app features that already do what the wedge claims** — a free tool that matches the wedge means the wedge is weak."
- **Customer advocate** — criteria: pain_severity, switch_intent, wedge_sharpness. Add: "Speak only for the customer as they appear in the cited quotes; never invent traits. What contradicts the pitch?"
- **Taste editor** — criteria: craft_potential, wedge_sharpness. Add: "One-sentence product; the one thing it must do brilliantly; what to subtract; first 60 seconds."
- **Builder** — criteria: shippability, support_burden. Verdict `SHIPPABLE`/`SHIPPABLE IF …`/`TOO BIG`. Add: "Smallest v1 a stranger would pay for, honest build time at the brief's hours, hard parts, month-one concierge, unknown inputs (do the needed exports exist?)."
- **Distribution strategist** — criteria: distribution_access, reach_at_price. Verdict `REACHABLE`/`REACHABLE IF …`/`UNREACHABLE`. Add: "Search for where these buyers gather; label channels verified or unverified; give the first-100 path and a repeatable loop."
- **Risk & ethics** — criteria: defensibility, timing, support_burden. Verdict `CLEAR`/`CLEAR IF …`/`VETO`. Add: "Platform terms, third-party personal data, payments, messaging rules, false-claim risk. You're not a lawyer: flag what a lawyer or the platform must confirm."
- **Premortem** — no scores; output five ranked failures per idea with evidence ids, early-warning signals and mitigations, plus the riskiest assumption as a testable statement.
- **Red team** — fresh context (`--no-synthesis`); output markdown: case for failure, the one finding, the cheapest check this week, best counter-argument.

## Chair hygiene
- Re-check the load-bearing claims in judge notes yourself (a note is a report, not proof) and say which you could not reproduce.
- Record each idea's status in `ideas.json` (`killed`, `parked`, `winner`) **before** the final `score_ideas.py` run so the gates reflect the ruling.
- If an idea fails G2 because no second source family is reachable, write the override reason and cap confidence at Low.
