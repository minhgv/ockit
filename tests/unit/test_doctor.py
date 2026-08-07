"""
test_doctor.py — Unit tests for ockit doctor diagnostics (R-013, R-023, E-027)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest

import pytest

from ockit.doctor import _run_probe, run_doctor


def write(path, content):
    path = os.fspath(path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


class TestDoctor(unittest.TestCase):
    def setUp(self):
        self.temp_root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_doctor_missing_opencode(self):
        res = run_doctor(project_root=self.temp_root)
        self.assertTrue(res["git_installed"])
        self.assertIn(".opencode/agent directory missing", res["errors"])
        self.assertIn(".opencode/skill directory missing", res["errors"])

    def test_r023_inventory_is_five_custom_agents(self):
        # D5: explore/general/compaction dropped from required custom agents
        opencode = os.path.join(self.temp_root, ".opencode")
        os.makedirs(os.path.join(opencode, "agent"))
        for name in ["orchestrator", "planner", "coder", "reviewer", "qa"]:
            write(
                os.path.join(opencode, "agent", f"{name}.md"),
                f"---\nname: {name}\ndescription: d\nmode: {'primary' if name == 'orchestrator' else 'subagent'}\n---\nbody\n",
            )
        write(os.path.join(opencode, "plugin", "ockit-quality-gate.js"), "export {}\n")
        write(os.path.join(opencode, "command", "plan.md"), "# plan\n")
        write(
            os.path.join(opencode, "opencode.json"), '{"provider": {}, "agent": {}}\n'
        )
        write(os.path.join(self.temp_root, "AGENTS.md"), "# AGENTS\n")
        res = run_doctor(project_root=self.temp_root)
        self.assertTrue(res["agents_valid"])
        self.assertFalse(any("compaction" in e for e in res["errors"]))
        self.assertFalse(any("explore" in e for e in res["errors"]))

    def test_r013_agents_md_missing_error(self):
        res = run_doctor(project_root=self.temp_root)
        self.assertFalse(res["agents_md_present"])
        self.assertTrue(any("AGENTS.md" in e for e in res["errors"]))

    def test_r013_agents_md_present_ok(self):
        write(os.path.join(self.temp_root, "AGENTS.md"), "# AGENTS\n")
        res = run_doctor(project_root=self.temp_root)
        self.assertTrue(res["agents_md_present"])

    def test_r013_invalid_opencode_json_error(self):
        write(os.path.join(self.temp_root, ".opencode", "opencode.json"), "{invalid")
        res = run_doctor(project_root=self.temp_root)
        self.assertFalse(res["config_json_valid"])
        self.assertTrue(any("invalid JSON" in e for e in res["errors"]))

    def test_r013_agent_frontmatter_bad_mode_error(self):
        opencode = os.path.join(self.temp_root, ".opencode")
        os.makedirs(os.path.join(opencode, "agent"))
        write(
            os.path.join(opencode, "agent", "planner.md"),
            "---\nname: planner\ndescription: d\nmode: all\n---\nbody\n",
        )
        res = run_doctor(project_root=self.temp_root)
        self.assertFalse(res["agent_modes_valid"])
        self.assertTrue(any("mode" in e for e in res["errors"]))

    def test_r013_agent_frontmatter_missing_key_error(self):
        opencode = os.path.join(self.temp_root, ".opencode")
        os.makedirs(os.path.join(opencode, "agent"))
        write(os.path.join(opencode, "agent", "planner.md"), "# no frontmatter\n")
        res = run_doctor(project_root=self.temp_root)
        self.assertFalse(res["agent_modes_valid"])
        self.assertTrue(any("frontmatter" in e.lower() for e in res["errors"]))

    def test_r013_agent_frontmatter_valid(self):
        opencode = os.path.join(self.temp_root, ".opencode")
        os.makedirs(os.path.join(opencode, "agent"))
        write(
            os.path.join(opencode, "agent", "planner.md"),
            "---\nname: planner\ndescription: d\nmode: subagent\n---\nbody\n",
        )
        res = run_doctor(project_root=self.temp_root)
        self.assertTrue(res["agent_modes_valid"])

    def test_e027_probe_timeout_is_enforced(self):
        with pytest.raises(subprocess.TimeoutExpired):
            _run_probe(
                ["python3", "-c", "import time; time.sleep(10)"],
                timeout=0.1,
                label="sleep",
            )

    def test_e027_doctor_runs_without_zombies(self):
        res = run_doctor(project_root=self.temp_root)
        self.assertIn("python_version", res)
        self.assertTrue(res["python_version"].startswith("Python"))


if __name__ == "__main__":
    unittest.main()
