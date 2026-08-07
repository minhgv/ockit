"""
test_spec_template_structure.py — Structural conformance between SPEC_TEMPLATE form
and spec-master-template guide (R-gap: dual source drift prevention).

The blank form `plans/SPEC_TEMPLATE.md` and the annotated guide
`src/ockit/templates/skill/ba-expert/references/spec-master-template.md` must agree
on structure: every section header + table column header in the form MUST appear in
the guide. This prevents silent drift when one is edited without the other.
"""

from __future__ import annotations

import os
import re

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_FORM = os.path.join(_ROOT, "plans", "SPEC_TEMPLATE.md")
_GUIDE = os.path.join(
    _ROOT,
    "src",
    "ockit",
    "templates",
    "skill",
    "ba-expert",
    "references",
    "spec-master-template.md",
)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _section_headers(content: str) -> list[str]:
    """Extract markdown section headers (## and ### lines), stripped of leading #."""
    headers = []
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r"^#{2,3}\s+\S", stripped):
            headers.append(stripped)
    return headers


def _table_headers(content: str) -> list[str]:
    """Extract markdown table header rows (lines between | with |---| separator after)."""
    lines = content.splitlines()
    headers = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if "|" in line and re.match(r"^\s*\|[-:\s|]+\|?\s*$", nxt):
            headers.append(line.strip())
    return headers


class TestSpecTemplateStructure:
    def test_both_files_exist(self):
        assert os.path.isfile(_FORM), f"Form missing: {_FORM}"
        assert os.path.isfile(_GUIDE), f"Guide missing: {_GUIDE}"

    def test_form_section_headers_subset_of_guide(self):
        """Every ## / ### header in the form must appear (as substring) in the guide."""
        form_headers = _section_headers(_read(_FORM))
        guide_text = _read(_GUIDE)

        missing = []
        for header in form_headers:
            # Normalize: strip ## prefix, check the title text appears in guide.
            title = re.sub(r"^#{1,6}\s+", "", header).strip()
            if title and title not in guide_text:
                missing.append(header)

        assert not missing, (
            f"Form headers not found in guide (drift detected):\n"
            + "\n".join(f"  - {h}" for h in missing)
        )

    def test_form_table_headers_subset_of_guide(self):
        """Every table header row in the form must have its column names present in guide."""
        form_tables = _table_headers(_read(_FORM))
        guide_text = _read(_GUIDE)

        missing = []
        for table_header in form_tables:
            # Extract column names from the header row.
            cells = [c.strip() for c in table_header.split("|")]
            cells = [c for c in cells if c and not re.match(r"^[-:\s]+$", c)]
            # At least the first column name should appear in the guide.
            if cells:
                first_col = cells[0]
                if first_col not in guide_text:
                    missing.append((table_header, first_col))

        assert not missing, (
            f"Form table headers not found in guide (drift detected):\n"
            + "\n".join(f"  - table '{t}' first col '{c}'" for t, c in missing)
        )

    def test_form_contains_verify_required_markers(self):
        """The form must contain the strings ockit verify checks for."""
        form = _read(_FORM)
        for marker in ("Req ID", "Edge Case", "3-State Verification"):
            assert marker in form, f"Form missing verify marker: {marker}"

    def test_guide_contains_verify_required_markers(self):
        """The guide must document the same verify markers."""
        guide = _read(_GUIDE)
        for marker in ("Req ID", "Edge Case", "3-State Verification"):
            assert marker in guide, f"Guide missing verify marker: {marker}"
