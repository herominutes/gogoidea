# Gate track — close the sprint? Ship and archive the build?

The Gate answers one question: **is this build ready to close out, ship and archive — and if not, exactly what stands in the way?** It reviews the build against the product's own strategy and priorities, and across ten lenses: strategy fit, security, privacy, auth, functionality, quality, journey, UX, data accuracy and release readiness. The result is a decision, a prioritised list of what to fix or carry over, and an archive checklist.

## Principles
1. **No-Go is a valid, useful result.** A clear No-Go with a short blocker list saves a bad release.
2. **Blockers beat scores.** A high average can't outvote an exposed secret, a broken core journey, or data loss.
3. **Evidence over opinion.** Every finding cites a file and line, a test result, a log, an issue, or a manual check you actually performed.
4. **Unknown is a risk.** A lens with no evidence can't score above 2, and a gate with an unreviewed lens is **INCOMPLETE**, never GO.
5. **Strategy first.** A flawless build of the wrong thing is still not a ship: it may be **ARCHIVE WITHOUT SHIP**.
6. **Reviewers review; the chair decides.** Keep them separate, and let the chair re-check the load-bearing claims.
7. **Read-only on the build.** Never modify the repo, tags or branches; offer commands instead.

## Depth
| | quick | standard | exhaustive |
|---|---|---|---|
| Time | ~45 min | a few hours | a day+ |
| Evidence | repo scan, issue skim, one core-journey walkthrough | + test results, issue export, data-inventory and auth walkthroughs, two journeys with edge cases | + dependency audit run by the user, crash/analytics review, accessibility pass, performance check |
| Reviewers | one pass over all lenses (you plus a skeptic pass) | one isolated reviewer per lens | per lens + red team ("why did we regret shipping this?") + second chair |
| Use when | small change, low risk | a normal sprint close | public launch, payments, sensitive data, or a risky migration |

## Run folder
`gate-runs/<slug>/` under the working directory:

```
gate-brief.md  evidence/repo-scan.json  evidence/repo-scan.md  issues.md  journeys.md
findings.json  scores.json  decision-input.md  decision-input.json
decision.md  carryover.md  risk-register.md  archive-checklist.md  state.json
```
Keep `state.json` (`{"mode","stage","completed":[…]}`) updated so a run can resume.

## Steps

### 0 · Frame (`gate-brief.md`)
Use the template in `references/gate/templates.md`. Capture: the **sprint goal** and acceptance criteria; the **product strategy and top 3 priorities** (the core promise to users); product type (consumer app, B2B SaaS, regulated-adjacent such as finance or health, internal tool, prototype) which picks the scoring profile; platform and stack; users and data sensitivity; the intended release (TestFlight, App Store, production deploy, internal); hard dates; and who owns the decision. Draft from what you already know and confirm in one message. If the user can't state the strategy and priorities, say that is itself the first finding.

### 1 · Collect evidence
Read `references/gate/evidence-guide.md` for what to gather at each depth.
- **Scan the build (read-only):** `python3 scripts/repo_scan.py <repo> --out gate-runs/<slug>/evidence`. It finds leads (secrets, cleartext URLs, tokens in local storage, auth and privacy signals, TODO debt, tests, git state). These are **signals, not findings** — reviewers confirm them.
- **Open issues:** ask for an export or paste (CSV, markdown, a list). Save as `issues.md`.
- **Tests, crashes, feedback:** ask for the latest results, crash or error summaries, analytics funnels, tester feedback. Don't run builds or tests unless the user says yes; record any you run with the command and outcome.
- **Walk the core journey** (`journeys.md`): first run → first value → core loop → payment if any → return → delete account. Note each step's expected and actual result.

### 2 · Review through the ten lenses
Read `references/gate/lenses.md`. In **standard** and **exhaustive**, spawn one isolated reviewer subagent per lens using `references/gate/reviewer-prompts.md`; each sees the gate brief, the evidence and its own lens only, never other reviewers' findings or scores. In **quick**, do one pass yourself, writing each lens's findings before starting the next. Each reviewer writes findings (severity S1–S4, lens, evidence, strategic impact, recommendation) and a 0–5 score per lens with a reason.

### 3 · Verify and score
- `python3 scripts/verify_findings.py gate-runs/<slug> --repo <repo>` checks that every cited file and line exists and the snippet matches. Fix or drop findings that fail. Findings that cite only issues, logs or manual checks are marked **unverified**; S1 and S2 findings should have at least one verifiable or reproducible piece of evidence.
- `python3 scripts/gate_score.py gate-runs/<slug> --profile <profile> --mode <mode>` computes lens scores (median across reviewers), the weighted score, open blockers, the recommendation with reasons, and the priority list. It writes `decision-input.md`.

### 4 · Prioritise (the core-issue review)
Re-rank every open finding by **severity × strategic impact × exposure** (the scorer does this; confirm the order makes sense). Sort each into one bucket: **Fix before ship** (blockers and core-priority S2), **Carry over** (next sprint, in order), **Accept risk** (written, with an owner and an expiry), **Won't fix** (with a reason). Check that every top-3 product priority has a verified test or walkthrough, and that nothing in security, privacy, auth or data is silently deferred. Write `carryover.md` and `risk-register.md`.

### 5 · Decide (`decision.md`)
The chair reads `decision-input.md`, re-checks the load-bearing findings (a note is a report, not proof), says which biases could be skewing the review (optimism near a deadline, sunk cost, reviewer overlap with the builder), and rules. Run every "how we verify" check against the **current** state first, so it can't fail or pass for the wrong reason (for example a grep that also matches legitimate text); record counts as `count` evidence so `verify_findings.py` can re-run them:
- **GO** — close the sprint; archive the build as the release.
- **GO WITH CONDITIONS** — close the sprint and archive, but only ship once the listed conditions are met; each has an owner, a due date and a way to verify it.
- **NO-GO** — don't close or archive; keep the sprint open or extend it. List the blockers and the re-gate plan.
- **ARCHIVE WITHOUT SHIP** — the build no longer serves the strategy; archive it for reference and carry over only what still matters.
- **INCOMPLETE** — lenses are unreviewed; say which, and finish them first.
Rules for overriding the scorer are in `references/gate/decision-rules.md`; blockers can't be overridden without a written, owned risk acceptance, and S1 findings can't be accepted at all.

### 6 · Close and archive (only on GO, GO WITH CONDITIONS, ARCHIVE WITHOUT SHIP)
Write `archive-checklist.md` from the template: tag and freeze the release branch, store build artifacts with checksums, release notes and a known-issues list, move carry-over items into the next sprint's backlog in priority order, record the decision and risk register, a short retro, and the rollback plan. **Offer the commands** (for example `git tag`, branch protection); run them only if the user says yes.

After a **NO-GO**, re-gate: fix the blockers, then re-review only the lenses with open blockers or changed code and re-run steps 3–5.

## What the Gate does not do
It doesn't fix bugs, change the repo, deploy, tag, or submit anything, and it **doesn't write patches or code for fixes**. The recommendation in each finding is the deliverable. When the decision record is done you may *offer* to draft a fix as a separate follow-up, and do it only if the user explicitly asks for that specific thing (for example "draft a patch for F-001"). A bare "go" or "yes" approves only the step you just proposed. It isn't a penetration test, a legal review, or app-store approval, and it only sees the evidence it's given — say what wasn't covered in the decision record.
