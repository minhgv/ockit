"""
test_html_doc_updated.py — R-010 (doc-traceability)

docs/ockit_workflow_and_feature.html §16 ISSUE-01/03/04 entries MUST be marked
RESOLVED with the date 2026-08-07, and §17 risk-top-3 card MUST reflect the
resolved state.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HTML = REPO_ROOT / "docs" / "ockit_workflow_and_feature.html"

_RESOLVED_TOKEN = "RESOLVED 2026-08-07"
_ISSUES = ("ISSUE-01", "ISSUE-03", "ISSUE-04")


def _section(html: str, issue: str) -> str:
    """Extract the text between an <h3>ISSUE-NN ... heading and the next <h3>."""
    start = html.find(f"<h3>{issue}")
    assert start != -1, f"could not locate <h3>{issue} heading in HTML"
    next_h3 = html.find("<h3>", start + 4)
    end = next_h3 if next_h3 != -1 else len(html)
    return html[start:end]


def test_r010_issue_entries_marked_resolved():
    """R-010: each of ISSUE-01/03/04 carries a RESOLVED marker + fix-applied note."""
    html = HTML.read_text(encoding="utf-8")
    for issue in _ISSUES:
        section = _section(html, issue)
        assert _RESOLVED_TOKEN in section, (
            "What=ISSUE entry missing RESOLVED marker; "
            f"Context={issue} §16 section does not contain '{_RESOLVED_TOKEN}'; "
            "Fix=append a RESOLVED badge to the <h3> heading and a "
            "'✅ Fix applied' paragraph citing plans/SPEC_top3_risk_fixes.md."
        )
        assert "Fix applied" in section or "fix applied" in section.lower(), (
            "What=ISSUE entry missing 'Fix applied' note; "
            f"Context={issue} §16 section has RESOLVED badge but no applied-fix paragraph; "
            "Fix=add a <p><b>✅ Fix applied:</b> ...</p> describing the change + SPEC ref."
        )


def test_r010_section17_risk_card_marked_resolved():
    """R-010: §17 'Risk top-3' card MUST reflect the resolved state."""
    html = HTML.read_text(encoding="utf-8")
    marker = html.find("Risk top-3")
    assert marker != -1, "could not locate §17 Risk top-3 card"
    card = html[marker : marker + 600]
    assert _RESOLVED_TOKEN in card or "RESOLVED" in card, (
        "What=§17 risk card not marked resolved; "
        f"Context=card text=\n{card[:400]}; "
        "Fix=update the §17 'Risk top-3 cần fix' heading + list items to show "
        "all 3 RESOLVED with date 2026-08-07."
    )
