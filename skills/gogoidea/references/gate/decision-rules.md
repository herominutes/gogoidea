# Decision rules

These are the defaults built into `scripts/gate_score.py`. The chair may argue with the recommendation, but must write down why and can never override a blocker without the owned risk acceptance described below.

Contents: [Severity](#severity) · [Hard blockers](#hard-blockers) · [Scoring profiles](#scoring-profiles) · [Thresholds](#thresholds) · [Decisions](#decisions) · [Conditions](#conditions) · [Risk acceptance](#risk-acceptance) · [Priority formula](#priority-formula) · [Re-gating](#re-gating)

## Severity
| Level | Meaning | Examples |
|---|---|---|
| **S1 Critical** | Harm to users or the business; no safe way to ship | exposed secret, auth bypass, data loss, crash in a core flow, privacy violation, wrong money figures |
| **S2 High** | A core feature or journey step is badly broken or risky, with no good workaround | purchase restore fails, onboarding dead end on one device class |
| **S3 Medium** | Noticeable problem, with a workaround or limited reach | misaligned layout, slow screen, unclear error copy |
| **S4 Low** | Polish | typo, minor spacing |

## Hard blockers
Any **open S1** is a blocker. A finding may also be flagged `blocker: true` by a reviewer (for example, a lens-specific blocker from `lenses.md` that is S2 in a regulated profile). While any blocker is open, the recommendation is **NO-GO** whatever the scores say.

## Scoring profiles
Weights per lens. Pick the profile that matches the product; the chair may supply a custom weights file.

| Lens | consumer-app (default) | saas | regulated | internal | prototype |
|---|---|---|---|---|---|
| strategy | 3 | 2 | 1 | 3 | 4 |
| security | 3 | 3 | 4 | 2 | 1 |
| privacy | 3 | 3 | 4 | 1 | 1 |
| auth | 2 | 3 | 3 | 2 | 1 |
| functionality | 3 | 3 | 3 | 3 | 3 |
| quality | 2 | 2 | 2 | 3 | 1 |
| journey | 2 | 2 | 1 | 1 | 3 |
| ux | 2 | 1 | 1 | 1 | 2 |
| data | 3 | 3 | 4 | 3 | 2 |
| release | 1 | 2 | 2 | 1 | 1 |

*regulated* means regulated-adjacent products such as finance or health. Even in *prototype*, security and privacy blockers still stop a release that touches real user data.

**Critical lenses:** security, privacy, auth, data. They have higher minimums below.

## Thresholds
Weighted score = Σ(weight × median lens score) ÷ (5 × Σ weight) × 100.

| Recommendation | Requires |
|---|---|
| **GO** | no blockers; open S2 = 0; score ≥ **80**; every lens ≥ 3 (critical lenses ≥ 3, never thin evidence) |
| **GO WITH CONDITIONS** | no blockers; score ≥ **65**; open S2 ≤ **3**, each with an owner and a mitigation; every lens ≥ 2; critical lenses ≥ 3 |
| **NO-GO** | anything else: a blocker, a lens below 2, a critical lens below 3, too many open S2, or a score under 65 |
| **INCOMPLETE** | one or more lenses has no score yet; finish the review first |

**Strategy flag:** if the strategy lens scores below 2, the scorer adds "consider ARCHIVE WITHOUT SHIP": the build may not serve the current direction even if it's technically sound.

Thresholds can be changed with `--go-score`, `--cond-score`, `--max-s2` when the team has a reason; write the reason in the decision record.

## Decisions
- **GO** — close the sprint; archive the build as the release (tag, freeze, artifacts, notes).
- **GO WITH CONDITIONS** — close the sprint and archive the candidate; ship only after every condition is met and verified.
- **NO-GO** — do **not** close or archive; keep the sprint open or extend. Blockers and the re-gate plan are listed.
- **ARCHIVE WITHOUT SHIP** — a strategic decision: the build no longer serves the product direction. Archive it for reference, carry over only what still matters, and say what replaces it.
- **INCOMPLETE** — not a decision; it names the missing lenses.

## Conditions
A condition is a concrete, checkable requirement before shipping (for example "feature flag X stays off until the migration is verified on a copy of production data"). Each has an **owner**, a **due date** and a **verification** step. A condition that can't be verified isn't a condition; it's a hope. If there are more than three, the build probably isn't ready.

## Risk acceptance
Some open issues will ship anyway. Accepting a risk is a written decision, not a shrug:
- It names an **owner** (a person) and an **expiry date** (when it must be fixed or re-accepted).
- It states the **impact if it goes wrong** and what **detects** it.
- **S1 findings can't be accepted.** They must be fixed. If the team believes a finding is wrongly rated S1, re-rate it with evidence, don't accept it.
- Accepted S2 findings count toward the S2 limit for GO WITH CONDITIONS.
- Don't accept security, privacy or data-loss risks to hit a date.
`gate_score.py` flags any accepted finding without an owner and an expiry as **invalid**, and treats it as still open.

## Priority formula
For open findings: **priority = severity points × strategic multiplier × exposure multiplier**.
- Severity points: S1 = 100, S2 = 40, S3 = 10, S4 = 2.
- Strategic impact: core promise = ×3, supporting = ×2, peripheral = ×1.
- Exposure: all or most users = ×3, a segment = ×2, few or edge cases = ×1.
Sorting by priority gives the carry-over order; buckets are then **Fix before ship** (blockers and core S2), **Carry over**, **Accept risk**, **Won't fix**.

## Re-gating
After a NO-GO, fix the blockers, then re-review only the lenses with open blockers or changed code, re-run `verify_findings.py` and `gate_score.py`, and issue a new decision record that references the previous one. Don't average old and new scores.
