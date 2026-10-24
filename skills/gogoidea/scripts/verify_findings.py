#!/usr/bin/env python3
"""Check that the evidence cited by Gate findings is real, by re-running it.

Usage: verify_findings.py <gate-dir> --repo <repo>

Reads <gate-dir>/findings.json and re-checks two kinds of evidence against the repo:

  {"type": "file",  "path": "app/x.ts", "line": 42, "snippet": "text on or near that line"}
      the file exists inside the repo, the line is in range, and the snippet appears within two
      lines of it.
  {"type": "count", "path": "app/x.ts", "pattern": "regex", "expected": 3, "ref": "HEAD", "flags": "i"}
      the number of LINES matching the Python regex `pattern` in that file equals `expected`.
      `ref` (optional) is a git ref read with `git show ref:path`, so "HEAD" and "origin/main"
      counts can be checked; without it the working-tree file is used. `flags` may contain "i".

Any claim of presence or absence ("0 matches", "no tests", "8 lines") should be recorded as
`count` evidence so a stale or mistaken number is caught here, not in front of the user.
Other types (test, issue, log, manual) can't be checked by script and are reported as
unverifiable. Writes <gate-dir>/verify-results.json and exits 1 if any check fails.
Read-only: the only subprocess is `git show`. Standard library only.
"""
import argparse
import json
import os
import re
import subprocess
import sys

CHECKABLE = ("file", "count")
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/~^@-]*$")


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def read_text(repo, rel, ref):
    """Return (text, problem). Reads the working-tree file, or `git show ref:rel` when ref is given."""
    if os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
        return None, "path must be relative and stay inside the repo: " + rel
    if ref:
        if not SAFE_REF.match(ref):
            return None, "unsafe or invalid git ref: %r" % ref
        try:
            r = subprocess.run(["git", "-C", repo, "--no-optional-locks", "show", "%s:%s" % (ref, rel.replace(os.sep, "/"))],
                               capture_output=True, text=True, timeout=20)
        except Exception as ex:
            return None, "cannot run git: %s" % ex
        if r.returncode != 0:
            return None, "cannot read %s:%s (is the ref and path right?)" % (ref, rel)
        return r.stdout, None
    full = os.path.realpath(os.path.join(repo, rel))
    if not (full == repo or full.startswith(repo + os.sep)):
        return None, "path escapes the repo: " + rel
    if not os.path.isfile(full):
        return None, "file not found: " + rel
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(), None
    except OSError as ex:
        return None, "cannot read %s: %s" % (rel, ex)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gate_dir")
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()

    repo = os.path.realpath(a.repo)
    path = os.path.join(a.gate_dir, "findings.json")
    if not os.path.exists(path):
        sys.exit("findings.json not found in " + a.gate_dir)
    with open(path, encoding="utf-8") as f:
        findings = json.load(f)

    verified, failed, unverifiable, weak, no_check_high = [], {}, [], [], []
    for fnd in findings:
        fid = fnd.get("id", "?")
        ev = fnd.get("evidence") or []
        checkable = [e for e in ev if e.get("type") in CHECKABLE]
        problems, ok_count = [], 0
        for e in checkable:
            rel = e.get("path", "")
            text, problem = read_text(repo, rel, e.get("ref") if e.get("type") == "count" else None)
            if problem:
                problems.append(problem)
                continue
            lines = text.splitlines()
            if e["type"] == "file":
                line = e.get("line")
                if not isinstance(line, int) or line < 1 or line > len(lines):
                    problems.append("line out of range for %s: %r (file has %d lines)" % (rel, line, len(lines)))
                    continue
                snippet = norm(e.get("snippet"))
                if snippet:
                    window = norm(" ".join(lines[max(0, line - 3):line + 2]))
                    if snippet not in window:
                        problems.append("snippet not found near %s:%d" % (rel, line))
                        continue
                else:
                    weak.append(fid)
            else:  # count
                pattern, expected = e.get("pattern"), e.get("expected")
                if not pattern or not isinstance(expected, int) or isinstance(expected, bool):
                    problems.append("count evidence needs a regex `pattern` and an integer `expected` (%s)" % rel)
                    continue
                try:
                    rx = re.compile(pattern, re.I if "i" in (e.get("flags") or "") else 0)
                except re.error as ex:
                    problems.append("invalid regex %r: %s" % (pattern, ex))
                    continue
                found = sum(1 for line in lines if rx.search(line))
                if found != expected:
                    where = "%s%s" % ((e.get("ref") + ":") if e.get("ref") else "", rel)
                    problems.append("count mismatch for %s /%s/: claimed %d matching lines, found %d" % (where, pattern, expected, found))
                    continue
            ok_count += 1
        if problems:
            failed[fid] = problems
        elif ok_count:
            verified.append(fid)
        else:
            unverifiable.append(fid)
        if fnd.get("severity") in ("S1", "S2") and not checkable:
            no_check_high.append(fid)

    result = {"verified": verified, "failed": failed, "unverifiable": unverifiable,
              "high_severity_without_file_evidence": no_check_high,
              "file_evidence_without_snippet": sorted(set(weak))}
    with open(os.path.join(a.gate_dir, "verify-results.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("findings: %d · verified: %d · failed: %d · unverifiable (no file or count evidence): %d"
          % (len(findings), len(verified), len(failed), len(unverifiable)))
    for fid, probs in failed.items():
        for p in probs:
            print("  FAIL", fid, "-", p)
    if no_check_high:
        print("  note: S1/S2 findings with no file or count evidence (reproduce before relying on them): " + ", ".join(no_check_high))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
