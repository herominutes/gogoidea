# Evidence guide (Gate track)

What to collect, how, and how much, at each depth. The aim is evidence a reviewer can point to, not a heap of data.

## Safety first
- **Read-only by default.** Reading and scanning files is fine. Building, running tests, installing dependencies, running the app, or contacting servers needs the user's explicit yes, one action at a time. Never run install scripts from a repo you haven't reviewed.
- **Only test what the user owns.** Don't probe third-party or production systems. For deeper security testing, tell the user what to run and read the output they paste.
- **Never print secrets.** Scripts mask them; if a reviewer finds one, cite the file and line and say "secret exposed", not the secret.
- **Production data stays out of the outputs.** Use fake or sample data for walkthroughs; if real data is unavoidable, don't copy it into the gate folder.

## What to gather
| Evidence | How | Used by |
|---|---|---|
| Sprint goal, acceptance criteria, strategy and top priorities | The user states them; ask once if missing | strategy, functionality |
| **Repo scan** | `python3 scripts/repo_scan.py <repo> --out gate-runs/<slug>/evidence` | security, privacy, auth, quality, release |
| Open issues | Export or paste from the tracker into `issues.md` | quality, strategy, all lenses |
| Test and CI results | Latest run summary; run tests only with approval and record the command and result | quality, functionality |
| Crash, error and performance data | Pasted crash-free rate, top crashes, slow screens | quality, release |
| Analytics and funnels | Pasted funnel steps and drop-offs; event list | journey, data |
| Tester or user feedback | Pasted comments | journey, ux, functionality |
| Journey walkthrough | A manual run following the template below | journey, auth, functionality, ux |
| Data golden examples | 5–10 inputs with independently computed expected outputs | data |
| Dependency audit (exhaustive) | The user runs the ecosystem's audit tool and pastes the output | security |
| Privacy inventory | A table of data collected, purpose, storage, recipients | privacy |
| Release checklist | Version, notes, config, rollback plan, monitoring | release |

## Minimum by depth
- **quick:** repo scan, issues skim, one core-journey walkthrough.
- **standard:** the above plus test results, the issue export, an auth-flow walkthrough, a privacy data inventory, five golden data examples, two journeys including edge cases.
- **exhaustive:** the above plus a dependency audit, crash and analytics review, an accessibility pass, a performance check, and an independent red-team pass.

## Journey walkthrough template (`journeys.md`)
Run each journey on a real device or simulator with sample data and record what actually happened.

| # | Step | Expected | Actual | Pass/Fail | Evidence (screenshot note, log, file) |
|---|---|---|---|---|---|
| 1 | Install and first launch | App opens to onboarding | | | |
| 2 | Sign up | Account created, verified | | | |
| 3 | First value | User completes the core action within N minutes | | | |
| 4 | Core loop (repeat) | Works twice in a row, state persists | | | |
| 5 | Payment (if any) | Purchase, restore and cancel all work | | | |
| 6 | Return after a day | State and session intact | | | |
| 7 | Sign out and back in | Data is still there | | | |
| 8 | Delete account | Data removed, user informed | | | |
Edge passes: offline, permission denied, interrupted, small screen, large text, dark mode.

## Data golden examples
For each of five to ten calculations or outputs the product shows (totals, balances, scores, dates, conversions), compute the expected answer **independently** (by hand or a separate script), run the product with the same input, and record both. Include awkward inputs: zero, negative, very large, rounding boundaries, other currencies or time zones, a daylight-saving change.

## Recording evidence for findings
A finding's evidence list can contain:
- `{"type": "file", "path": "Sources/Auth/TokenStore.swift", "line": 42, "snippet": "UserDefaults.standard.set(token"}` — **verifiable** by `verify_findings.py`.
- `{"type": "count", "path": "app/api/chat/route.ts", "pattern": "6-agent|Neurologist", "expected": 8, "ref": "HEAD"}` — **verifiable**: any claim of presence or absence ("8 matches", "no tests", "nothing found") belongs here, so the script re-counts it. Use `ref` to check a committed state (`HEAD`, `origin/main`) and omit it for the working tree.
- `{"type": "test", "ref": "UITests.testPurchase", "result": "failed", "note": "…"}`
- `{"type": "issue", "ref": "#123"}` or `{"type": "log", "note": "…"}`
- `{"type": "manual", "note": "Walked journey step 3 on iPhone 15 simulator; button unresponsive"}`
Non-file evidence is accepted but marked **unverified**; S1 and S2 findings should include at least one piece the chair can reproduce.
