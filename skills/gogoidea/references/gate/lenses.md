# The ten review lenses

Each lens is reviewed by one role. For every lens: what to check, where evidence comes from, what counts as a blocker (an automatic S1), and how to score. Findings are rated by severity (see `decision-rules.md`); scores are 0–5.

Contents: [Scoring anchors](#scoring-anchors) · [1 strategy](#1-strategy) · [2 security](#2-security) · [3 privacy](#3-privacy) · [4 auth](#4-auth) · [5 functionality](#5-functionality) · [6 quality](#6-quality) · [7 journey](#7-journey) · [8 ux](#8-ux) · [9 data](#9-data) · [10 release](#10-release)

## Scoring anchors
| Score | Meaning |
|---|---|
| 0 | Not reviewed, or no evidence at all. Counts as a gap, never as a pass |
| 1 | Serious unresolved problems; would hurt users or the business |
| 2 | Significant gaps; or reviewed with thin evidence (the cap when evidence is thin) |
| 3 | Acceptable: known minor gaps, none threatening the core promise |
| 4 | Solid: checked with evidence, only small polish items open |
| 5 | Exemplary: verified end to end, tested, nothing material open |

A lens can score at most **2** when its evidence is thin, however good it looks. Say why.

## 1 strategy
**Question:** Does this build deliver the sprint goal and advance the product's top priorities — and is anything in it off-strategy?
**Check:** planned vs delivered against the sprint goal and acceptance criteria; whether each top-3 priority moved; scope creep and unplanned work; features built for a deprecated bet; open issues ranked against the core promise; dependencies on unfinished work; opportunity cost of shipping vs holding.
**Evidence:** sprint plan, issue list, release notes, the product strategy doc, a walkthrough of the core promise.
**Blockers:** the core promise isn't delivered; the build serves a strategy the team has dropped (consider **ARCHIVE WITHOUT SHIP**).

## 2 security
**Check:** secrets in the repo, history or config; where tokens are stored (Keychain vs UserDefaults/localStorage); transport (HTTPS, App Transport Security, certificate validation); authorization enforced **server-side** (row-level security, API guards) not just in the client; input validation and injection (SQL, XSS, deep links, URL schemes, file uploads); webhook signature checks (payments); rate limiting; sensitive data in logs; debug backdoors and test keys; least-privilege permissions and API scopes; dependency vulnerabilities.
**Evidence:** `repo_scan.py` signals, code review of auth and data-access paths, dependency audit output (run by the user), config files, backend policies.
**Blockers:** an exposed secret or service-role key; an authorization bypass or IDOR; user data readable without a policy; exploitable injection; sensitive data sent or stored in clear text.

## 3 privacy
**Check:** a data inventory (what is collected, why, where it's stored, who receives it including third-party SDKs); data minimisation; consent and tracking permission; accuracy of the privacy policy and store privacy labels or manifests; retention and deletion; export; analytics and crash reports free of personal data; permission prompts with honest usage strings; children's data and regional rules flagged for a lawyer.
**Evidence:** SDK list, permission strings, privacy manifest, network calls, policy text, backend tables.
**Blockers:** undisclosed collection of sensitive data; tracking without required consent; a required disclosure or deletion path missing; personal data sent to a third party that isn't declared. *(This is a review aid, not legal advice.)*

## 4 auth
**Check:** sign-up, sign-in, sign-out, password reset, email verification, session expiry and refresh, token revocation, multi-device behaviour, account deletion (required in-app on major app stores when accounts can be created), required social-login rules, lockout and rate limiting, MFA where it fits, role and permission checks, deep-link auth, the logged-out state, and auth error handling.
**Evidence:** `repo_scan.py` auth checklist, a manual walkthrough of every auth flow, backend auth config.
**Blockers:** users can't sign in or out; an auth bypass or account-takeover path; no account deletion where one is required; a session that never expires in a sensitive app.

## 5 functionality
**Check:** features against acceptance criteria; the core flows end to end; edge cases (empty, very large, offline, interrupted, permission denied, background and foreground, different devices); purchases and subscriptions (buy, restore, refund, receipt validation); notifications; integrations; error handling; feature-flag state; regression on earlier features.
**Evidence:** test results, a feature checklist walked by hand, bug reports, screen recordings.
**Blockers:** a core feature broken with no workaround; a failing purchase flow; data lost on a common action.

## 6 quality
**Check:** open bugs triaged by severity; crash-free rate and error logs; failing or flaky tests; coverage on critical paths; performance (cold start, memory, battery, API latency); build warnings and lint; TODO/FIXME debt in critical paths; CI status; whether the build is reproducible; the known-issues list.
**Evidence:** CI output, crash reports, test runs, `repo_scan.py` counts, the bug list.
**Blockers:** a crash at launch or in a core flow; failing tests on critical paths; any open S1.

## 7 journey
**Check:** install → first run and onboarding → first value (time-to-value) → core loop → paywall or monetisation → return and retention hooks → settings → exit and delete. Dead ends, unnecessary friction, permission prompts at the wrong moment, empty states that guide, error recovery, funnel drop-offs, and clarity of copy at each step.
**Evidence:** the journey walkthrough, funnel analytics, tester feedback, recordings.
**Blockers:** a user cannot reach first value; a dead end in onboarding or purchase; misleading or dark-pattern monetisation.

## 8 ux
**Check:** consistency with the design system and platform conventions; layout across supported device sizes and orientations; text scaling; dark mode; accessibility (screen-reader labels, contrast, touch-target size, motion); loading, empty, error and success states; copy tone; localisation; overall polish and focus.
**Evidence:** screenshots across sizes, an accessibility pass, a design checklist, comparison to the design file.
**Blockers:** the core flow is unusable on a supported device size; a core flow is inaccessible where accessibility is a stated requirement; broken layout in a core screen.

## 9 data
**Check:** that numbers shown to users are right (units, rounding, currency, time zones, daylight saving); sync and conflict handling; migrations (forward, backward, rollback); validation; a single source of truth; duplicate prevention; analytics events firing once with the right names; import and export fidelity; cache staleness; test or seed data leaking into production; backups.
**Evidence:** "golden examples" (inputs with independently computed outputs), migration scripts, database checks, analytics event logs.
**Blockers:** wrong numbers in a core output (especially money or health); data loss or corruption; a risky migration with no rollback.

## 10 release
**Check:** versioning and build numbers; release notes; store or deployment compliance checklist; feature flags and a kill switch; a rollback plan; monitoring and alerting; support readiness (help, contact); docs and changelog; production configuration (no test keys, staging URLs or debug flags); signed, reproducible build; legal pages; and **archive readiness** (tag, artifacts, handoff notes).
**Evidence:** build settings, release notes, config files, the release checklist.
**Blockers:** no way to roll back a risky release; production configured with test keys or staging endpoints; the build can't be signed or reproduced.
