"""
test_installer.py — Unit tests for ockit project scaffolder installer
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from ockit.installer import OckitInstaller


class TestInstaller(unittest.TestCase):

    def setUp(self):
        self.temp_templates = tempfile.mkdtemp()
        self.temp_target = tempfile.mkdtemp()

        # Create dummy template structure
        os.makedirs(os.path.join(self.temp_templates, "agents"))
        os.makedirs(os.path.join(self.temp_templates, "skills", "ba-expert"))
        with open(os.path.join(self.temp_templates, "agents", "planner.md"), "w") as f:
            f.write("# Dummy Planner")
        with open(os.path.join(self.temp_templates, "skills", "ba-expert", "SKILL.md"), "w") as f:
            f.write("# Dummy BA Skill")

    def tearDown(self):
        shutil.rmtree(self.temp_templates, ignore_errors=True)
        shutil.rmtree(self.temp_target, ignore_errors=True)

    def test_installer_scaffold(self):
        installer = OckitInstaller(templates_dir=self.temp_templates)
        res = installer.initialize_project(target_dir=self.temp_target)

        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(os.path.join(self.temp_target, ".opencode", "agents", "planner.md")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_target, ".opencode", "skills", "ba-expert", "SKILL.md")))


if __name__ == "__main__":
    unittest.main()
