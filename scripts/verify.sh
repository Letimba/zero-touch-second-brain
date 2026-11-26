#!/usr/bin/env bash
# Release hygiene gate. Read-only. Prints findings, exits 1 on any finding.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FINDINGS=0

fail() { printf 'FINDING: %s\n' "$1"; FINDINGS=$((FINDINGS+1)); }

for f in LICENSE README.md QUICKSTART.md SECURITY.md CONTRIBUTING.md CHANGELOG.md .gitignore; do
  [ -f "$ROOT/$f" ] || fail "missing $f"
done

if grep -rIEq '(0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})' \
    "$ROOT" --exclude-dir=.git --exclude='verify.sh' --exclude='test_release.py'; then
  fail "secret-shaped string found"
fi

if grep -rIEq '/storage/emulated|/data/data/com\.termux|tim-engine|Völker' \
    "$ROOT" --exclude-dir=.git --exclude='verify.sh' --exclude='test_release.py' \
    --exclude='RELEASE-CHECKLIST.md' --exclude='DISTRIBUTION-PLAN.md' --exclude='brain-auto-termux.sh'; then
  fail "personal path or name found"
fi

for d in examples/vault/50_Personen examples/vault/60_Tagebuch automation/logs automation/state automation/queue; do
  [ -e "$ROOT/$d" ] && fail "runtime/personal directory present: $d"
done

while IFS= read -r f; do bash -n "$f" || fail "bash syntax: $f"; done \
  < <(find "$ROOT" -type f -name '*.sh' -not -path '*/.git/*')

while IFS= read -r f; do python3 -m py_compile "$f" || fail "python syntax: $f"; done \
  < <(find "$ROOT" -type f -name '*.py' -not -path '*/.git/*')

printf 'findings=%s\n' "$FINDINGS"
[ "$FINDINGS" -eq 0 ]
