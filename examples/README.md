# Examples

Everything here uses **invented data**. Nothing comes from a real project, and nothing quotes a real person.

| Path | What it shows | How it was made |
|---|---|---|
| `gate/repo-scan-sample.md` | What the read-only repo scan reports for a small app: leads, with secrets masked | Real output of `repo_scan.py` on a fictional app ("Pocket Pantry") with planted problems |
| `gate/01-first-gate/` | A first Gate that ends **NO-GO**: one critical issue blocks the release although the score (68.3) looks fine | Real output of `verify_findings.py` and `gate_score.py` (`decision-input.md`, `findings.json`, `scores.json`); `decision.md` is written by hand from them |
| `gate/02-re-gate/` | The re-gate after the fixes: **GO WITH CONDITIONS** (73.3). The fixes are proven by `count` evidence that the script re-ran against the repo | Same: real script output, hand-written `decision.md` |
| `idea-memo-example.md` | The shape of an Idea-track memo | Written by hand with invented evidence, clearly marked |

## Read them in this order
1. `gate/repo-scan-sample.md`: the scanner finds *leads*, including one harmless match, which is why a reviewer must confirm each one.
2. `gate/01-first-gate/decision-input.md`, then `decision.md`: how a blocker outranks a good score.
3. `gate/02-re-gate/decision-input.md`, then `decision.md`: how a fix is verified by re-counting, and what "with conditions" means.

## Reproduce the numbers
The `findings.json` and `scores.json` in each folder are the inputs. With a gate folder that contains them plus a repo to check against, the same decision comes out of `scripts/gate_score.py`:
```bash
python3 skills/gogoidea/scripts/verify_findings.py <gate-folder> --repo <repo>
python3 skills/gogoidea/scripts/gate_score.py <gate-folder> --profile consumer-app --mode standard
```
The fictional repo is not included, so `verify_findings.py` can't re-check the file evidence here; its saved result (`verify-results.json`) is in each folder, so the scorer runs on the folder as it is and reproduces the recommendation shown.
