#!/usr/bin/env bash
# bin/scan-dependencies.sh — thin wrapper for `ockit scan-deps` (R-012/R-026)
#
# Ported from agy-kit's bin/scan-dependencies.sh (R-027). The scanner logic
# now lives in the ockit Python CLI; this script only forwards argv + exit code.
# Source: https://github.com/giapminh79/agy-kit/tree/main/bin/scan-dependencies.sh
set -euo pipefail

if command -v ockit >/dev/null 2>&1; then
    exec ockit scan-deps "$@"
elif [ -x .venv/bin/ockit ]; then
    exec .venv/bin/ockit scan-deps "$@"
else
    echo "ockit: command not found on PATH or .venv/bin/ockit; install with 'pip install ockit'" >&2
    exit 1
fi
