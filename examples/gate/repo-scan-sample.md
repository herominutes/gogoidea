# Repo scan (signals, not findings)

Repo: `pocketpantry` · files scanned: 7 · read-only, no network

## Top signals

| Sev | Category | Rule | Where | Snippet (secrets masked) |
|---|---|---|---|---|
| high | security | sensitive-value-in-local-storage | `PocketPantry/Auth/SessionStore.swift:7` | `UserDefaults.standard.set(token, forKey: "authToken")` |
| high | security | sensitive-value-in-local-storage | `PocketPantry/Auth/SessionStore.swift:16` | `UserDefaults.standard.removeObject(forKey: "authToken")` |
| medium | privacy | sensitive-value-in-log | `PocketPantry/Auth/SessionStore.swift:8` | `print("saved session token: \(token)")` |
| medium | release | test-key-in-source | `PocketPantry/Config.swift:1` | `let stripePublishable = "pk_t***(27 chars)"` |
| medium | security | cleartext-http | `PocketPantry/Network/API.swift:4` | `let baseURL = "http://api.pocketpantry.example/v1"` |

## Counts

| Item | Count |
|---|---|
| swift-try-bang | 1 |
| todo-fixme-hack | 2 |

## Privacy leads

- Tracking/analytics SDKs mentioned: none found
- Sensitive APIs referenced: none found
- Permission strings: 2 · privacy manifest files: 0

## Auth checklist (verify each manually)

| Flow | Status | Mentions |
|---|---|---|
| sign-in | found | 2 |
| sign-up | not found in code (verify manually) | 0 |
| sign-out | found | 1 |
| password-reset | not found in code (verify manually) | 0 |
| email-verification | not found in code (verify manually) | 0 |
| account-deletion | not found in code (verify manually) | 0 |
| keychain | not found in code (verify manually) | 0 |
| sign-in-with-apple | not found in code (verify manually) | 0 |
| token-refresh | not found in code (verify manually) | 0 |
| mfa-or-otp | not found in code (verify manually) | 0 |
| oauth-social | not found in code (verify manually) | 0 |

- ⚠ Sign-in found but no Keychain usage: check where tokens are stored.

## Quality and release leads

- Tests: 0 test files vs 5 source files (ratio 0.0)
- CI config: none found
- Lint config: none found
- Docs: README.md
- Git: {"is_repo": true, "branch": "main", "uncommitted_changes": 0, "untracked_files": 0, "last_tag": null, "last_commit_date": "2026-10-24T06:53:57-10:00", "remotes_configured": 0}
- Dependency manifests: 0 (see JSON)

## Limits

- Static pattern scan only: no build, no tests, no network, no dependency vulnerability lookup.
- Signals are leads for a reviewer to confirm; absence of a signal is not proof of absence.
