# Decision — Pocket Pantry v1.4.0 candidate · first gate · 2026-10-30

> **Example.** Pocket Pantry and the people in it are fictional. The scanner, verifier and scorer output next to this file is real tool output on made-up data; this record is written by hand from it, following `references/gate/templates.md`.

## Decision
**NO-GO** — keep the sprint open. One critical issue (F-001) must be fixed first, and two high-severity items (F-002, F-003) are due before ship. This is a fix of about a day, not a rethink.

## Why
1. **A session token is stored in clear text and written to the log (F-001, S1).** `SessionStore.swift:7` saves it in `UserDefaults`, and line 8 prints it. Anyone with access to the device backup or the logs can reuse the session. This is an open S1, so it is a hard blocker.
2. **The score would not have saved it.** The weighted score is 68.3/100, above the 65 line for GO WITH CONDITIONS, and the other lenses are healthy. Blockers beat scores: an open S1 means NO-GO however good the average looks, and the security lens is below the critical-lens minimum of 3 anyway.
3. **Two more must-fix items before shipping.** The API base URL is cleartext HTTP (F-002), and users cannot delete their account (F-003), which the major app stores require wherever accounts can be created.

## Blockers and conditions
| # | Item | Severity | Owner | Due | How we verify |
|---|------|----------|-------|-----|---------------|
| F-001 | Move the token to the Keychain; remove the log line | S1 | (unassigned: blocker) | before re-gate | Count of `UserDefaults` mentions in `SessionStore.swift` is 0; no log line prints a token |
| F-002 | Serve the API over HTTPS | S2 | Sam | 2026-11-02 | Count of `http://` in `API.swift` is 0; the app loads lists on a device |
| F-003 | In-app account deletion | S2 | Sam | 2026-11-09 | Walkthrough: Settings → Delete account removes the account and signs out |

## Scores (profile: consumer-app, mode: standard)
See `decision-input.md` for the table. Weighted score 68.3/100 · open S1: 1 · open S2: 2 · lenses reviewed: 10/10.

## Top carry-over (in priority order)
No tests or CI (F-004), an empty first-launch screen (F-008), a missing privacy manifest (F-005), a test payment key in source (F-006), unplanned animation work (F-009), a force-try (F-007). See `decision-input.md`.

## Accepted risks
None. S1 findings cannot be accepted.

## What was not covered
No penetration test, no dependency audit, no real-device matrix, no accessibility pass, no legal or privacy review. Findings come from the repo scan, reading code and one simulator walkthrough.

## Biases considered
A single reviewer scored every lens in this example, so the scores are not independent; the standard-mode design uses one isolated reviewer per lens. Deadline pressure to ship v1.4.0 could favour "ship with a note", which is exactly why the blocker rule is mechanical.

## Re-gate
After F-001 and F-002 are fixed: re-review security, re-run `verify_findings.py` and `gate_score.py`, and issue a new record. See `../02-re-gate/`.
