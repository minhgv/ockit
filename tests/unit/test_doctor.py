"""
test_doctor.py — Unit tests for ockit doctor diagnostics
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from ockit.doctor import run_doctor


class TestDoctor(unittest.TestCase):

    def setUp(self):
        self.temp_root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_doctor_missing_opencode(self):
        res = run_doctor(project_root=self.temp_root)
        self.assertTrue(res["git_installed"])
        self.assertIn(".opencode/agents (or .opencode/agent) directory missing", res["errors"])
        self.assertIn(".opencode/skills (or .opencode/skill) directory missing", res["errors"])


if __name__ == "__main__":
    unittest.main()
