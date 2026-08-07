"""
test_agents_frontmatter.py — Agent mode & clobber-audit tests (R-008)

Verifies both the live ``.opencode/agent/`` tree and the packaged
``src/ockit/templates/agent/`` tree ship exactly the post-nativization agent
set: orchestrator (mode: primary) + planner/coder/reviewer/qa (mode: subagent),
with no built-in clobber files (explore/general/compaction) and no ``mode: all``.
"""

from __future__ import annotations

import os

import pytest

from ockit import __file__ as ockit_init_file
from ockit.verify import parse_frontmatter

_PKG_DIR = os.path.dirname(os.path.abspath(ockit_init_file))
_TEMPLATES_AGENT = os.path.join(_PKG_DIR, "templates", "agent")
_ACTIVE_AGENT = os.path.join(os.path.dirname(_PKG_DIR), "..", ".opencode", "agent")

CLOBBER_NAMES = {"explore", "general", "compaction"}


def _agent_dirs():
    return [_TEMPLATES_AGENT, os.path.abspath(_ACTIVE_AGENT)]


def test_agent_dirs_exist():
    for d in _agent_dirs():
        assert os.path.isdir(d), f"agent dir missing: {d}"


@pytest.mark.parametrize("agents_dir", _agent_dirs())
def test_no_builtin_clobber_files(agents_dir):
    files = {f for f in os.listdir(agents_dir) if f.endswith(".md")}
    assert not (files & {f"{n}.md" for n in CLOBBER_NAMES}), (
        f"built-in clobber agents shipped in {agents_dir}"
    )


@pytest.mark.parametrize("agents_dir", _agent_dirs())
def test_expected_agent_inventory(agents_dir):
    files = sorted(f for f in os.listdir(agents_dir) if f.endswith(".md"))
    assert files == [
        "coder.md",
        "orchestrator.md",
        "planner.md",
        "qa.md",
        "reviewer.md",
    ]


@pytest.mark.parametrize("agents_dir", _agent_dirs())
def test_all_modes_valid_and_no_mode_all(agents_dir):
    for filename in os.listdir(agents_dir):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(agents_dir, filename)
        data = parse_frontmatter(open(path, encoding="utf-8").read())
        assert data.get("name"), f"{filename} missing frontmatter key 'name'"
        assert data.get("description"), (
            f"{filename} missing frontmatter key 'description'"
        )
        assert data.get("mode"), f"{filename} missing frontmatter key 'mode'"
        assert data["mode"] in ("primary", "subagent"), (
            f"{filename} has invalid mode '{data['mode']}'"
        )


@pytest.mark.parametrize("agents_dir", _agent_dirs())
def test_orchestrator_primary_others_subagent(agents_dir):
    expected = {
        "orchestrator.md": "primary",
        "planner.md": "subagent",
        "coder.md": "subagent",
        "reviewer.md": "subagent",
        "qa.md": "subagent",
    }
    for filename, mode in expected.items():
        path = os.path.join(agents_dir, filename)
        data = parse_frontmatter(open(path, encoding="utf-8").read())
        assert data.get("mode") == mode, (
            f"{filename} expected mode '{mode}', got '{data.get('mode')}'"
        )
