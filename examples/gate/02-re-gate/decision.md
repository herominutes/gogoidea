# Decision — Pocket Pantry v1.4.1 · re-gate · 2026-11-03

> **Example.** Pocket Pantry and the people in it are fictional. The scorer output next to this file is real tool output on made-up data; this record is written by hand from it.

## Decision
**GO WITH CONDITIONS** — close the sprint and archive v1.4.1 as the release candidate, but do not ship until account deletion (F-003) is built and verified. The critical issue and the cleartext API are fixed.

## Why
1. **The blocker is gone, and the fix was checked by script, not by trust.** F-001 was re-verified with `count` evidence: `UserDefaults` appears on 0 lines of `SessionStore.swift` and no line prints a token. F-002 likewise: `http://` appears on 0 lines of `API.swift`. `verify_findings.py` re-ran both counts against the repo and they passed.
2. **The score rose from 68.3 to 73.3.** Only the security lens was re-reviewed (2 → 4), as the re-gate rules say; the other lenses carry over from the first gate. Re-gating does not average old and new scores.
3. **One high-severity item remains, with an owner and a date.** F-003 (no account deletion) keeps this below GO (which needs no open S2 and a score of 80 or more), so it stays a condition.

## Blockers and conditions
| # | Item | Severity | Owner | Due | How we verify |
|---|------|----------|-------|-----|---------------|
| F-003 | In-app account deletion | S2 | Sam | 2026-11-09 | Walkthrough on a device: Settings → Delete account removes the account and signs out; re-sign-in with the same email fails |

## Top carry-over (in priority order)
F-004 no tests or CI, F-008 empty first-launch screen, F-005 privacy manifest, F-006 test key in source, F-009 unplanned animation work, F-007 force-try. See `decision-input.md`.

## Accepted risks
None.

## What was not covered
Same as the first gate: no penetration test, dependency audit, real-device matrix, accessibility pass or legal review.

## Archive (offered, not run)
On GO or GO WITH CONDITIONS the Gate writes an archive checklist and **offers** the commands, for example `git tag -a v1.4.1 -m "release candidate"`. It runs them only if you say yes.
