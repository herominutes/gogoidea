# Gate decision input

Profile **consumer-app** · mode **standard** · weighted score **68.3/100**

## Recommendation: **NO-GO**

- 1 open blocker(s): F-001

_The chair may argue with this, but cannot override an open blocker without an owned, dated risk acceptance; S1 findings can't be accepted._

## Lens scores (median across reviewers)

| Lens | Weight | Score | Reviewers | Lowest | Note |
|---|---|---|---|---|---|
| strategy | 3 | 4 | 1 | 4 |  |
| security | 3 | 2 | 1 | 2 | critical lens |
| privacy | 3 | 3 | 1 | 3 | critical lens |
| auth | 2 | 3 | 1 | 3 | critical lens |
| functionality | 3 | 4 | 1 | 4 |  |
| quality | 2 | 3 | 1 | 3 |  |
| journey | 2 | 4 | 1 | 4 |  |
| ux | 2 | 4 | 1 | 4 |  |
| data | 3 | 4 | 1 | 4 | critical lens |
| release | 1 | 3 | 1 | 3 |  |

## Counts

Open findings — S1: 1 · S2: 2 · S3: 5 · S4: 1 · blockers: 1 · accepted risks (valid): 0
Evidence — verification run · failed: 0 · open S1/S2 with no file evidence: 0

## Blockers

| Priority | ID | Sev | Lens | Title | Where | Owner |
|---|---|---|---|---|---|---|
| 900 | F-001 | S1 | security | Session token stored in UserDefaults and printed to the log | PocketPantry/Auth/SessionStore.swift:7 | — |

## Fix before ship

| Priority | ID | Sev | Lens | Title | Where | Owner |
|---|---|---|---|---|---|---|
| 900 | F-001 | S1 | security | Session token stored in UserDefaults and printed to the log | PocketPantry/Auth/SessionStore.swift:7 | — |
| 360 | F-002 | S2 | security | API base URL uses cleartext HTTP | PocketPantry/Network/API.swift:4 | Sam |
| 360 | F-003 | S2 | auth | No way to delete an account | PocketPantry/Auth/SessionStore.swift | Sam |

## Carry over (priority order)

| Priority | ID | Sev | Lens | Title | Where | Owner |
|---|---|---|---|---|---|---|
| 60 | F-004 | S3 | quality | No automated tests and no CI | (no file evidence) | — |
| 60 | F-008 | S3 | journey | First launch shows an empty screen with no guidance | (no file evidence) | — |
| 40 | F-005 | S3 | privacy | No privacy manifest; camera and photo permissions need a purpose revie | (no file evidence) | — |
| 20 | F-006 | S3 | release | Payment test key is in source code | PocketPantry/Config.swift:1 | — |
| 20 | F-009 | S3 | strategy | Unplanned animation work added this sprint | (no file evidence) | — |
| 2 | F-007 | S4 | quality | Force-try when decoding the list | PocketPantry/Views/ListsView.swift:4 | — |

## Accepted risks

None.
