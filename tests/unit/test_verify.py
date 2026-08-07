"""
test_verify.py — Unit tests for ockit verify engine (R-001, R-002, R-014, R-020)

Covers the traceability suite (R-001), ba-qa suite (R-002), agents + commands
suites (R-014) and the exit contract (R-020) against tmp fixtures.
"""

from __future__ import annotations

import gc
import os

import pytest

from ockit.verify import VerifyFinding, VerifyReport, run_verify

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_valid_template(tmp):
    """SPEC_TEMPLATE.md that passes every traceability template check."""
    plans = tmp / "plans"
    write(
        plans / "SPEC_TEMPLATE.md",
        """# SPEC: [FEATURE_NAME]

## 1. Executive Summary

### 1.2 Requirement Traceability Matrix (RTM)

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Foo | Arch | P0 | src/foo.py | tests/test_foo.py::test_r001 | qa/foo.log | Pending |

## 6. Test Plan & 12-Dimensional Edge Case Matrix (ACM)

### 6.2 12-Dimensional Business Edge Case Matrix (ACM)

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID |
|---------|----------------|---------------|------------------------|---------|
| E-001 | 1. Null / Missing | foo | bar | T-EDGE-001 |

## 8. Definition of Done & 3-State Verification

- [ ] All RTM requirements mapped 1:1 to passing tests
""",
    )
    return tmp


def make_spec_with(rtm=True, edge_case=True, unit_ref=True, req_id=True):
    lines = ["# SPEC: feature\n"]
    if rtm:
        lines.append("### 1.2 Requirement Traceability Matrix (RTM)\n")
        if req_id:
            lines.append(
                "| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |\n"
            )
            lines.append("|--------|--------|\n")
            ref = "tests/test_x.py::test_r001" if unit_ref else ""
            lines.append(
                f"| R-001 | desc | Src | P0 | src/x.py | {ref} | qa/x.log | Pending |\n"
            )
    if edge_case:
        lines.append("### 6.2 12-Dimensional Business Edge Case Matrix (ACM)\n")
        lines.append(
            "| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID |\n"
        )
        lines.append(
            "|---------|----------------|---------------|------------------------|---------|\n"
        )
        lines.append("| E-001 | 1. Null / Missing | x | y | T-EDGE-001 |\n")
    return "".join(lines)


def make_agent_file(path, name="planner", description="d", mode="subagent"):
    write(
        path,
        f"---\nname: {name}\ndescription: {description}\nmode: {mode}\n---\n\nbody\n",
    )


def make_command_file(path, body):
    write(path, body)


# ---------------------------------------------------------------------------
# R-001 — traceability suite
# ---------------------------------------------------------------------------


class TestTraceability:
    def test_r001_plans_dir_missing_fails(self, tmp_path):
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(f.level == "FAIL" for f in report.findings)
        assert any("SPEC_TEMPLATE" in f.message for f in report.findings)

    def test_r001_template_missing_rtm_fails(self, tmp_path):
        plans = tmp_path / "plans"
        write(plans / "SPEC_TEMPLATE.md", "# template without RTM\n")
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(f.level == "FAIL" and "RTM" in f.message for f in report.findings)

    def test_r001_template_missing_edge_case_fails(self, tmp_path):
        plans = tmp_path / "plans"
        write(
            plans / "SPEC_TEMPLATE.md",
            "# SPEC\n### 1.2 Requirement Traceability Matrix (RTM)\n| Req ID |\n|---|\n",
        )
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(
            f.level == "FAIL" and "Edge Case" in f.message for f in report.findings
        )

    def test_r001_e002_zero_active_specs_ok(self, tmp_path):
        make_valid_template(tmp_path)
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert any("No active feature SPECs" in f.message for f in report.findings)
        assert any(f.level == "OK" for f in report.findings)

    def test_r001_valid_template_and_spec_all_ok(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with())
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.error_count == 0
        assert any(
            "SPEC_alpha.md" in f.message and f.level == "OK" for f in report.findings
        )

    def test_r001_spec_missing_rtm_fails(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(rtm=False))
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(f.level == "FAIL" and "RTM" in f.message for f in report.findings)

    def test_r001_spec_rtm_without_req_id_table_fails(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(req_id=False))
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(f.level == "FAIL" and "RTM" in f.message for f in report.findings)

    def test_r001_e019_spec_missing_edge_case_warns_not_fails(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(edge_case=False))
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.error_count == 0
        assert report.warning_count >= 1
        assert any(
            f.level == "WARN" and "Edge Case" in f.message for f in report.findings
        )

    def test_r001_spec_missing_unit_test_ref_warns(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(unit_ref=False))
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.warning_count >= 1
        assert any(
            "Unit Test Reference" in f.message and f.level == "WARN"
            for f in report.findings
        )

    def test_r001_spec_with_unit_test_ref_ok(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(unit_ref=True))
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert not any(
            "Unit Test Reference" in f.message and f.level == "WARN"
            for f in report.findings
        )

    def test_r020_warnings_only_exit_zero(self, tmp_path):
        make_valid_template(tmp_path)
        write(
            tmp_path / "plans" / "SPEC_alpha.md",
            make_spec_with(edge_case=False, unit_ref=False),
        )
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.warning_count > 0

    def test_r020_any_fail_exits_one(self, tmp_path):
        make_valid_template(tmp_path)
        write(
            tmp_path / "plans" / "SPEC_alpha.md",
            make_spec_with(rtm=False, edge_case=False),
        )
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert report.error_count > 0

    def test_e016_double_verify_stable(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with(unit_ref=False))
        first = run_verify(suite="traceability", project_root=str(tmp_path))
        second = run_verify(suite="traceability", project_root=str(tmp_path))
        assert [(f.level, f.message) for f in first.findings] == [
            (f.level, f.message) for f in second.findings
        ]
        assert first.exit_code == second.exit_code

    def test_e010_loop_50x_stable_no_fd_growth(self, tmp_path):
        make_valid_template(tmp_path)
        write(tmp_path / "plans" / "SPEC_alpha.md", make_spec_with())
        write(tmp_path / "plans" / "SPEC_beta.md", make_spec_with(unit_ref=False))
        baseline = None
        for _ in range(50):
            report = run_verify(suite="traceability", project_root=str(tmp_path))
            assert report.error_count == 0
            gc.collect()
            if baseline is None:
                baseline = len(report.findings)
            assert len(report.findings) == baseline


# ---------------------------------------------------------------------------
# R-002 — ba-qa suite (phase10 port, ockit paths)
# ---------------------------------------------------------------------------


def make_ba_qa_fixture(tmp):
    """Golden fixture: mirrored skills + markers + SPEC_TEMPLATE + agents + README."""
    skills = {
        "ba-expert": (
            "# BA Expert\n12-Dimensional Business Edge-Case Matrix\nBounded Contexts\nUser Stories\nZod schemas\n"
        ),
        "qa-auditor": ("# QA Auditor\naudit_summary\nRuntime Risk Matrix\n"),
        "qa-test-gen": ("# QA Test Gen\ntest_plan\nGherkin BDD\n"),
        "qa-reproducer": (
            "# QA Reproducer\nreproduction_summary\nMinimal Reproduction Example\n"
        ),
    }
    for name, content in skills.items():
        write(tmp / "active" / ".opencode" / "skill" / name / "SKILL.md", content)
        write(tmp / "templates" / "skill" / name / "SKILL.md", content)

    write(
        tmp / "plans" / "SPEC_TEMPLATE.md",
        "# SPEC\n### 1.2 Requirement Traceability Matrix (RTM)\n### 6.2 ACM\n### NFR\n### DFD\n",
    )
    write(
        tmp / "active" / ".opencode" / "agent" / "planner.md",
        "# planner\nba-expert\n12-Dimensional\n",
    )
    write(tmp / "active" / ".opencode" / "agent" / "coder.md", "# coder\nqa-test-gen\n")
    write(
        tmp / "active" / ".opencode" / "agent" / "reviewer.md",
        "# reviewer\nqa-auditor\n",
    )
    write(tmp / "active" / ".opencode" / "agent" / "qa.md", "# qa\nqa-reproducer\n")
    write(tmp / "README.md", "# README\n")
    return tmp


class TestBaQa:
    def test_r002_golden_fixture_passes(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 0, report.findings
        assert report.error_count == 0

    def test_r002_missing_skill_fails(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        (tmp_path / "active" / ".opencode" / "skill" / "qa-auditor").rename(
            tmp_path / "active" / ".opencode" / "skill" / "qa-auditor-gone"
        )
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 1
        assert any(
            "qa-auditor" in f.message and f.level == "FAIL" for f in report.findings
        )

    def test_r002_skill_mirror_mismatch_fails(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        write(
            tmp_path / "active" / ".opencode" / "skill" / "ba-expert" / "SKILL.md",
            "# DIFFERENT CONTENT\n",
        )
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 1
        assert any("mirror" in f.message and f.level == "FAIL" for f in report.findings)

    def test_r002_skill_content_missing_markers_fails(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        write(
            tmp_path / "active" / ".opencode" / "skill" / "ba-expert" / "SKILL.md",
            "# bare\n",
        )
        write(tmp_path / "templates" / "skill" / "ba-expert" / "SKILL.md", "# bare\n")
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 1
        assert any(
            "ba-expert" in f.message and f.level == "FAIL" for f in report.findings
        )

    def test_r002_template_missing_dfd_fails(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        write(
            tmp_path / "plans" / "SPEC_TEMPLATE.md",
            "# SPEC\n### 1.2 Requirement Traceability Matrix (RTM)\n### 6.2 ACM\n### NFR\n",
        )
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 1
        assert any("DFD" in f.message and f.level == "FAIL" for f in report.findings)

    def test_r002_agent_content_missing_markers_fails(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        write(
            tmp_path / "active" / ".opencode" / "agent" / "planner.md",
            "# planner\nno markers here\n",
        )
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 1
        assert any(
            "planner.md" in f.message and f.level == "FAIL" for f in report.findings
        )

    def test_r002_missing_readme_warns(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        (tmp_path / "README.md").unlink()
        report = run_verify(
            suite="ba-qa",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.exit_code == 0
        assert any("README" in f.message and f.level == "WARN" for f in report.findings)


# ---------------------------------------------------------------------------
# R-014 — agents suite
# ---------------------------------------------------------------------------


class TestAgentsSuite:
    def test_r014_valid_agents_pass(self, tmp_path):
        agents = tmp_path / ".opencode" / "agent"
        make_agent_file(agents / "orchestrator.md", name="orchestrator", mode="primary")
        make_agent_file(agents / "planner.md", name="planner", mode="subagent")
        report = run_verify(suite="agents", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.error_count == 0

    def test_r014_e012_mode_all_fails(self, tmp_path):
        agents = tmp_path / ".opencode" / "agent"
        make_agent_file(agents / "planner.md", name="planner", mode="all")
        report = run_verify(suite="agents", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any("mode" in f.message and f.level == "FAIL" for f in report.findings)

    def test_r014_builtin_clobber_fails(self, tmp_path):
        agents = tmp_path / ".opencode" / "agent"
        make_agent_file(agents / "explore.md", name="explore", mode="subagent")
        make_agent_file(agents / "general.md", name="general", mode="subagent")
        make_agent_file(agents / "compaction.md", name="compaction", mode="subagent")
        report = run_verify(suite="agents", project_root=str(tmp_path))
        assert report.exit_code == 1
        clobbered = [
            f for f in report.findings if "built-in" in f.message and f.level == "FAIL"
        ]
        assert len(clobbered) == 3

    def test_r014_missing_frontmatter_fails(self, tmp_path):
        agents = tmp_path / ".opencode" / "agent"
        make_agent_file(
            agents / "planner.md", name="planner", description="", mode="subagent"
        )
        write(agents / "coder.md", "# no frontmatter at all\n")
        make_agent_file(agents / "qa.md", name="qa", description="d", mode="bogus")
        report = run_verify(suite="agents", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(
            "frontmatter" in f.message.lower() and f.level == "FAIL"
            for f in report.findings
        )
        assert any("name" in f.message and f.level == "FAIL" for f in report.findings)
        assert any("mode" in f.message and f.level == "FAIL" for f in report.findings)

    def test_r014_missing_agents_dir_fails(self, tmp_path):
        report = run_verify(suite="agents", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any("agent" in f.message and f.level == "FAIL" for f in report.findings)


# ---------------------------------------------------------------------------
# R-014 — commands suite
# ---------------------------------------------------------------------------


class TestCommandsSuite:
    ALLOWED = (
        "Run `./bin/validate-traceability.sh` for plan compliance.\n"
        "Run `./bin/validate-phase10-ba-qa.sh` for BA-QA.\n"
        "Run `./bin/scan-dependencies.sh` for supply chain.\n"
    )

    def test_r014_only_allowed_wrappers_ok(self, tmp_path):
        commands = tmp_path / ".opencode" / "command"
        write(commands / "gate.md", self.ALLOWED)
        report = run_verify(suite="commands", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.error_count == 0

    def test_r014_e011_dead_bin_ref_fails(self, tmp_path):
        commands = tmp_path / ".opencode" / "command"
        write(commands / "pipeline.md", "Run `./bin/safe-agent-run.sh` now.\n")
        report = run_verify(suite="commands", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(
            "safe-agent-run.sh" in f.message and f.level == "FAIL"
            for f in report.findings
        )

    def test_r014_e014_init_md_fails(self, tmp_path):
        commands = tmp_path / ".opencode" / "command"
        write(commands / "init.md", "# init\n")
        report = run_verify(suite="commands", project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any(
            "init.md" in f.message and f.level == "FAIL" for f in report.findings
        )

    def test_r014_ockit_init_md_ok(self, tmp_path):
        commands = tmp_path / ".opencode" / "command"
        write(commands / "ockit-init.md", "# init\nRun `!ockit init`\n")
        report = run_verify(suite="commands", project_root=str(tmp_path))
        assert report.exit_code == 0
        assert not any(
            "init.md" in f.message and f.level == "FAIL" for f in report.findings
        )

    def test_r014_missing_commands_dir_fails(self, tmp_path):
        report = run_verify(suite="commands", project_root=str(tmp_path))
        assert report.exit_code == 1


# ---------------------------------------------------------------------------
# Suite plumbing
# ---------------------------------------------------------------------------


class TestSuiteSelection:
    def test_unknown_suite_raises(self, tmp_path):
        with pytest.raises(ValueError, match="suite"):
            run_verify(suite="nope", project_root=str(tmp_path))

    def test_all_runs_every_suite(self, tmp_path):
        make_ba_qa_fixture(tmp_path)
        # SPEC_TEMPLATE must satisfy BOTH traceability (| Req ID | table,
        # Edge Case, 3-State) and ba-qa (RTM/ACM/NFR/DFD markers).
        write(
            tmp_path / "plans" / "SPEC_TEMPLATE.md",
            """# SPEC
### 1.2 Requirement Traceability Matrix (RTM)
| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Foo | Arch | P0 | src/foo.py | tests/test_foo.py | qa/foo.log | Pending |
### 6.2 12-Dimensional Business Edge Case Matrix (ACM)
| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID |
|---------|----------------|---------------|------------------------|---------|
| E-001 | 1. Null / Missing | foo | bar | T-EDGE-001 |
### NFR
### DFD
## 8. Definition of Done & 3-State Verification
""",
        )
        write(
            tmp_path / "active" / ".opencode" / "agent" / "planner.md",
            "---\nname: planner\ndescription: d\nmode: subagent\n---\n# planner\nba-expert\n12-Dimensional\n",
        )
        write(
            tmp_path / "active" / ".opencode" / "agent" / "coder.md",
            "---\nname: coder\ndescription: d\nmode: subagent\n---\n# coder\nqa-test-gen\n",
        )
        write(
            tmp_path / "active" / ".opencode" / "agent" / "reviewer.md",
            "---\nname: reviewer\ndescription: d\nmode: subagent\n---\n# reviewer\nqa-auditor\n",
        )
        write(
            tmp_path / "active" / ".opencode" / "agent" / "qa.md",
            "---\nname: qa\ndescription: d\nmode: subagent\n---\n# qa\nqa-reproducer\n",
        )
        write(
            tmp_path / "active" / ".opencode" / "command" / "gate.md",
            "Run `./bin/validate-traceability.sh`.\n",
        )
        write(tmp_path / "active" / "README.md", "# README\n")
        report = run_verify(
            suite="all",
            project_root=str(tmp_path / "active"),
            plans_dir=str(tmp_path / "plans"),
            templates_dir=str(tmp_path / "templates"),
        )
        assert report.suite == "all"
        assert report.error_count == 0

    def test_findings_have_levels(self):
        finding = VerifyFinding(level="WARN", message="m", path="p")
        assert finding.level == "WARN"
        assert finding.path == "p"
        report = VerifyReport(suite="traceability")
        assert report.exit_code == 0
