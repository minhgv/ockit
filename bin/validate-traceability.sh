#!/usr/bin/env bash
# bin/validate-traceability.sh — thin wrapper for `ockit verify` (R-011)
#
# Ported from agy-kit's bin/validate-traceability.sh (R-027). The audit logic
# now lives in the ockit Python CLI; this script only forwards argv + exit code.
# Source: https://github.com/giapminh79/agy-kit/tree/main/bin/validate-traceability.sh
set -euo pipefail

if command -v ockit >/dev/null 2>&1; then
    exec ockit verify "$@"
elif [ -x .venv/bin/ockit ]; then
    exec .venv/bin/ockit verify "$@"
else
    echo "ockit: command not found on PATH or .venv/bin/ockit; install with 'pip install ockit'" >&2
    exit 1
fi
