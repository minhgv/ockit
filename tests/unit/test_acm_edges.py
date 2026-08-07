"""
test_acm_edges.py — ACM E-001..E-032 coverage audit + gap fill (R-025)

Phase D4 fills the 12-Dimensional Edge Case Matrix gaps that existing suites
do not exercise. The header table maps every ACM edge to its covering test
(existing files or this file). New tests here target concurrency (E-008,
E-009), scale (E-025), plugin path deny (E-023), worktree cleanup (E-028) and
CLI-level actionable failures (E-001, E-032).

ACM coverage table (R-025):

| E-ID | Covering test |
|------|---------------|
| E-001 | tests/unit/test_acm_edges.py::test_e001_cli_init_missing_templates_exit1_actionable (+ test_installer.py::test_e001_missing_templates_error_actionable) |
| E-002 | tests/unit/test_verify.py::test_r001_e002_zero_active_specs_ok |
| E-003 | tests/unit/test_doctor.py::test_doctor_missing_opencode |
| E-004 | tests/unit/test_sync.py::test_r003_e004_empty_templates_exit1 |
| E-005 | tests/unit/test_validators.py::test_dotdot_canonicalized_to_single_dest |
| E-006 | tests/unit/test_validators.py::test_symlink_escape_denied |
| E-007 | tests/unit/test_validators.py::test_unicode_path_ok |
| E-008 | tests/unit/test_acm_edges.py::test_e008_parallel_init_force_no_corrupt_tree |
| E-009 | tests/unit/test_acm_edges.py::test_e009_parallel_sync_no_truncation (+ test_sync.py::test_e009_sync_idempotent) |
| E-010 | tests/unit/test_verify.py::test_e010_loop_50x_stable_no_fd_growth |
| E-011 | tests/unit/test_verify.py::test_r014_e011_dead_bin_ref_fails (+ test_bin_wrappers.py::test_bin_surface_exactly_three_wrappers) |
| E-012 | tests/unit/test_verify.py::test_r014_e012_mode_all_fails |
| E-013 | tests/unit/test_doctor.py::test_r013_invalid_opencode_json_error |
| E-014 | tests/unit/test_verify.py::test_r014_e014_init_md_fails (+ test_commands_native.py::test_no_init_md) |
| E-015 | tests/unit/test_installer.py::test_r007_idempotent_rerun (+ test_cli.py::test_r028_init_idempotent_cli) |
| E-016 | tests/unit/test_verify.py::test_e016_double_verify_stable |
| E-017 | tests/unit/test_sync.py::test_r003_e017_check_clean_when_no_extras |
| E-018 | tests/unit/test_installer.py::test_r022_partial_init_rerun_completes |
| E-019 | tests/unit/test_verify.py::test_r001_e019_spec_missing_edge_case_warns_not_fails (partial artefact -> WARN, not hard fail) |
| E-020 | tests/unit/test_scan_deps.py::test_r012_e020_slopsquat_in_requirements_fails |
| E-021 | tests/unit/test_validators.py::test_traversal_denied (+ test_cli.py::test_r028_init_traversal_exits_1) |
| E-022 | tests/unit/test_portable_config.py::test_no_home_paths |
| E-023 | tests/unit/test_acm_edges.py::test_e023_plugin_denies_tool_path_env (+ test_validators.py::test_path_traversal / test_sensitive_files) |
| E-024 | tests/unit/test_installer.py::test_r005_force_overwrites_and_creates_backup |
| E-025 | tests/unit/test_acm_edges.py::test_e025_500_specs_verify_within_nfr |
| E-026 | tests/unit/test_installer.py::test_r005_skips_junk_dotfiles (+ test_sync.py::test_r003_skips_junk) |
| E-027 | tests/unit/test_doctor.py::test_e027_probe_timeout_is_enforced (+ test_e027_doctor_runs_without_zombies) |
| E-028 | tests/unit/test_acm_edges.py::test_e028_worktree_exception_cleans_up |
| E-029 | tests/unit/test_portable_config.py::test_no_personal_external_directory |
| E-030 | tests/unit/test_portable_config.py::test_no_secret_literals |
| E-031 | tests/unit/test_sync.py::test_r003_e031_atomic_write_no_tmp_leftovers (atomic per-file replace) |
| E-032 | tests/unit/test_acm_edges.py::test_e032_cli_sync_missing_templates_exit1_actionable (+ test_sync.py::test_e032_missing_templates_dir_error, test_installer.py::test_e001_missing_templates_error_actionable) |
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import threading
import time

import pytest

from ockit import __file__ as ockit_init_file
from ockit import cli
from ockit.installer import OckitInstaller
from ockit import sync as sync_mod
from ockit.sync import run_sync
from ockit.verify import run_verify
from ockit.worktree import WorktreeManager

_PKG_DIR = os.path.dirname(os.path.abspath(ockit_init_file))
_ACTIVE_PLUGIN = os.path.join(
    os.path.dirname(_PKG_DIR), "..", ".opencode", "plugin", "ockit-quality-gate.js"
)
_TEMPLATE_PLUGIN = os.path.join(
    _PKG_DIR, "templates", "plugin", "ockit-quality-gate.js"
)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_template_tree(root, extra_files=None):
    write(root / "agent" / "planner.md", "# planner v1\n")
    write(root / "skill" / "ba-expert" / "SKILL.md", "# ba skill\n")
    write(root / "plugin" / "p.js", "export {}\n")
    write(root / "command" / "plan.md", "# plan v1\n")
    write(root / "opencode.json", '{"agent": {}}\n')
    write(root / "AGENTS.md", "# AGENTS template\n")
    for rel in extra_files or []:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content:{rel}\n", encoding="utf-8")
    return root


def make_active_tree(root):
    write(root / "agent" / "planner.md", "# planner v1\n")
    write(root / "command" / "plan.md", "# plan v1\n")
    write(root / "opencode.json", '{"agent": {}}\n')
    return root


# ---------------------------------------------------------------------------
# E-008 — concurrency: parallel init --force never corrupts the target tree
# ---------------------------------------------------------------------------


class TestE008ParallelInit:
    def test_e008_parallel_init_force_no_corrupt_tree(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = make_template_tree(
            tmp_path / "templates",
            extra_files=[
                "command/gate.md",
                "command/pipeline.md",
                "command/safe-pipeline.md",
            ],
        )
        installer = OckitInstaller(templates_dir=str(templates))

        # Seed one run first so backup + overwrite paths are exercised.
        installer.install(target="proj", lang="python")
        (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").write_text(
            "EDITED\n", encoding="utf-8"
        )

        errors: list[Exception] = []
        lock = threading.Lock()

        def do_install():
            try:
                installer.install(target="proj", lang="python", force=True)
            except Exception as exc:  # noqa: BLE001
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=do_install) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"parallel init raised: {errors}"
        # No corrupt tree: every template file exists with template content.
        for rel in [
            "agent/planner.md",
            "command/plan.md",
            "command/gate.md",
            "command/pipeline.md",
            "command/safe-pipeline.md",
            "opencode.json",
            "skill/ba-expert/SKILL.md",
        ]:
            assert (tmp_path / "proj" / ".opencode" / rel).exists(), rel
            if rel == "agent/planner.md":
                assert (tmp_path / "proj" / ".opencode" / rel).read_text(
                    encoding="utf-8"
                ) == "# planner v1\n"
        assert (tmp_path / "proj" / "AGENTS.md").exists()
        # No orphaned temp files.
        assert list((tmp_path / "proj").rglob(".ockit-tmp-*")) == []
        # A backup dir was created (E-024 behavior under concurrency).
        assert list((tmp_path / "proj").glob(".opencode.bak-*"))


# ---------------------------------------------------------------------------
# E-009 — concurrency: parallel sync --sync never truncates a file
# ---------------------------------------------------------------------------


class TestE009ParallelSync:
    def test_e009_parallel_sync_no_truncation(self, tmp_path):
        templates = make_template_tree(tmp_path / "templates")
        active = make_active_tree(tmp_path / "active")
        # Large content makes truncation detectable.
        big = "# planner v2\n" * 3000
        write(templates / "agent" / "planner.md", big)

        errors: list[Exception] = []
        lock = threading.Lock()

        def do_sync():
            try:
                run_sync(
                    active_dir=str(active),
                    templates_dir=str(templates),
                    mode="sync",
                )
            except Exception as exc:  # noqa: BLE001
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=do_sync) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"parallel sync raised: {errors}"
        assert (active / "agent" / "planner.md").read_text(encoding="utf-8") == big, (
            "file truncated by concurrent sync"
        )
        assert list(active.rglob(".ockit-tmp-*")) == []


# ---------------------------------------------------------------------------
# E-023 — security: quality-gate plugin denies tool paths escaping the project
# ---------------------------------------------------------------------------


class TestE023PluginPathDeny:
    @pytest.mark.parametrize(
        "plugin_path",
        [os.path.abspath(_ACTIVE_PLUGIN), os.path.abspath(_TEMPLATE_PLUGIN)],
    )
    def test_e023_plugin_denies_tool_path_env(self, plugin_path):
        assert os.path.isfile(plugin_path), plugin_path
        src = open(plugin_path, encoding="utf-8").read()
        # Directory traversal (`../.env`) is refused before any tool runs.
        assert 'filePath.includes("..")' in src, "traversal check missing"
        # `.env` (and friends) sit on the sensitive-pattern deny list.
        assert '".env"' in src
        assert "Sensitive file pattern" in src
        # Symlink-escape detection present (dotfile-escape port).
        assert "Symlink escape" in src
        # Control characters (NUL/newline) rejected.
        assert "Control characters" in src

    def test_e023_validator_equivalent_denies_env_traversal(self, tmp_path):
        from ockit.validators import validate_path_safety

        assert validate_path_safety("../.env", str(tmp_path)) is False
        assert validate_path_safety(".env", str(tmp_path)) is False


# ---------------------------------------------------------------------------
# E-025 — scale: 500 SPEC files verify completes within NFR
# ---------------------------------------------------------------------------


class TestE025Scale:
    def test_e025_500_specs_verify_within_nfr(self, tmp_path):
        write(
            tmp_path / "plans" / "SPEC_TEMPLATE.md",
            """# SPEC\n### 1.2 Requirement Traceability Matrix (RTM)\n| Req ID | Unit Test Reference |\n|---|---|\n| R-001 | t::x |\n### 6.2 Edge Case Matrix\n## 8. 3-State Verification\n""",
        )
        for i in range(500):
            write(
                tmp_path / "plans" / f"SPEC_bulk_{i:03d}.md",
                """# SPEC bulk\n### 1.2 Requirement Traceability Matrix (RTM)\n| Req ID | Unit Test Reference |\n|---|---|\n| R-001 | t::x |\n### 6.2 Edge Case Matrix\n""",
            )
        start = time.monotonic()
        report = run_verify(suite="traceability", project_root=str(tmp_path))
        elapsed = time.monotonic() - start
        assert report.exit_code == 0, report.findings
        # NFR-001 floor is < 2s for ≤20 SPECs; generous 10s budget for 500.
        assert elapsed < 10.0, f"verify too slow for 500 SPECs: {elapsed:.2f}s"


# ---------------------------------------------------------------------------
# E-028 — resource leak: WorktreeManager cleans up on subprocess failure
# ---------------------------------------------------------------------------


class TestE028WorktreeCleanup:
    def test_e028_worktree_exception_cleans_up(self, tmp_path, monkeypatch):
        import subprocess
        import tempfile

        # Unique run_id so stale dirs from earlier test runs cannot pollute.
        run_id = f"r1-{os.getpid()}-{time.time_ns()}"
        wt = WorktreeManager(project_root=str(tmp_path), run_id=run_id)

        def failing_run(cmd, **kwargs):  # noqa: ARG001
            # Simulate `git worktree add` failing after mkdtemp succeeded.
            raise subprocess.CalledProcessError(128, cmd)

        monkeypatch.setattr(subprocess, "run", failing_run)
        with pytest.raises(subprocess.CalledProcessError):
            wt.create_isolated_worktree("feat")

        # No leaked worktree temp dirs remain.
        leaks = list(pathlib.Path(tempfile.gettempdir()).glob(f"ockit-wt-{run_id}-*"))
        assert leaks == [], f"worktree temp dirs leaked: {leaks}"


# ---------------------------------------------------------------------------
# E-001 / E-032 — CLI-level actionable failures (missing packaged templates)
# ---------------------------------------------------------------------------


class TestCliMissingTemplates:
    def _run(self, monkeypatch, *argv):
        monkeypatch.setattr(sys, "argv", ["ockit", *argv])
        return pytest.raises(SystemExit)

    def test_e001_cli_init_missing_templates_exit1_actionable(
        self, tmp_path, monkeypatch, capsys
    ):
        # No packaged templates reachable → init must exit 1 with an
        # actionable reinstall hint, not a raw traceback.
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            cli, "_templates_dir", lambda: str(tmp_path / "missing-templates")
        )
        with self._run(monkeypatch, "init", "--target", "proj") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        out = captured.out + captured.err
        assert "reinstall" in out.lower() or "templates" in out.lower()
        assert "Traceback" not in out

    def test_e032_cli_sync_missing_templates_exit1_actionable(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".opencode").mkdir()
        monkeypatch.setattr(
            sync_mod, "_DEFAULT_TEMPLATES_DIR", str(tmp_path / "missing-templates")
        )
        with self._run(monkeypatch, "sync") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        out = captured.out + captured.err
        assert "reinstall" in out.lower() or "templates" in out.lower()
        assert "Traceback" not in out
