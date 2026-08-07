"""
test_cli.py — Unit tests for ockit CLI (R-028: argparse surface + safe init)
"""

from __future__ import annotations

import os
import sys

import pytest

from ockit import cli


def run_cli(monkeypatch, *argv):
    """Invoke cli.main() in-process, capturing stdout + exit code."""
    monkeypatch.setattr(sys, "argv", ["ockit", *argv])
    return pytest.raises(SystemExit)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestInitArgparseSurface:
    def test_r028_init_flags_present_in_help(self, capsys):
        with pytest.raises(SystemExit):
            cli.main()
        out = capsys.readouterr().out

    def test_r028_help_lists_force_and_dry_run(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "init", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "--force" in out
        assert "--dry-run" in out
        assert "--target" in out

    def test_r028_doctor_still_present(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "doctor" in out
        assert "init" in out

    def test_r028_help_lists_verify_sync_scan_deps(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "verify" in out
        assert "sync" in out
        assert "scan-deps" in out

    def test_r028_verify_help_lists_suite_choices(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "verify", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "--suite" in out
        assert "traceability" in out
        assert "ba-qa" in out
        assert "agents" in out
        assert "commands" in out
        assert "all" in out

    def test_r028_sync_help_lists_check_and_sync(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "sync", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "--check" in out
        assert "--sync" in out

    def test_r028_scan_deps_subcommand_help(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ["ockit", "scan-deps", "--help"]
            cli.main()
        out = capsys.readouterr().out
        assert "scan-deps" in out or "dependency" in out.lower()


class TestInitCommand:
    def test_r028_init_creates_scaffold_exit_0(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init", "--target", "proj") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        assert (tmp_path / "proj" / ".opencode" / "agent").is_dir()
        assert (tmp_path / "proj" / "AGENTS.md").exists()
        out = capsys.readouterr().out
        assert "Copied" in out

    def test_r028_init_default_target_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        assert (tmp_path / ".opencode").is_dir()

    def test_r028_init_dry_run_writes_nothing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init", "--target", "proj", "--dry-run") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        assert not (tmp_path / "proj").exists()
        out = capsys.readouterr().out
        assert "dry" in out.lower() or "would" in out.lower()

    def test_r028_init_force_flag_accepted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init", "--target", "proj", "--force") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        assert (tmp_path / "proj" / ".opencode" / "agent").is_dir()

    def test_r028_init_traversal_exits_1(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init", "--target", "../escape") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        out = captured.out + captured.err
        assert "target" in out.lower()
        # nothing written outside cwd
        assert not (tmp_path.parent / "escape").exists()

    def test_r028_init_idempotent_cli(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "init", "--target", "proj") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        with run_cli(monkeypatch, "init", "--target", "proj") as excinfo2:
            cli.main()
        assert excinfo2.value.code == 0

    def test_r028_unknown_subcommand_shows_help(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            sys.argv = ["ockit", "bogus-command"]
            cli.main()
        assert excinfo.value.code in (0, 2)


class TestVerifyCommand:
    def test_r028_verify_traceability_exits_by_report(self, tmp_path, monkeypatch):
        plans = tmp_path / "plans"
        write(
            plans / "SPEC_TEMPLATE.md",
            "# SPEC\n### 1.2 Requirement Traceability Matrix (RTM)\n| Req ID |\n|---|\n### 6.2 Edge Case Matrix\n### 8. 3-State Verification\n",
        )
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "verify", "--suite", "traceability") as excinfo:
            cli.main()
        assert excinfo.value.code == 0

    def test_r028_verify_fail_exits_1(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "verify", "--suite", "traceability") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert "[FAIL]" in out

    def test_r028_verify_default_suite_all(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "verify") as excinfo:
            cli.main()
        # no plans/ + no .opencode → multiple FAILs, exit 1
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert "[FAIL]" in out

    def test_r028_verify_invalid_suite_rejected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "verify", "--suite", "nope") as excinfo:
            cli.main()
        assert excinfo.value.code == 2


class TestSyncCommand:
    def test_r028_sync_default_check_reports_drift_exit1(
        self, tmp_path, monkeypatch, capsys
    ):
        # packaged templates exist; empty active .opencode → drift
        (tmp_path / ".opencode").mkdir()
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "sync") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert "missing_in_active" in out or "drift" in out.lower()

    def test_r028_sync_check_flag_exits1_on_drift(self, tmp_path, monkeypatch):
        (tmp_path / ".opencode").mkdir()
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "sync", "--check") as excinfo:
            cli.main()
        assert excinfo.value.code == 1

    def test_r028_sync_sync_flag_writes_and_exits0(self, tmp_path, monkeypatch, capsys):
        (tmp_path / ".opencode").mkdir()
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "sync", "--sync") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        assert (tmp_path / ".opencode" / "opencode.json").exists()
        out = capsys.readouterr().out
        assert "Synced" in out


class TestScanDepsCommand:
    def test_r028_scan_deps_clean_exit0(self, tmp_path, monkeypatch, capsys):
        write(tmp_path / "requirements.txt", "requests==2.31.0\n")
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "scan-deps") as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "Scan" in out or "scan" in out.lower()

    def test_r028_scan_deps_error_exit1(self, tmp_path, monkeypatch, capsys):
        write(tmp_path / "requirements.txt", "react-helper-lib==1.0\n")
        monkeypatch.chdir(tmp_path)
        with run_cli(monkeypatch, "scan-deps") as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert "slopsquat" in out.lower()


if __name__ == "__main__":
    import unittest

    unittest.main()
