# Founder brief template

The brief is the rubric every idea is judged against. Fill it from the conversation where possible; ask only for what's missing. Save as `brief.md`.

```markdown
# Founder brief

## Who I am
<role, background, unfair advantages: industries known, audiences reached, past products>

## What I can build
<stack, skills, what's easy vs. hard; e.g. "web SaaS with Stripe + auth in 2 weeks; no mobile; no ML training">

## How fast I ship
<hours/week, longest I'll wait for a first paying customer, solo or team>

## Money floor
<minimum outcome worth it; e.g. "$2k MRR in 6 months"; price range I'm comfortable charging>

## Constraints & disqualifiers
<no sales calls / no regulated industries / no marketplaces / heavy support / platform dependence / etc.>

## Distribution I already have
<audience, communities, newsletter, network — or "none">

## Taste
<what I'd be proud to ship; products whose craft I admire; what I refuse to build (dark patterns, clutter, etc.)>

## Energy
<problems I'd happily work on for two years; customers I enjoy; work I'd dread>

## Risk appetite
<safe small win vs. swing for a big one; how long I'd keep going before quitting>

## Weights (optional)
<which criteria matter most; default weights are in rubric.md. Example: "distribution and shippability matter double; I don't care about defensibility yet">

## Target space (optional)
<a competitor to attack, a niche, or "open">
```

## Notes for the interviewer

- Two or three specific details beat ten generic ones. "Ships a CRUD SaaS in 2 weeks, 10 hrs/week, no sales calls" lets the builder reject a hundred ideas instantly.
- **Distribution** is the most underrated field: an idea the founder can reach customers for beats a better idea they can't.
- **Taste and energy** are what stop the council from recommending a technically fine idea the founder will abandon in month three.
- If the user says "I don't know what I'm good at", infer from their projects and files in the conversation and show them the draft to correct.
- Turn weights into `weights.json` (criterion → number) if the user supplies them; otherwise use the defaults.
