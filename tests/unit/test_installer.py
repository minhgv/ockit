"""
test_installer.py — Unit tests for ockit project scaffolder installer
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

import pytest

from ockit import __file__ as ockit_init_file
from ockit.installer import OckitInstaller


def _make_template_tree(root, extra_files=None):
    """Build a small template tree resembling the packaged layout."""
    (root / "agent").mkdir(parents=True, exist_ok=True)
    (root / "skill" / "ba-expert").mkdir(parents=True, exist_ok=True)
    (root / "plugin").mkdir(exist_ok=True)
    (root / "command").mkdir(exist_ok=True)
    (root / "agent" / "planner.md").write_text("# Dummy Planner", encoding="utf-8")
    (root / "skill" / "ba-expert" / "SKILL.md").write_text(
        "# Dummy BA Skill", encoding="utf-8"
    )
    (root / "opencode.json").write_text('{"agent": {}}', encoding="utf-8")
    (root / "AGENTS.md").write_text(
        "# AGENTS.md — ockit scaffold template", encoding="utf-8"
    )
    for rel in extra_files or []:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content:{rel}", encoding="utf-8")
    return root


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.temp_templates = tempfile.mkdtemp()
        self.temp_target = tempfile.mkdtemp()
        self._old_cwd = os.getcwd()
        # resolve_safe_target uses cwd as the safe root; run from the target dir
        os.chdir(self.temp_target)

        # Create dummy template structure
        os.makedirs(os.path.join(self.temp_templates, "agent"))
        os.makedirs(os.path.join(self.temp_templates, "skill", "ba-expert"))
        with open(os.path.join(self.temp_templates, "agent", "planner.md"), "w") as f:
            f.write("# Dummy Planner")
        with open(
            os.path.join(self.temp_templates, "skill", "ba-expert", "SKILL.md"), "w"
        ) as f:
            f.write("# Dummy BA Skill")

    def tearDown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.temp_templates, ignore_errors=True)
        shutil.rmtree(self.temp_target, ignore_errors=True)

    def test_installer_scaffold(self):
        installer = OckitInstaller(templates_dir=self.temp_templates)
        res = installer.initialize_project(target_dir=self.temp_target)

        self.assertEqual(res["status"], "success")
        self.assertTrue(
            os.path.exists(
                os.path.join(self.temp_target, ".opencode", "agent", "planner.md")
            )
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.temp_target, ".opencode", "skill", "ba-expert", "SKILL.md"
                )
            )
        )


# ---------------------------------------------------------------------------
# R-004 — templates packaged inside ockit package (no repo-checkout dependency)
# ---------------------------------------------------------------------------


class TestTemplatesPackaging:
    def test_r004_templates_resolve_from_package(self):
        pkg_dir = os.path.dirname(os.path.abspath(ockit_init_file))
        templates_dir = os.path.join(pkg_dir, "templates")
        assert os.path.isdir(templates_dir)
        assert os.path.isfile(os.path.join(templates_dir, "opencode.json"))
        assert os.path.isfile(os.path.join(templates_dir, "AGENTS.md"))
        assert os.path.isdir(os.path.join(templates_dir, "agent"))
        assert os.path.isdir(os.path.join(templates_dir, "command"))
        assert os.path.isdir(os.path.join(templates_dir, "plugin"))
        assert os.path.isdir(os.path.join(templates_dir, "skill"))

    def test_r004_old_templates_location_removed(self):
        # No dual source of truth: src/templates must be gone
        pkg_dir = os.path.dirname(os.path.abspath(ockit_init_file))
        old_location = os.path.join(os.path.dirname(pkg_dir), "templates")
        assert not os.path.exists(old_location)

    def test_r004_installer_defaults_to_package_templates(self):
        installer = OckitInstaller()
        assert os.path.isdir(installer.templates_dir)
        assert os.path.abspath(installer.templates_dir) == os.path.join(
            os.path.dirname(os.path.abspath(ockit_init_file)), "templates"
        )

    def test_r009_root_agents_md_exists(self):
        # ockit repo itself carries a root AGENTS.md (R-009)
        repo_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(ockit_init_file)))
        )
        root_agents = os.path.join(repo_root, "AGENTS.md")
        assert os.path.isfile(root_agents)
        with open(root_agents, encoding="utf-8") as fh:
            assert "ockit" in fh.read().lower()


# ---------------------------------------------------------------------------
# R-005 / R-007 / R-009 / R-022 — install() behavior
# ---------------------------------------------------------------------------


@pytest.fixture
def chdir_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestInstall:
    def test_r005_installs_tree_and_returns_result(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        res = installer.install(target="proj", lang="python")

        assert res["status"] == "success"
        assert res["target_dir"] == str((tmp_path / "proj").resolve())
        assert res["opencode_dir"] == str((tmp_path / "proj" / ".opencode").resolve())
        assert (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").exists()
        assert (
            tmp_path / "proj" / ".opencode" / "skill" / "ba-expert" / "SKILL.md"
        ).exists()
        assert (tmp_path / "proj" / ".opencode" / "opencode.json").exists()
        assert "agent/planner.md" in res["copied_files"]
        assert "skill/ba-expert/SKILL.md" in res["copied_files"]
        assert res["skipped_files"] == []

    def test_r005_dry_run_writes_nothing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        res = installer.install(target="proj", lang="python", dry_run=True)

        assert res["status"] == "dry_run"
        assert not (tmp_path / "proj").exists()
        # dry run still reports what WOULD be copied
        assert len(res["copied_files"]) >= 4
        assert "agent/planner.md" in res["copied_files"]

    def test_r005_without_force_skips_existing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        installer.install(target="proj", lang="python")

        (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").write_text(
            "USER EDITED", encoding="utf-8"
        )

        res = installer.install(target="proj", lang="python", force=False)
        assert res["status"] == "success"
        # existing files preserved, not overwritten
        assert (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "USER EDITED"
        assert len(res["copied_files"]) == 0
        assert len(res["skipped_files"]) >= 4

    def test_r005_force_overwrites_and_creates_backup(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        installer.install(target="proj", lang="python")

        (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").write_text(
            "USER EDITED", encoding="utf-8"
        )
        (tmp_path / "proj" / "AGENTS.md").write_text("USER AGENTS", encoding="utf-8")

        res = installer.install(target="proj", lang="python", force=True)
        assert res["status"] == "success"

        # overwritten with template content
        assert (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "# Dummy Planner"
        # E-024: backup dir created containing originals
        backups = list((tmp_path / "proj").glob(".opencode.bak-*"))
        assert len(backups) == 1
        backup = backups[0]
        assert (backup / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "USER EDITED"
        assert (backup / "AGENTS.md").read_text(encoding="utf-8") == "USER AGENTS"

    def test_r005_force_no_existing_files_no_backup(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        res = installer.install(target="proj", lang="python", force=True)
        assert res["status"] == "success"
        assert not list((tmp_path / "proj").glob(".opencode.bak-*"))

    def test_r005_skips_junk_dotfiles(self, tmp_path, monkeypatch):
        # E-026: .DS_Store and __pycache__ must not be copied
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(
            tmp_path / "templates",
            extra_files=["agent/.DS_Store", "skill/ba-expert/__pycache__/x.pyc"],
        )
        installer = OckitInstaller(templates_dir=str(templates))
        installer.install(target="proj", lang="python")
        assert not (tmp_path / "proj" / ".opencode" / "agent" / ".DS_Store").exists()
        assert not (
            tmp_path / "proj" / ".opencode" / "skill" / "ba-expert" / "__pycache__"
        ).exists()

    def test_r007_idempotent_rerun(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        first = installer.install(target="proj", lang="python")
        assert first["status"] == "success"
        assert len(first["copied_files"]) >= 4

        second = installer.install(target="proj", lang="python")
        assert second["status"] == "success"
        assert second["copied_files"] == []
        assert len(second["skipped_files"]) == len(first["copied_files"])
        # nothing overwritten on second run
        assert (tmp_path / "proj" / "AGENTS.md").read_text(encoding="utf-8") == (
            tmp_path / "templates" / "AGENTS.md"
        ).read_text(encoding="utf-8")

    def test_r009_agents_md_created_in_target(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        installer.install(target="proj", lang="python")
        agents_md = tmp_path / "proj" / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text(encoding="utf-8")
        assert "ockit" in content.lower()

    def test_r022_partial_init_rerun_completes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(
            tmp_path / "templates",
            extra_files=["command/plan.md", "command/gate.md"],
        )
        installer = OckitInstaller(templates_dir=str(templates))

        # Simulate a partial/interrupted first init: some files already present
        partial = tmp_path / "proj" / ".opencode"
        (partial / "agent").mkdir(parents=True, exist_ok=True)
        (partial / "agent" / "planner.md").write_text("partial", encoding="utf-8")

        res = installer.install(target="proj", lang="python")
        assert res["status"] == "success"
        # existing partial file skipped, missing files completed
        assert (tmp_path / "proj" / ".opencode" / "agent" / "planner.md").read_text(
            encoding="utf-8"
        ) == "partial"
        assert (
            tmp_path / "proj" / ".opencode" / "skill" / "ba-expert" / "SKILL.md"
        ).exists()
        assert (tmp_path / "proj" / ".opencode" / "command" / "plan.md").exists()
        assert (tmp_path / "proj" / ".opencode" / "command" / "gate.md").exists()
        assert (tmp_path / "proj" / "AGENTS.md").exists()

    def test_r022_no_tmp_leftovers_after_install(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        installer.install(target="proj", lang="python")
        leftovers = list((tmp_path / "proj").rglob(".ockit-tmp-*"))
        assert leftovers == []

    def test_e001_missing_templates_error_actionable(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        installer = OckitInstaller(templates_dir=str(tmp_path / "does-not-exist"))
        with pytest.raises(ValueError, match="templates"):
            installer.install(target="proj", lang="python")

    def test_install_rejects_unsafe_target(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        templates = _make_template_tree(tmp_path / "templates")
        installer = OckitInstaller(templates_dir=str(templates))
        with pytest.raises(ValueError, match="unsafe target"):
            installer.install(target="../escape", lang="python")


if __name__ == "__main__":
    unittest.main()
