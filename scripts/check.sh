#!/usr/bin/env bash
# Runs every check before a push: verify.sh, the test suite and the test budget.
# All checks are free and local: no model calls, paid services or rate-limited APIs.
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
bash scripts/verify.sh
python3 -m pytest -q -p no:cacheprovider tests
python3 plugins/workbench-core/scripts/audit_tests.py . --check
echo "PASS all checks"
