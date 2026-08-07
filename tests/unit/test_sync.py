"""
test_sync.py — Unit tests for ockit sync drift check/write (R-003, R-021)
"""

from __future__ import annotations

import pytest

from ockit.sync import DriftItem, SyncReport, run_sync


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_templates(root):
    write(root / "agent" / "planner.md", "# planner v1\n")
    write(root / "agent" / "coder.md", "# coder v1\n")
    write(root / "command" / "plan.md", "# plan v1\n")
    write(root / "opencode.json", '{"agent": {}}\n')
    return root


def make_active(root):
    write(root / "agent" / "planner.md", "# planner v1\n")
    write(root / "agent" / "coder.md", "# coder v1\n")
    write(root / "command" / "plan.md", "# plan v1\n")
    write(root / "opencode.json", '{"agent": {}}\n')
    return root


class TestSyncCheck:
    def test_r003_check_no_drift_exit0(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        assert report.mode == "check"
        assert report.drift == []
        assert report.exit_code == 0

    def test_r003_check_content_mismatch(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(active / "agent" / "planner.md", "# planner EDITED\n")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        item = next(i for i in report.drift if i.relative_path == "agent/planner.md")
        assert item.kind == "content_mismatch"
        assert report.exit_code == 1

    def test_r003_check_missing_in_active(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        (active / "opencode.json").unlink()
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        item = next(i for i in report.drift if i.relative_path == "opencode.json")
        assert item.kind == "missing_in_active"
        assert report.exit_code == 1

    def test_r003_check_missing_in_templates(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(active / "agent" / "extra.md", "# extra only in active\n")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        item = next(i for i in report.drift if i.relative_path == "agent/extra.md")
        assert item.kind == "missing_in_templates"
        assert report.exit_code == 1

    def test_r003_e004_empty_templates_exit1(self, tmp_path):
        templates = tmp_path / "templates"
        templates.mkdir()
        active = make_active(tmp_path / "active")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        assert report.exit_code == 1
        assert all(i.kind == "missing_in_templates" for i in report.drift)

    def test_r003_skips_junk(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(active / ".DS_Store", "junk")
        write(active / "agent" / "__pycache__" / "x.pyc", "junk")
        write(templates / ".DS_Store", "junk")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        assert not any(".DS_Store" in i.relative_path for i in report.drift)
        assert not any("__pycache__" in i.relative_path for i in report.drift)
        assert report.exit_code == 0

    def test_r003_ignores_agents_md(self, tmp_path):
        # AGENTS.md is installed to the project ROOT by init (R-009), not into
        # .opencode/ — sync must not report phantom drift for it.
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(templates / "AGENTS.md", "# template AGENTS\n")
        write(active / "AGENTS.md", "# active AGENTS\n")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        assert not any(i.relative_path == "AGENTS.md" for i in report.drift)
        assert report.exit_code == 0

    def test_r021_default_mode_is_check(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        report = run_sync(active_dir=str(active), templates_dir=str(templates))
        assert report.mode == "check"

    def test_e032_missing_templates_dir_error(self, tmp_path):
        active = make_active(tmp_path / "active")
        with pytest.raises(ValueError, match="templates"):
            run_sync(
                active_dir=str(active),
                templates_dir=str(tmp_path / "does-not-exist"),
                mode="check",
            )


class TestSyncWrite:
    def test_r003_sync_copies_and_e017_check_clean(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        # drift: template updated, active has extra local file
        write(templates / "agent" / "coder.md", "# coder v2\n")
        write(active / "agent" / "extra.md", "# local extra\n")

        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="sync"
        )
        assert report.mode == "sync"
        assert "agent/coder.md" in report.synced
        assert report.exit_code == 0
        assert (active / "agent" / "coder.md").read_text(
            encoding="utf-8"
        ) == "# coder v2\n"

        # E-017: sync --check after --sync → template-side drift cleared;
        # the active-only extra file is intentionally NOT deleted and still
        # reported as missing_in_templates.
        report2 = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        remaining = [i.relative_path for i in report2.drift]
        assert remaining == ["agent/extra.md"]
        assert report2.exit_code == 1

    def test_r003_e017_check_clean_when_no_extras(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(templates / "agent" / "coder.md", "# coder v2\n")
        run_sync(active_dir=str(active), templates_dir=str(templates), mode="sync")
        report2 = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="check"
        )
        assert report2.drift == []
        assert report2.exit_code == 0

    def test_r003_sync_does_not_delete_active_extra(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(active / "agent" / "extra.md", "# keep me\n")
        run_sync(active_dir=str(active), templates_dir=str(templates), mode="sync")
        assert (active / "agent" / "extra.md").exists()

    def test_r003_sync_creates_missing_dirs(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        (active / "agent").rmdir() if not list((active / "agent").iterdir()) else None
        import shutil

        shutil.rmtree(active / "agent")
        report = run_sync(
            active_dir=str(active), templates_dir=str(templates), mode="sync"
        )
        assert (active / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "# planner v1\n"
        assert "agent/planner.md" in report.synced

    def test_r003_e031_atomic_write_no_tmp_leftovers(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(templates / "agent" / "planner.md", "# planner v2\n" * 1000)
        run_sync(active_dir=str(active), templates_dir=str(templates), mode="sync")
        leftovers = list(active.rglob(".ockit-tmp-*"))
        assert leftovers == []
        assert (active / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "# planner v2\n" * 1000

    def test_e009_sync_idempotent(self, tmp_path):
        templates = make_templates(tmp_path / "templates")
        active = make_active(tmp_path / "active")
        write(templates / "agent" / "coder.md", "# coder v2\n")
        run_sync(active_dir=str(active), templates_dir=str(templates), mode="sync")
        run_sync(active_dir=str(active), templates_dir=str(templates), mode="sync")
        assert (active / "agent" / "coder.md").read_text(
            encoding="utf-8"
        ) == "# coder v2\n"

    def test_drift_item_and_report_shapes(self):
        item = DriftItem(relative_path="a.md", kind="content_mismatch")
        assert item.relative_path == "a.md"
        report = SyncReport(mode="check", drift=[item])
        assert report.exit_code == 1
        ok = SyncReport(mode="sync", drift=[item])
        assert ok.exit_code == 0


# ---------------------------------------------------------------------------
# R-003: active plugin mirror MUST stay byte-identical to packaged template.
# Sync invariant — applies to all 4 packaged plugins (ockit sync contract).
# ---------------------------------------------------------------------------

_PLUGIN_NAMES = [
    "ockit-ba-traceability.js",
    "ockit-quality-gate.js",
    "ockit-linter-fixer.js",
    "ockit-tdd-runner.js",
]


def test_r003_ba_traceability_active_equals_template():
    """R-003 / E-002: every active plugin file MUST be byte-identical to its
    packaged template mirror (zero sync drift)."""
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    active_dir = repo_root / ".opencode" / "plugin"
    template_dir = repo_root / "src" / "ockit" / "templates" / "plugin"
    for name in _PLUGIN_NAMES:
        active = active_dir / name
        template = template_dir / name
        assert active.exists(), (
            "What=active plugin file missing; "
            f"Context={active}; "
            "Fix=run `ockit sync` or restore the active plugin from packaged template."
        )
        assert template.exists(), (
            "What=packaged plugin template missing; "
            f"Context={template}; "
            "Fix=reinstall ockit (pip install --force-reinstall ockit)."
        )
        assert active.read_bytes() == template.read_bytes(), (
            "What=active plugin diverged from packaged template (sync drift); "
            f"Context=plugin='{name}'; active={active} template={template}; "
            "Fix=run `ockit sync` to mirror template → active (byte-identical)."
        )
