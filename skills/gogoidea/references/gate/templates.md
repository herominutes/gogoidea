# Gate templates and schemas

Contents: [Gate brief](#gate-brief) · [findings.json](#findingsjson) · [scores.json](#scoresjson) · [Decision record](#decision-record) · [Carry-over list](#carry-over-list) · [Risk register](#risk-register) · [Archive checklist](#archive-checklist)

## Gate brief
Save as `gate-brief.md`.

```markdown
# Gate brief — <product> · <sprint name or number>

## Sprint goal and "done"
<the goal in one or two sentences; the acceptance criteria that define done>

## Strategy and top priorities
<the product's core promise to users; the top 3 priorities in order; what is deliberately out of scope>

## Build
<product type: consumer-app | saas | regulated | internal | prototype>; <platform and stack>; <repo path>; <branch/commit/tag under review>

## Users and data
<who uses it; what personal or sensitive data it handles>

## Intended release and constraints
<TestFlight / store / production / internal>; <hard dates>; <risk appetite>

## Decision owner
<who decides, and who can accept risk>

## Depth
<quick | standard | exhaustive>
```

## findings.json
A list. Reviewers write per-lens files that are merged here with sequential ids.

```json
[
  {
    "id": "F-001",
    "lens": "security",
    "severity": "S1",
    "title": "Auth token stored in UserDefaults",
    "evidence": [
      {"type": "file", "path": "Sources/Auth/TokenStore.swift", "line": 42, "snippet": "UserDefaults.standard.set(token"}
    ],
    "strategic_impact": "core",
    "exposure": "all",
    "status": "open",
    "owner": null,
    "due": null,
    "blocker": true,
    "recommendation": "Move the token to the Keychain.",
    "reviewer": "security"
  }
]
```
- `severity`: `S1 | S2 | S3 | S4`. `strategic_impact`: `core | supporting | peripheral`. `exposure`: `all | segment | few`.
- `status`: `open | fixed | accepted | wont_fix`. `accepted` requires `owner` and `due` (expiry); S1 can't be accepted.
- `blocker`: true for lens-listed blockers; every open S1 is a blocker regardless.
- Evidence types: `file` (path, line, snippet; **verifiable**), `count` (path, regex `pattern`, integer `expected`, optional `ref` such as `HEAD`, optional `flags: "i"`; **verifiable**: the script re-counts matching lines), `test`, `issue`, `log`, `manual` (unverified but allowed).

## scores.json
`{lens: {reviewer: {score, note}}}`. Lenses: `strategy, security, privacy, auth, functionality, quality, journey, ux, data, release`.

```json
{
  "security": {"security-reviewer": {"score": 2, "note": "Token storage and one open RLS gap; auth logic otherwise sound."}},
  "privacy":  {"privacy-reviewer":  {"score": 3, "note": "Inventory complete; policy matches SDKs."}}
}
```
More than one entry per lens is fine (for example the skeptic); the scorer uses the median.

## Decision record
Save as `decision.md`. Answer first.

```markdown
# Decision — <product> · <sprint> · <date>

## Decision
**<GO | GO WITH CONDITIONS | NO-GO | ARCHIVE WITHOUT SHIP | INCOMPLETE>** — <one sentence on what happens now: close and archive / keep the sprint open / archive for reference>

## Why
1. <strongest reason, with finding ids>
2. <second reason>
3. <third reason>

## Blockers and conditions
| # | Item | Severity | Owner | Due | How we verify |
|---|------|----------|-------|-----|---------------|

## Scores (profile: <profile>, mode: <mode>)
| Lens | Score | Weight | Notes |
|---|---|---|---|
Weighted score: <n>/100 · open S1: <n> · open S2: <n> · lenses reviewed: <n>/10 · unverified S1/S2 evidence: <n>

## Top carry-over (in priority order)
1. …

## Accepted risks
<id — owner — expires — impact if wrong — how detected> (or "none")

## What was not covered
<e.g. no penetration test, no real-device matrix, no legal review, no load test>

## Biases considered
<deadline optimism, sunk cost, builder-reviewer overlap, anchoring — and what was done about them>

## Re-gate
<for NO-GO / conditions: what changes, which lenses get re-reviewed, by when>
```

## Carry-over list
Save as `carryover.md`: open findings in priority order, grouped into buckets.

```markdown
# Carry-over — <sprint>

## Fix before ship
| Priority | Finding | Severity | Lens | Owner |
## Carry over to next sprint (in order)
| Priority | Finding | Severity | Lens | Suggested sprint |
## Accepted risk
| Finding | Owner | Expires | Impact if wrong |
## Won't fix
| Finding | Reason |
```

## Risk register
Save as `risk-register.md`. One row per accepted risk; a risk with no owner or expiry is not accepted.

| Finding | Why we accept it | Impact if it goes wrong | Detected by | Owner | Expires |
|---|---|---|---|---|---|

## Archive checklist
Save as `archive-checklist.md` on GO, GO WITH CONDITIONS or ARCHIVE WITHOUT SHIP. **Offer** the commands; run them only with an explicit yes.

- [ ] Release branch frozen and protected; final commit identified
- [ ] Tag created (for example `git tag -a vX.Y.Z -m "<sprint> release"`) and pushed
- [ ] Build artifacts stored with checksums (and signing details recorded)
- [ ] Release notes and **known-issues list** written
- [ ] Carry-over items moved into the next sprint's backlog in priority order
- [ ] Decision record, risk register and findings stored with the release
- [ ] Rollback plan and monitoring owners recorded
- [ ] Docs and changelog updated; support informed
- [ ] Short retrospective note: what the gate caught, what it missed
- [ ] Conditions (if any) tracked with owners and dates before shipping
