"""
test_verify_exit_contract.py — R-008

Regression guard: after all top-3 fixes, ``ockit verify`` MUST exit 0 with
0 errors / 0 warnings (traceability + ba-qa + agents/commands suites intact).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OCKIT_BIN = REPO_ROOT / ".venv" / "bin" / "ockit"


def test_r008_verify_clean_after_fixes():
    """R-008: ``ockit verify`` exits 0 with zero errors / zero warnings."""
    proc = subprocess.run(
        [str(OCKIT_BIN), "verify"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=60,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "What=ockit verify exited non-zero after fixes; "
        f"Context=exit={proc.returncode}; tail output=\n"
        f"{combined[-800:]}; "
        "Fix=re-run `ockit verify` and resolve every FAIL/warning; the SPEC "
        "baseline contract requires 0 errors / 0 warnings."
    )
    # The verify success line reads: "✅ Verify passed (0 warning(s))."
    # On a clean run it does NOT print an error count — exit 0 + the passed
    # summary + zero-warning token IS the contract.
    assert "Verify passed" in combined and "0 warning" in combined, (
        "What=verify summary did not report a clean pass; "
        f"Context=tail output=\n{combined[-800:]}; "
        "Fix=inspect the verify output and clear all warnings/errors."
    )
