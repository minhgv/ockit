"""
test_no_leaked_config.py — R-004: no personal config leaks outside the
portable shipped template (ISSUE-03).

Single source of truth for opencode.json = ``src/ockit/templates/opencode.json``
(byte-identical mirror = ``.opencode/opencode.json``). No other opencode.json in
the repo may carry personal provider/MCP/plugin pins.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Personal-pin fingerprints harvested from the deleted docs/opencode.json leak.
_PERSONAL_FINGERPRINTS = [
    "api.z.ai",
    "opencode.ai/zen",
    "figma-mcp-go",
    "webclaw",
    "@tarquinen",
    "openslimedit",
    "opencodex-fast",
    "gpt-5-nano",
]

# The ONLY two sanctioned opencode.json locations in the repo.
_SANCTIONED = {
    REPO_ROOT / ".opencode" / "opencode.json",
    REPO_ROOT / "src" / "ockit" / "templates" / "opencode.json",
}


def test_r004_docs_opencode_json_removed():
    """R-004: docs/opencode.json (leaked personal config) MUST be absent."""
    leaked = REPO_ROOT / "docs" / "opencode.json"
    assert not leaked.exists(), (
        "What=leaked personal config present in docs/; "
        f"Context={leaked} diverges from the portable single source of truth "
        f"src/ockit/templates/opencode.json; "
        "Fix=delete docs/opencode.json (git rm) — the shipped template is the "
        "only sanctioned opencode.json under docs-adjacent paths."
    )


def test_r004_no_stray_personal_config_outside_sanctioned():
    """R-004 / NFR-003: no opencode.json outside the 2 sanctioned paths may
    carry personal provider/MCP/plugin pins."""
    for path in REPO_ROOT.rglob("opencode.json"):
        if path in _SANCTIONED:
            continue
        # Skip anything inside vendored / build dirs we don't ship.
        parts = path.relative_to(REPO_ROOT).parts
        if parts[:1] in ((".venv",), ("node_modules",)):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = [fp for fp in _PERSONAL_FINGERPRINTS if fp in text]
        assert not hits, (
            "What=stray opencode.json carries personal config pins; "
            f"Context={path} matched fingerprints {hits}; "
            "Fix=delete the file or strip personal pins (provider baseURLs, "
            "MCP servers, third-party plugins, model pins) — only the portable "
            "template may carry config."
        )
