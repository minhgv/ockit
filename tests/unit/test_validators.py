"""
test_validators.py — Unit tests for ockit path safety validators
"""
from __future__ import annotations

import unittest
from ockit.validators import validate_path_safety


class TestValidators(unittest.TestCase):

    def test_valid_path(self):
        self.assertTrue(validate_path_safety("src/main.py", "/tmp"))

    def test_path_traversal(self):
        self.assertFalse(validate_path_safety("../etc/passwd", "/tmp"))

    def test_sensitive_files(self):
        self.assertFalse(validate_path_safety(".env", "/tmp"))
        self.assertFalse(validate_path_safety(".ssh/id_rsa", "/tmp"))


if __name__ == "__main__":
    unittest.main()
