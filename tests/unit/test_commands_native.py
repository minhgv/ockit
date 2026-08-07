"""
test_commands_native.py — Command nativization tests (R-015, R-016, R-019)

Verifies both the live ``.opencode/command/`` tree and the packaged
``src/ockit/templates/command/`` tree:
- no dead ``./bin/<script>.sh`` references (R-015)
- ``init.md`` deleted in favor of ``ockit-init.md`` (R-016)
- ``ockit-init.md`` invokes ``!ockit init`` with passthrough
- ``safe-pipeline.md`` carries ``agent: coder`` + ``subtask: true`` and uses
  only ``!ockit verify`` / ``!ockit scan-deps`` (R-019)
"""

from __future__ import annotations

import os
import re

import pytest

from ockit import __file__ as ockit_init_file
from ockit.verify import parse_frontmatter

_PKG_DIR = os.path.dirname(os.path.abspath(ockit_init_file))
_TEMPLATES_CMD = os.path.join(_PKG_DIR, "templates", "command")
_ACTIVE_CMD = os.path.join(os.path.dirname(_PKG_DIR), "..", ".opencode", "command")

# Same policy as verify.py: only thin CI wrappers are ever allowed.
_ALLOWED_WRAPPERS = {
    "validate-traceability.sh",
    "validate-phase10-ba-qa.sh",
    "scan-dependencies.sh",
}
_BIN_REF_RE = re.compile(r"(?:\./)?bin/([A-Za-z0-9_.-]+\.sh)")

EXPECTED_COMMANDS = [
    "brainstorm.md",
    "doctor.md",
    "gate.md",
    "grill.md",
    "learn.md",
    "migrate.md",
    "ockit-init.md",
    "pipeline.md",
    "plan.md",
    "qa.md",
    "review.md",
    "safe-pipeline.md",
    "schedule.md",
    "solve.md",
]

# Appendix A: command → expected !ockit verbs.
APPENDIX_A_VERBS = {
    "doctor.md": ("!ockit doctor",),
    "gate.md": ("!ockit scan-deps", "!ockit verify"),
    "pipeline.md": ("!ockit verify", "!ockit scan-deps"),
    "plan.md": ("!ockit verify",),
    "qa.md": ("!ockit verify",),
    "review.md": ("!ockit verify",),
    "migrate.md": ("!ockit verify --suite agents", "!ockit verify --suite commands"),
    "schedule.md": ("!ockit scan-deps",),
    "safe-pipeline.md": ("!ockit verify", "!ockit scan-deps"),
}


def _cmd_dirs():
    return [_TEMPLATES_CMD, os.path.abspath(_ACTIVE_CMD)]


def test_command_dirs_exist():
    for d in _cmd_dirs():
        assert os.path.isdir(d), f"command dir missing: {d}"


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
def test_expected_command_inventory(cmd_dir):
    files = sorted(f for f in os.listdir(cmd_dir) if f.endswith(".md"))
    assert files == EXPECTED_COMMANDS, f"command inventory drift in {cmd_dir}"


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
def test_no_init_md(cmd_dir):
    assert "init.md" not in os.listdir(cmd_dir), f"init.md must be renamed in {cmd_dir}"


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
def test_no_dead_bin_references(cmd_dir):
    for filename in os.listdir(cmd_dir):
        if not filename.endswith(".md"):
            continue
        content = open(os.path.join(cmd_dir, filename), encoding="utf-8").read()
        for match in _BIN_REF_RE.finditer(content):
            assert match.group(1) in _ALLOWED_WRAPPERS, (
                f"dead bin reference './bin/{match.group(1)}' in '{filename}'"
            )


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
@pytest.mark.parametrize("filename,verbs", APPENDIX_A_VERBS.items())
def test_appendix_a_ockit_verbs_present(cmd_dir, filename, verbs):
    content = open(os.path.join(cmd_dir, filename), encoding="utf-8").read()
    for verb in verbs:
        assert verb in content, f"'{filename}' missing required '!ockit' verb: {verb}"


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
def test_ockit_init_body(cmd_dir):
    content = open(os.path.join(cmd_dir, "ockit-init.md"), encoding="utf-8").read()
    data = parse_frontmatter(content)
    assert data.get("description") == "Initialize ockit scaffold into a target project"
    assert '!ockit init --target "$ARGUMENTS"' in content
    assert "--force" in content and "--dry-run" in content


@pytest.mark.parametrize("cmd_dir", _cmd_dirs())
def test_safe_pipeline_native_subtask(cmd_dir):
    content = open(os.path.join(cmd_dir, "safe-pipeline.md"), encoding="utf-8").read()
    data = parse_frontmatter(content)
    assert data.get("agent") == "coder"
    assert data.get("subtask") in ("true", True), (
        "safe-pipeline.md must declare 'subtask: true'"
    )
    assert "safe-agent-run.sh" not in content
    assert "!ockit verify" in content
    assert "!ockit scan-deps" in content
