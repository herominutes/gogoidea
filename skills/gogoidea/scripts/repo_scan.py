#!/usr/bin/env python3
"""Read-only scan of a build (repo) that produces *signals* for the Gate track.

Usage: repo_scan.py <repo> [--out DIR] [--max-seconds 60]

Walks the repository without modifying it, running or installing anything, or using the
network, and writes repo-scan.json and repo-scan.md into --out (default ./gate-scan-out).
--out must not be inside the repo. Signals are LEADS, not findings: a reviewer must confirm
each one before it is recorded. Secrets are always masked in the output.

Standard library only; Python 3.8+.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

SKIP_DIRS = {".git", "node_modules", "Pods", ".build", "DerivedData", "build", "dist", "venv", ".venv",
             "__pycache__", ".next", ".gradle", "Carthage", "vendor", "coverage", ".idea", ".vscode",
             "xcuserdata", ".svn", "target", ".tox", ".mypy_cache", ".pytest_cache"}
BIN_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".pdf", ".zip", ".gz", ".tar", ".tgz",
           ".mp3", ".mp4", ".mov", ".wav", ".ttf", ".otf", ".woff", ".woff2", ".eot", ".class", ".jar",
           ".so", ".dylib", ".a", ".o", ".exe", ".dll", ".bin", ".car", ".nib", ".xib", ".storyboardc",
           ".pbxuser", ".lock", ".sqlite", ".db", ".heic", ".svg", ".xcassets"}
CODE_EXT = {".swift", ".m", ".mm", ".h", ".kt", ".java", ".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".go",
            ".rs", ".php", ".cs", ".sh", ".json", ".yml", ".yaml", ".plist", ".xml", ".toml", ".ini", ".cfg",
            ".gradle", ".html", ".vue", ".svelte", ".sql", ".env", ".entitlements", ".pbxproj", ".xcconfig"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html"}
SCRIPT_EXT = {".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".php"}
MAX_BYTES = 1000000
MAX_FILES = 20000
MAX_PER_RULE = 25
SEV_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}

SECRET_RULES = [
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}"), "high"),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "high"),
    ("stripe-live-key", re.compile(r"sk_live_[0-9a-zA-Z]{16,}"), "high"),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "high"),
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "medium"),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY"), "high"),
    ("jwt-token", re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "high"),
    ("generic-secret-assignment",
     re.compile(r"(?i)\b(?:api[_-]?key|secret|passwd|password|token|client[_-]?secret)\b\s*[:=]\s*[\"'][A-Za-z0-9_\-/+=]{16,}[\"']"),
     "medium"),
]
PLACEHOLDER = re.compile(r"(?i)example|your[_-]|xxxx|changeme|<[a-z_ -]+>|\$\{|process\.env|os\.environ|getenv|placeholder|dummy|sample")
STORAGE = re.compile(r"UserDefaults|localStorage|sessionStorage|AsyncStorage|SharedPreferences")
SENSITIVE = re.compile(r"(?i)token|password|passwd|secret|jwt|session|api[_-]?key|credential")
LOG = re.compile(r"\bprint\s*\(|NSLog|os_log|Logger\.|console\.(?:log|debug|info)|logger\.|logging\.|println\(")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs|UITests|[A-Za-z0-9_]*Tests)(/|$)")
TEST_FILE = re.compile(r"(Tests?\.swift|\.test\.[jt]sx?|\.spec\.[jt]sx?|(^|/)test_[^/]*\.py|_test\.py|_test\.go)$")

SMELL_RULES = [
    ("cleartext-http", "security", "medium",
     re.compile(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|10\.|192\.168\.|www\.w3\.org|schemas\.|www\.apple\.com/DTDs|xmlns)[A-Za-z0-9]"),
     CODE_EXT),
    ("tls-verification-disabled", "security", "high",
     re.compile(r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\"']?0|InsecureSkipVerify\s*:\s*true"),
     CODE_EXT),
    ("dynamic-eval-or-shell", "security", "medium",
     re.compile(r"\beval\s*\(|\bnew Function\s*\(|os\.system\s*\(|shell\s*=\s*True"), SCRIPT_EXT),
    ("html-injection-sink", "security", "medium",
     re.compile(r"\.innerHTML\s*=|dangerouslySetInnerHTML|document\.write\s*\("), JS_EXT),
    ("sql-string-building", "security", "medium",
     re.compile(r"(?i)[\"'](?:SELECT|INSERT|UPDATE|DELETE)\b[^\"']*[\"']\s*(?:\+|%|\.format\()|f[\"'](?:SELECT|INSERT|UPDATE|DELETE)\b[^\"']*\{"),
     CODE_EXT),
    ("weak-hash", "security", "low", re.compile(r"(?i)\b(?:md5|sha1)\s*\(|CC_MD5|Insecure\.(?:MD5|SHA1)"), CODE_EXT),
    ("auth-bypass-or-debug-flag", "security", "high",
     re.compile(r"(?i)\b(?:skip|bypass|disable)[_ ]?auth\b|\ballowInsecure\w*\s*=\s*true|\bisDebug\s*=\s*true|\bdebugMode\s*=\s*true"),
     CODE_EXT),
    ("test-key-in-source", "release", "medium",
     re.compile(r"(?:sk|pk)_test_[0-9a-zA-Z]{12,}"), CODE_EXT),
    ("staging-endpoint", "release", "low",
     re.compile(r"(?i)https?://[\w.-]*(?:staging|stage|sandbox)[\w.-]*\.[a-z]{2,}"), CODE_EXT),
    ("localhost-endpoint", "release", "low",
     re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?"), CODE_EXT),
]
COUNT_RULES = {
    "todo-fixme-hack": re.compile(r"\b(?:TODO|FIXME|HACK|XXX)\b"),
    "swift-try-bang": re.compile(r"\btry!"),
    "swift-fatalError": re.compile(r"\bfatalError\s*\("),
    "swift-force-cast": re.compile(r"\bas!"),
    "js-console-log": re.compile(r"\bconsole\.log\s*\("),
    "js-debugger": re.compile(r"\bdebugger\s*;"),
    "py-bare-except": re.compile(r"^\s*except\s*:"),
    "compiler-warning-directive": re.compile(r"#warning\b"),
}
TRACKERS = ["firebase", "crashlytics", "mixpanel", "amplitude", "segment", "appsflyer", "adjust", "branch.io",
            "facebooksdk", "fbsdk", "onesignal", "sentry", "posthog", "datadog", "google-analytics", "gtag",
            "revenuecat", "intercom", "braze", "clevertap"]
PRIVACY_APIS = ["CLLocationManager", "CNContactStore", "PHPhotoLibrary", "HKHealthStore", "AVCaptureDevice",
                "ATTrackingManager", "ASIdentifierManager", "navigator.geolocation", "getUserMedia",
                "UNUserNotificationCenter"]
AUTH_KEYS = [
    ("sign-in", re.compile(r"(?i)sign[ _-]?in\b|signIn\b|\blogin\b|log[ _-]?in\b")),
    ("sign-up", re.compile(r"(?i)sign[ _-]?up\b|signUp\b|register(?:User|Account)?\b|create[ _-]?account")),
    ("sign-out", re.compile(r"(?i)sign[ _-]?out|\blogout\b|log[ _-]?out")),
    ("password-reset", re.compile(r"(?i)reset[ _-]?password|forgot[ _-]?password|password[ _-]?reset")),
    ("email-verification", re.compile(r"(?i)verify[ _-]?email|email[ _-]?verif|confirm[ _-]?email")),
    ("account-deletion", re.compile(r"(?i)delete[ _-]?account|deleteAccount|account[ _-]?deletion|remove[ _-]?account")),
    ("keychain", re.compile(r"Keychain|SecItemAdd|SecItemCopyMatching")),
    ("sign-in-with-apple", re.compile(r"ASAuthorizationAppleIDProvider|Sign in with Apple|SignInWithApple")),
    ("token-refresh", re.compile(r"(?i)refresh[ _-]?token|refreshSession")),
    ("mfa-or-otp", re.compile(r"(?i)\bmfa\b|2fa|two[ _-]?factor|\botp\b")),
    ("oauth-social", re.compile(r"(?i)oauth|GoogleSignIn|FBSDKLogin|signInWithOAuth")),
]
CRED_FILES = re.compile(r"(\.pem|\.p12|\.pfx|\.keystore|\.jks|\.mobileprovision)$|(^|/)(GoogleService-Info\.plist|google-services\.json|id_rsa)$")


def mask(text):
    return text[:4] + "***(" + str(len(text)) + " chars)"


def safe_snippet(line, limit=140):
    """Return a trimmed line with any secret-looking text masked."""
    out = line.strip()
    for _, rx, _ in SECRET_RULES:
        out = rx.sub(lambda m: mask(m.group(0)), out)
    out = re.sub(r"(?i)(sk|pk)_(live|test)_[0-9a-zA-Z]{8,}", lambda m: mask(m.group(0)), out)
    return out[:limit] + ("…" if len(out) > limit else "")


def is_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in BIN_EXT:
        return False
    try:
        with open(path, "rb") as f:
            return b"\0" not in f.read(2048)
    except OSError:
        return False


def git(repo, *args):
    try:
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        r = subprocess.run(["git", "--no-optional-locks", "-C", repo] + list(args), capture_output=True,
                           text=True, timeout=10, env=env)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--out", default="gate-scan-out")
    ap.add_argument("--max-seconds", type=int, default=60)
    a = ap.parse_args()

    repo = os.path.realpath(a.repo)
    out = os.path.realpath(a.out)
    if not os.path.isdir(repo):
        sys.exit("repo not found: " + a.repo)
    if out == repo or out.startswith(repo + os.sep):
        sys.exit("--out must be outside the repo (the scan never writes into the build)")
    os.makedirs(out, exist_ok=True)

    started = time.time()
    signals, counts, locs = [], Counter(), {}
    rule_hits = Counter()
    lang, tests, source_files = Counter(), 0, 0
    trackers, privacy_apis, perm_strings = {}, {}, []
    privacy_manifests, entitlements, ci_files, lint_files, doc_files = [], [], [], [], []
    env_files, cred_files, conflict_files = [], [], []
    auth_counts, auth_first = Counter(), {}
    manifests, versions = [], []
    files_scanned, truncated = 0, False

    def add(cat, rule, sev, path, line, text, conf="medium"):
        rule_hits[rule] += 1
        if rule_hits[rule] <= MAX_PER_RULE:
            signals.append({"category": cat, "rule": rule, "severity_hint": sev, "path": path, "line": line,
                            "snippet": safe_snippet(text), "confidence": conf})

    for dirpath, dirnames, filenames in os.walk(repo, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not os.path.islink(os.path.join(dirpath, d))]
        for fn in filenames:
            if files_scanned >= MAX_FILES or time.time() - started > a.max_seconds:
                truncated = True
                break
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, repo).replace(os.sep, "/")
            if os.path.islink(full):
                continue
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            low = rel.lower()
            if CRED_FILES.search(rel):
                cred_files.append(rel)
            if re.search(r"(^|/)\.env(\.[A-Za-z0-9_-]+)?$", rel) and not re.search(r"\.(example|sample|template)$", rel):
                env_files.append(rel)
            if rel.endswith("PrivacyInfo.xcprivacy"):
                privacy_manifests.append(rel)
            if rel.endswith(".entitlements"):
                entitlements.append(rel)
            if low.startswith(".github/workflows/") or low in (".gitlab-ci.yml", "bitrise.yml", "jenkinsfile",
                                                               "codemagic.yaml", ".circleci/config.yml") or low.startswith("fastlane/"):
                ci_files.append(rel)
            if re.search(r"(^|/)(\.swiftlint\.yml|\.eslintrc[^/]*|eslint\.config\.[a-z]+|ruff\.toml|\.flake8|\.prettierrc[^/]*)$", rel):
                lint_files.append(rel)
            if re.match(r"(?i)(readme|changelog|license)[^/]*$", fn):
                doc_files.append(rel)
            if size > MAX_BYTES or not is_text(full):
                continue
            files_scanned += 1
            ext = os.path.splitext(fn)[1].lower()
            is_test = bool(TEST_PATH.search(rel) or TEST_FILE.search(rel))
            if ext in (".swift", ".m", ".mm", ".kt", ".java", ".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".go", ".rs", ".php", ".cs"):
                lang[ext] += 1
                if is_test:
                    tests += 1
                else:
                    source_files += 1
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError:
                continue

            # manifests, versions, plist permission strings
            if fn == "package.json":
                try:
                    d = json.loads(content)
                    deps = dict(d.get("dependencies", {}))
                    dev = d.get("devDependencies", {})
                    loose = [k for k, v in list(deps.items()) + list(dev.items())
                             if isinstance(v, str) and (v.strip() in ("*", "latest") or v.startswith(("git", "http", "github:")))]
                    manifests.append({"file": rel, "kind": "npm", "count": len(deps) + len(dev), "loose_specifiers": loose[:10]})
                    if d.get("version"):
                        versions.append({"file": rel, "version": str(d["version"])})
                except ValueError:
                    pass
            elif fn == "Package.resolved":
                try:
                    d = json.loads(content)
                    pins = d.get("pins") or d.get("object", {}).get("pins", [])
                    manifests.append({"file": rel, "kind": "swiftpm", "count": len(pins)})
                except ValueError:
                    pass
            elif fn == "Package.swift":
                manifests.append({"file": rel, "kind": "swiftpm-manifest", "count": content.count(".package(")})
            elif re.match(r"requirements.*\.txt$", fn):
                lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith(("#", "-"))]
                manifests.append({"file": rel, "kind": "pip", "count": len(lines),
                                  "unpinned": [l for l in lines if "==" not in l][:10]})
            elif fn in ("pyproject.toml", "Pipfile.lock", "go.mod", "Cargo.lock", "Gemfile.lock", "Podfile", "Podfile.lock"):
                manifests.append({"file": rel, "kind": fn, "count": len(re.findall(r"(?m)^\s{2}- ", content)) if fn == "Podfile.lock" else None})
            if fn.endswith(".pbxproj"):
                for key in ("MARKETING_VERSION", "CURRENT_PROJECT_VERSION"):
                    vals = sorted(set(re.findall(key + r"\s*=\s*([^;]+);", content)))
                    if vals:
                        versions.append({"file": rel, "key": key, "values": vals[:5]})
            if fn == "Info.plist":
                for key, text in re.findall(r"<key>(NS\w+UsageDescription)</key>\s*<string>(.*?)</string>", content, re.S):
                    perm_strings.append({"file": rel, "key": key, "text": text.strip()[:120]})
                if re.search(r"NSAllowsArbitraryLoads</key>\s*<true\s*/>", content):
                    add("security", "ats-arbitrary-loads", "high", rel, 1, "NSAllowsArbitraryLoads is true")

            check_code = ext in CODE_EXT or fn in ("Podfile", "Dockerfile", "Makefile")
            lines = content.splitlines()
            lowc = content.lower()
            for t in TRACKERS:
                if t in lowc and t not in trackers and (fn in ("package.json", "Package.resolved", "Podfile", "Podfile.lock", "Package.swift")
                                                       or ext in CODE_EXT):
                    trackers[t] = rel
            for api in PRIVACY_APIS:
                if api in content and api not in privacy_apis:
                    privacy_apis[api] = rel

            for i, line in enumerate(lines, 1):
                if len(line) > 2000:
                    continue
                for rule, rx, sev in SECRET_RULES:
                    m = rx.search(line)
                    if m and not PLACEHOLDER.search(line):
                        conf = "low" if (is_test or ext in (".md", ".txt") or re.search(r"\.(example|sample|template)$", fn)) else "medium"
                        add("security", "secret:" + rule, sev, rel, i, line, conf)
                        break
                if check_code:
                    for rule, cat, sev, rx, exts in SMELL_RULES:
                        if ext in exts or (not ext and rule in ("cleartext-http",)):
                            if rx.search(line):
                                if rule in ("staging-endpoint", "localhost-endpoint", "test-key-in-source") and is_test:
                                    continue
                                add(cat, rule, sev, rel, i, line, "low" if is_test else "medium")
                    if STORAGE.search(line) and SENSITIVE.search(STORAGE.sub("", line)):
                        add("security", "sensitive-value-in-local-storage", "high", rel, i, line, "low" if is_test else "medium")
                    if LOG.search(line) and SENSITIVE.search(line) and not is_test:
                        add("privacy", "sensitive-value-in-log", "medium", rel, i, line)
                    for key, rx in COUNT_RULES.items():
                        if rx.search(line):
                            counts[key] += 1
                            if key == "todo-fixme-hack" and not is_test:
                                locs.setdefault(key, [])
                                if len(locs[key]) < 10:
                                    locs[key].append({"path": rel, "line": i, "snippet": safe_snippet(line, 100)})
                    if not is_test:
                        for key, rx in AUTH_KEYS:
                            if rx.search(line):
                                auth_counts[key] += 1
                                auth_first.setdefault(key, rel)
                    if re.match(r"^(<<<<<<< |>>>>>>> )", line):
                        conflict_files.append(rel)
                        break
        else:
            continue
        break

    # tracked-file checks via git (read-only)
    gitinfo = {"is_repo": False}
    inside = git(repo, "rev-parse", "--is-inside-work-tree")
    tracked = []
    if inside == "true":
        gitinfo["is_repo"] = True
        gitinfo["branch"] = git(repo, "branch", "--show-current")
        status = git(repo, "status", "--porcelain") or ""
        slines = [l for l in status.splitlines() if l.strip()]
        gitinfo["uncommitted_changes"] = len([l for l in slines if not l.startswith("??")])
        gitinfo["untracked_files"] = len([l for l in slines if l.startswith("??")])
        tag = git(repo, "describe", "--tags", "--abbrev=0")
        gitinfo["last_tag"] = tag
        if tag:
            gitinfo["commits_since_tag"] = git(repo, "rev-list", "--count", tag + "..HEAD")
        gitinfo["last_commit_date"] = git(repo, "log", "-1", "--format=%cI")
        gitinfo["remotes_configured"] = len((git(repo, "remote") or "").split())
        tracked = (git(repo, "ls-files") or "").splitlines()
        tracked_env = [t for t in tracked if re.search(r"(^|/)\.env(\.[A-Za-z0-9_-]+)?$", t) and not re.search(r"\.(example|sample|template)$", t)]
        for t in tracked_env:
            add("security", "env-file-tracked-in-git", "high", t, 1, "environment file is tracked by git")
        for t in tracked:
            if CRED_FILES.search(t):
                add("security", "credential-file-tracked-in-git", "medium" if "GoogleService" in t or "google-services" in t else "high", t, 1, "credential-style file is tracked by git")
        big = []
        for t in tracked:
            try:
                if os.path.getsize(os.path.join(repo, t)) > 5 * 1024 * 1024:
                    big.append(t)
            except OSError:
                pass
        gitinfo["large_tracked_files"] = big[:10]
    for rel in sorted(set(conflict_files)):
        add("quality", "merge-conflict-marker", "high", rel, 1, "merge conflict marker present")

    # auth checklist: signals for reviewers to confirm
    def seen(key):
        return {"status": "found" if auth_counts[key] else "not found in code (verify manually)",
                "mentions": auth_counts[key], "first_file": auth_first.get(key)}
    auth_checklist = {k: seen(k) for k, _ in AUTH_KEYS}
    note = []
    if auth_counts["sign-up"] and not auth_counts["account-deletion"]:
        note.append("Accounts can be created but no account-deletion flow was found in code. Major app stores require in-app deletion when accounts can be created: verify.")
    if auth_counts["oauth-social"] and not auth_counts["sign-in-with-apple"]:
        note.append("Social login found but no Sign in with Apple: check store rules for your platform and login types.")
    if auth_counts["sign-in"] and not auth_counts["keychain"]:
        note.append("Sign-in found but no Keychain usage: check where tokens are stored.")
    if auth_counts["sign-in"] and not auth_counts["sign-out"]:
        note.append("Sign-in found but no sign-out flow: verify.")

    ratio = round(tests / source_files, 3) if source_files else None
    scan = {
        "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "repo_name": os.path.basename(repo),
        "files_scanned": files_scanned,
        "truncated": truncated,
        "signals": sorted(signals, key=lambda s: (SEV_ORDER[s["severity_hint"]], s["category"], s["path"], s["line"])),
        "signal_counts_by_rule": dict(rule_hits),
        "counts": dict(counts),
        "todo_locations": locs.get("todo-fixme-hack", []),
        "privacy": {"tracking_sdks_found": trackers, "sensitive_apis_found": privacy_apis,
                    "permission_strings": perm_strings[:20], "privacy_manifests": privacy_manifests,
                    "entitlement_files": entitlements},
        "auth_checklist": auth_checklist, "auth_notes": note,
        "quality": {"source_files_by_ext": dict(lang), "test_files": tests, "source_files": source_files,
                    "test_to_source_ratio": ratio, "ci_files": ci_files[:10], "lint_configs": lint_files[:10],
                    "docs_present": doc_files[:10], "env_files_present": env_files[:10],
                    "credential_style_files": cred_files[:10]},
        "git": gitinfo,
        "dependencies": manifests[:30],
        "versions": versions[:20],
        "limits": ["Static pattern scan only: no build, no tests, no network, no dependency vulnerability lookup.",
                   "Signals are leads for a reviewer to confirm; absence of a signal is not proof of absence."],
    }
    with open(os.path.join(out, "repo-scan.json"), "w", encoding="utf-8") as f:
        json.dump(scan, f, indent=2)

    md = ["# Repo scan (signals, not findings)", "",
          "Repo: `%s` · files scanned: %d%s · read-only, no network" % (scan["repo_name"], files_scanned, " (TRUNCATED)" if truncated else ""),
          "", "## Top signals", "",
          "| Sev | Category | Rule | Where | Snippet (secrets masked) |", "|---|---|---|---|---|"]
    for s in scan["signals"][:40]:
        md.append("| %s | %s | %s | `%s:%s` | `%s` |" % (s["severity_hint"], s["category"], s["rule"], s["path"], s["line"],
                                                       s["snippet"].replace("|", "\\|").replace("`", "'")))
    if len(scan["signals"]) > 40:
        md.append("")
        md.append("_%d more in repo-scan.json._" % (len(scan["signals"]) - 40))
    md += ["", "## Counts", "", "| Item | Count |", "|---|---|"]
    for k, v in sorted(counts.items()):
        md.append("| %s | %d |" % (k, v))
    md += ["", "## Privacy leads", "",
           "- Tracking/analytics SDKs mentioned: %s" % (", ".join(sorted(trackers)) or "none found"),
           "- Sensitive APIs referenced: %s" % (", ".join(sorted(privacy_apis)) or "none found"),
           "- Permission strings: %d · privacy manifest files: %d" % (len(perm_strings), len(privacy_manifests))]
    md += ["", "## Auth checklist (verify each manually)", "", "| Flow | Status | Mentions |", "|---|---|---|"]
    for k, v in auth_checklist.items():
        md.append("| %s | %s | %d |" % (k, v["status"], v["mentions"]))
    for n in note:
        md.append("")
        md.append("- ⚠ " + n)
    q = scan["quality"]
    md += ["", "## Quality and release leads", "",
           "- Tests: %d test files vs %d source files (ratio %s)" % (tests, source_files, ratio),
           "- CI config: %s" % (", ".join(ci_files[:5]) or "none found"),
           "- Lint config: %s" % (", ".join(lint_files[:5]) or "none found"),
           "- Docs: %s" % (", ".join(doc_files[:6]) or "none found"),
           "- Git: %s" % json.dumps({k: v for k, v in gitinfo.items() if k != "large_tracked_files"}),
           "- Dependency manifests: %d (see JSON)" % len(manifests)]
    md += ["", "## Limits", ""] + ["- " + l for l in scan["limits"]]
    with open(os.path.join(out, "repo-scan.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    high = sum(1 for s in signals if s["severity_hint"] == "high")
    print("scanned %d files; %d signals shown (%d high); wrote %s/repo-scan.json and repo-scan.md"
          % (files_scanned, len(signals), high, os.path.relpath(out)))


if __name__ == "__main__":
    main()
