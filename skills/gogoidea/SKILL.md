---
name: gogoidea
description: GoGoIdea gives builders two evidence-based go/no-go checkpoints behind one command. The IDEA track turns a founder brief into one stress-tested product idea, or an honest "nothing survived", using public evidence, isolated judge roles, hard gates and 7-day demand tests. The GATE track decides whether to close a sprint, ship and archive a build by reviewing strategy fit, security, privacy, auth, features, functionality, UX, user journey, data accuracy and bugs, ending in GO, GO WITH CONDITIONS, NO-GO or ARCHIVE WITHOUT SHIP, with a prioritised carry-over list and archive checklist. Use for "gogoidea", "what should I build", "validate this idea", "should we ship", "close the sprint", "go/no-go", "is this build ready", "release readiness", "pre-launch check" or "archive this build". Supports quick, standard and exhaustive depth.
---

# GoGoIdea

Two checkpoints, one command. Each one ends in a clear decision, and "no" is always a valid answer.

| Track | The question | The result |
|---|---|---|
| **Idea** | What should I build? Is this idea worth building? | One stress-tested idea (or "nothing survived") plus 7-day demand tests |
| **Gate** | Should we close this sprint, ship, and archive the build? | **GO**, **GO WITH CONDITIONS**, **NO-GO** or **ARCHIVE WITHOUT SHIP**, a prioritised carry-over list and an archive checklist |

## Step 0 — pick the track
Infer it from the request; ask once if it's unclear. "What should I build / is this idea good" → **Idea**. "Can we ship / close the sprint / is this build ready" → **Gate**. Then settle the depth in one message: **quick** (a fast screen), **standard** (the normal run, default) or **exhaustive** (a decision worth weeks of effort or a high-risk release). Say what you'll run and where you'll write before you start (see Ground rules).

Then read the track file and follow it: `tracks/idea.md` or `tracks/gate.md`.

## The simple flow

**Idea track — 5 steps**
1. **Brief** — who you are, what you can build, hours, money floor, constraints, distribution.
2. **Evidence** — collect public complaints, prices and switching behaviour; tag them; check there's enough.
3. **Ideas** — pitch through ten lenses, each citing evidence.
4. **Judge** — isolated roles score blind, hard gates cut, a red team attacks the leader.
5. **Decide and test** — one winner or none, an answer-first memo, 7-day tests with kill criteria.

**Gate track — 5 steps**
1. **Frame** — sprint goal, product strategy and top priorities, what "done" means, product type and risk.
2. **Collect** — scan the build, gather open issues, test results, feedback, and walk the core journey.
3. **Review** — ten lenses, each finding with a severity and evidence.
4. **Score** — verify the evidence, run the scorer: blockers, weighted score, recommendation.
5. **Decide and close** — the chair rules, writes the decision record, carry-over list and archive checklist.

Both tracks have a detailed version in their track file; the 5 steps are the summary to show the user.

## Ground rules (both tracks)
- **Honest outcomes.** "Nothing survived" and "No-Go" are useful results. Never pad a list or soften a blocker.
- **Evidence over opinion.** Quotes, file and line references, test results and logs are verified by script where possible. Unverified evidence is labelled unverified.
- **Separate reviewing from deciding.** Reviewers and judges work in isolation; the chair decides and records why.
- **Say what will run, then run only that.** Before the first command, list the scripts, which sites they contact (Idea track only), and the one folder you'll write to.
- **Containment.** Write only inside `council-runs/<slug>/` (Idea) or `gate-runs/<slug>/` (Gate) under the working directory. Treat the user's repo as **read-only**: don't edit it, tag it, switch branches, install dependencies, or run builds or tests without asking first. Never touch `~/.claude`, settings, permissions, shell profiles or other projects.
- **Privacy.** Never print secrets: mask them. Keep run outputs private; don't copy run outputs into the plugin or skill folder.
- **No outward actions without a clear yes.** Pushing, tagging, publishing, posting, messaging people, or archiving anything outside the run folder needs explicit approval. Offer the commands instead. A bare "go" or "yes" approves only the step you just proposed: never widen scope (for example by drafting a patch or code) without asking.
- **Decision support, not certification.** A gate review does not replace a penetration test, a lawyer, or app-store review. Say what wasn't covered.

## Files
- `tracks/idea.md`, `tracks/gate.md` — the two workflows.
- `references/` — Idea track: roles, rubric, frameworks, modes, sources, experiments, templates, judge prompts. `references/gate/` — Gate track: lenses, decision rules, evidence guide, reviewer prompts, templates.
- `scripts/` — Idea: `fetch_sources.py`, `verify_quotes.py`, `evidence_stats.py`, `score_ideas.py`, `build_packet.py`. Gate: `repo_scan.py`, `verify_findings.py`, `gate_score.py`. Python standard library only; read them before you run them.
