#!/usr/bin/env bash
# bin/validate-phase10-ba-qa.sh — thin wrapper for `ockit verify --suite ba-qa` (R-011)
#
# Ported from agy-kit's bin/validate-phase10-ba-qa.sh (R-027). The audit logic
# now lives in the ockit Python CLI; this script only forwards argv + exit code.
# Source: https://github.com/giapminh79/agy-kit/tree/main/bin/validate-phase10-ba-qa.sh
set -euo pipefail

if command -v ockit >/dev/null 2>&1; then
    exec ockit verify --suite ba-qa "$@"
elif [ -x .venv/bin/ockit ]; then
    exec .venv/bin/ockit verify --suite ba-qa "$@"
else
    echo "ockit: command not found on PATH or .venv/bin/ockit; install with 'pip install ockit'" >&2
    exit 1
fi
