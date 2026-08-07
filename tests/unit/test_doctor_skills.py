"""
test_doctor_skills.py — R-007 (ISSUE-04)

After demo-skill relocation, ``ockit doctor`` on the repo MUST report
``skills_valid == True`` AND the active ``.opencode/skill/`` inventory MUST
contain exactly the 10 production skills (no example-skill / test-skill).
"""

from __future__ import annotations

from pathlib import Path

from ockit.doctor import run_doctor

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_SKILLS_DIR = REPO_ROOT / ".opencode" / "skill"

_DEMO_SKILLS = ("example-skill", "test-skill")
_EXPECTED_PRODUCTION_SKILLS = [
    "ba-expert",
    "brainstorming",
    "grill-me",
    "problem-solving",
    "qa-auditor",
    "qa-reproducer",
    "qa-test-gen",
    "quality-gate",
    "tdd-workflow",
    "writing-skills",
]


def test_r007_doctor_reports_exactly_ten_skills():
    """R-007 / NFR-005: doctor reports 10 production skills, zero demos."""
    res = run_doctor(project_root=str(REPO_ROOT))
    assert res["skills_valid"] is True, (
        "What=doctor skills_valid is False after demo relocation; "
        f"Context=doctor errors={res.get('errors')} warnings={res.get('warnings')}; "
        "Fix=ensure all 10 expected production skills are present under "
        ".opencode/skill/<name>/SKILL.md."
    )
    actual = {
        d.name
        for d in ACTIVE_SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    }
    demos_present = sorted(set(_DEMO_SKILLS) & actual)
    assert not demos_present, (
        "What=demo skills still present in active .opencode/skill/; "
        f"Context=found {demos_present}; "
        "Fix=delete .opencode/skill/{example-skill,test-skill}/."
    )
    missing = sorted(set(_EXPECTED_PRODUCTION_SKILLS) - actual)
    assert not missing, (
        "What=production skill missing from active inventory; "
        f"Context=missing {missing}; actual={sorted(actual)}; "
        "Fix=restore the missing production skill dirs from packaged templates."
    )
    # Exactly 10 (the production set), no extras.
    assert len(actual) == 10, (
        "What=active skill count is not exactly 10; "
        f"Context=found {len(actual)} skill dirs: {sorted(actual)}; "
        "Fix=remove any non-production skill dir from .opencode/skill/."
    )
