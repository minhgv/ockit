"""
test_verify_contract_fresh.py — Enforce that verify-contract.md is freshly generated
from verify.py constants (R-gap: verify-contract staleness prevention).

If verify.py constants change but verify-contract.md is not regenerated, this test
fails. Run `python scripts/generate_verify_contract.py` to refresh.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CONTRACT = os.path.join(
    _ROOT,
    "src",
    "ockit",
    "templates",
    "skill",
    "ba-expert",
    "references",
    "verify-contract.md",
)
_GENERATOR = os.path.join(_ROOT, "scripts", "generate_verify_contract.py")


class TestVerifyContractFresh:
    def test_contract_file_exists(self):
        assert os.path.isfile(_CONTRACT), f"verify-contract.md missing: {_CONTRACT}"

    def test_contract_is_fresh(self):
        """Regenerate in-process and compare against committed copy."""
        assert os.path.isfile(_GENERATOR), f"Generator missing: {_GENERATOR}"

        with open(_CONTRACT, "r", encoding="utf-8") as fh:
            committed = fh.read()

        import importlib.util

        sys.path.insert(0, os.path.join(_ROOT, "src"))
        spec = importlib.util.spec_from_file_location("gen", _GENERATOR)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fresh = mod.generate()

        assert fresh == committed, (
            "verify-contract.md is STALE. verify.py constants changed but the reference "
            "was not regenerated.\n"
            f"Fix: run `python scripts/generate_verify_contract.py` from repo root.\n"
            f"Committed length: {len(committed)}, fresh length: {len(fresh)}"
        )
