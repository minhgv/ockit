"""
test_installer_skill_exclusion.py — R-005, R-006 (ISSUE-04)

- R-005: the 2 demo skills (example-skill, test-skill) MUST NOT appear in the
  installer's copy plan → they never ship into a target project.
- R-006: their content MUST be preserved under tests/fixtures/skills/ for
  fixture use (relocated, not discarded).
"""

from __future__ import annotations

from pathlib import Path

from ockit.installer import OckitInstaller

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_SKILLS = REPO_ROOT / "tests" / "fixtures" / "skills"

_DEMO_SKILLS = ("example-skill", "test-skill")


def test_r005_demo_skills_not_in_plan():
    """R-005: installer._plan_files() MUST NOT list the demo skills."""
    installer = OckitInstaller()  # default packaged templates_dir
    plan = installer._plan_files()
    offending = [
        rel
        for rel in plan
        for demo in _DEMO_SKILLS
        if rel.replace("\\", "/") == f"skill/{demo}/SKILL.md"
    ]
    assert not offending, (
        "What=demo skills still in installer copy plan; "
        f"Context=_plan_files() listed {offending}; "
        "Fix=remove src/ockit/templates/skill/{example-skill,test-skill}/ so "
        "ockit init never copies demo skills into target projects."
    )


def test_r006_demo_skills_preserved_in_fixtures():
    """R-006: demo skill content MUST be preserved under tests/fixtures/skills/."""
    for demo in _DEMO_SKILLS:
        fixture = FIXTURES_SKILLS / demo / "SKILL.md"
        assert fixture.exists(), (
            "What=demo skill fixture missing; "
            f"Context=expected {fixture}; "
            "Fix=relocate the demo SKILL.md to tests/fixtures/skills/ "
            f"(preserve content for fixture use)."
        )
        assert fixture.read_text(encoding="utf-8").strip(), (
            "What=demo skill fixture empty; "
            f"Context={fixture} has zero content; "
            "Fix=copy the original SKILL.md body into the fixture path."
        )
