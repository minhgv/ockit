"""
test_validators.py — Unit tests for ockit path safety validators
"""

from __future__ import annotations

import os
import unittest

import pytest

from ockit.validators import (
    is_within,
    resolve_safe_target,
    validate_path_safety,
    validate_target_arg,
)


class TestValidators(unittest.TestCase):
    def test_valid_path(self):
        self.assertTrue(validate_path_safety("src/main.py", "/tmp"))

    def test_path_traversal(self):
        self.assertFalse(validate_path_safety("../etc/passwd", "/tmp"))

    def test_sensitive_files(self):
        self.assertFalse(validate_path_safety(".env", "/tmp"))
        self.assertFalse(validate_path_safety(".ssh/id_rsa", "/tmp"))


# ---------------------------------------------------------------------------
# R-006 — resolve_safe_target / is_within / validate_target_arg
# ---------------------------------------------------------------------------


class TestResolveSafeTarget:
    """R-006: path-safe target resolution (E-005, E-006, E-007, E-021)."""

    def test_relative_target_resolves_inside_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = resolve_safe_target("proj")
        assert result == (tmp_path / "proj").resolve()

    def test_dot_target_is_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = resolve_safe_target(".")
        assert result == tmp_path.resolve()

    def test_dotdot_canonicalized_to_single_dest(self, tmp_path, monkeypatch):
        # E-005: ./a/../a collapses to a single resolved destination
        monkeypatch.chdir(tmp_path)
        (tmp_path / "a").mkdir()
        result = resolve_safe_target("./a/../a")
        assert result == (tmp_path / "a").resolve()

    def test_traversal_denied(self, tmp_path, monkeypatch):
        # E-021: `..` escape outside safe root rejected
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="unsafe target"):
            resolve_safe_target("../escape")

    def test_absolute_path_outside_cwd_denied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="unsafe target"):
            resolve_safe_target("/etc")

    def test_symlink_escape_denied(self, tmp_path, monkeypatch):
        # E-006: symlink resolving outside safe root rejected
        monkeypatch.chdir(tmp_path)
        outside = tmp_path.parent / "secret-dir"
        outside.mkdir(exist_ok=True)
        (tmp_path / "evil-link").symlink_to(outside, target_is_directory=True)
        with pytest.raises(ValueError, match="unsafe target"):
            resolve_safe_target("evil-link")

    def test_symlink_within_root_allowed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "real").mkdir()
        (tmp_path / "good-link").symlink_to(tmp_path / "real", target_is_directory=True)
        result = resolve_safe_target("good-link")
        assert result == (tmp_path / "real").resolve()

    def test_unicode_path_ok(self, tmp_path, monkeypatch):
        # E-007: unicode target path resolves fine
        monkeypatch.chdir(tmp_path)
        result = resolve_safe_target("ünïcode-プロジェクト")
        assert result == (tmp_path / "ünïcode-プロジェクト").resolve()

    def test_nul_denied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="NUL|newline|invalid target"):
            resolve_safe_target("bad\x00dir")

    def test_newline_denied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="NUL|newline|invalid target"):
            resolve_safe_target("bad\ndir")

    def test_carriage_return_denied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="NUL|newline|invalid target"):
            resolve_safe_target("bad\rdir")

    def test_empty_target_denied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError):
            resolve_safe_target("   ")

    def test_error_is_actionable_three_dimensional(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        try:
            resolve_safe_target("../escape")
        except ValueError as exc:
            msg = str(exc)
            assert "What=" in msg
            assert "Context=" in msg
            assert "Fix=" in msg
        else:  # pragma: no cover
            pytest.fail("expected ValueError")


class TestValidateTargetArg:
    def test_returns_canonical_str(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = validate_target_arg("proj")
        assert isinstance(result, str)
        assert result == str((tmp_path / "proj").resolve())

    def test_rejects_traversal(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="unsafe target"):
            validate_target_arg("../escape")


class TestIsWithin:
    def test_child_within_base(self, tmp_path):
        assert is_within(tmp_path, tmp_path / "a" / "b") is True

    def test_child_equal_base(self, tmp_path):
        assert is_within(tmp_path, tmp_path) is True

    def test_child_outside_base(self, tmp_path):
        assert is_within(tmp_path, tmp_path.parent) is False

    def test_disjoint_paths(self, tmp_path):
        other = tmp_path.parent / "unrelated"
        assert is_within(tmp_path, other) is False

    def test_symlink_resolved(self, tmp_path):
        (tmp_path / "real").mkdir()
        link = tmp_path / "link"
        link.symlink_to(tmp_path / "real", target_is_directory=True)
        assert is_within(tmp_path, link) is True
        assert is_within(tmp_path, link / ".." / ".." / "etc") is False


if __name__ == "__main__":
    unittest.main()
