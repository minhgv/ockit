"""
test_scan_deps.py — Unit tests for ockit scan-deps supply chain scanner (R-012)
"""

from __future__ import annotations

import pytest

from ockit.scan_deps import ScanDepsReport, run_scan_deps


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestScanDeps:
    def test_r012_no_dependency_files_ok(self, tmp_path):
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.errors == []
        assert report.scanned_files == []

    def test_r012_clean_requirements_ok(self, tmp_path):
        write(tmp_path / "requirements.txt", "requests==2.31.0\nflask==3.0.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.scanned_files == ["requirements.txt"]

    def test_r012_e020_slopsquat_in_requirements_fails(self, tmp_path):
        write(
            tmp_path / "requirements.txt",
            "requests==2.31.0\nreact-helper-lib==1.0.0\n",
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 1
        assert report.errors
        assert any("slopsquat" in e.lower() for e in report.errors)
        assert any("react-helper-lib" in e for e in report.errors)

    def test_r012_slopsquat_case_insensitive(self, tmp_path):
        write(tmp_path / "requirements.txt", "Python-Crypto==1.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 1

    def test_r012_slopsquat_in_go_lockfile_fails(self, tmp_path):
        write(tmp_path / "go.mod", "module demo\nrequire langchain-core-plus v0.1.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any("go.mod" in e for e in report.errors)

    def test_r012_slopsquat_in_package_json_fails(self, tmp_path):
        write(
            tmp_path / "package.json",
            '{"dependencies": {"flask-utils-v2": "1.0.0"}}\n',
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 1

    def test_r012_unpinned_requirements_warn_not_fail(self, tmp_path):
        write(tmp_path / "requirements.txt", "requests\nflask==3.0.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.warnings
        assert any("unpinned" in w.lower() for w in report.warnings)
        assert "requests" in report.warnings[0]

    def test_r012_loose_pin_warns(self, tmp_path):
        write(tmp_path / "requirements.txt", "requests>=0.0.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert any("unpinned" in w.lower() for w in report.warnings)

    def test_r012_pinned_all_clean(self, tmp_path):
        write(
            tmp_path / "requirements.txt",
            "requests==2.31.0\nflask>=3.0,<4.0\nclick~=8.1\n",
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.warnings == []
        assert report.exit_code == 0

    def test_r012_insecure_http_url_fails(self, tmp_path):
        write(
            tmp_path / "requirements.txt",
            "requests==2.31.0\n--index-url http://pypi.example.com/simple\n",
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 1
        assert any("http://" in e for e in report.errors)

    def test_r012_http_localhost_allowed(self, tmp_path):
        write(
            tmp_path / "requirements.txt",
            "requests==2.31.0\n--index-url http://localhost:8080/simple\n",
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0

    def test_r012_package_json_unpinned_range_warns(self, tmp_path):
        write(
            tmp_path / "package.json",
            '{"dependencies": {"react": "^18.2.0", "lodash": "4.17.21"}}\n',
        )
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert any("unpinned" in w.lower() and "react" in w for w in report.warnings)

    def test_r012_skips_junk_dirs(self, tmp_path):
        write(
            tmp_path / "node_modules" / "pkg" / "package.json", '{"dependencies": {}}\n'
        )
        write(tmp_path / ".venv" / "requirements.txt", "react-helper-lib==1.0\n")
        write(tmp_path / "requirements.txt", "requests==2.31.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert report.scanned_files == ["requirements.txt"]

    def test_r012_recursive_scan_finds_subdir_deps(self, tmp_path):
        write(tmp_path / "sub" / "project" / "requirements.txt", "requests==2.31.0\n")
        report = run_scan_deps(project_root=str(tmp_path))
        assert report.exit_code == 0
        assert "sub/project/requirements.txt" in report.scanned_files

    def test_r012_report_shape(self):
        report = ScanDepsReport(errors=["e"], warnings=["w"], scanned_files=["f"])
        assert report.exit_code == 1
        ok = ScanDepsReport(errors=[], warnings=["w"], scanned_files=["f"])
        assert ok.exit_code == 0
