"""
validators.py — Path safety, traversal, and boundary security validators for ockit
"""
from __future__ import annotations

import os

SENSITIVE_PATTERNS = {".env", ".ssh", ".aws", ".gnupg", "id_rsa", "credentials"}


def validate_path_safety(file_path: str, allowlisted_root: str) -> bool:
    """
    Validates that file_path is within allowlisted_root and free of path traversal attempts.
    """
    if not file_path or not allowlisted_root:
        return False

    if not file_path.strip() or os.path.isabs(file_path):
        return False

    if ".." in file_path or file_path.startswith("-") or "\n" in file_path:
        return False

    for pattern in SENSITIVE_PATTERNS:
        if pattern in file_path:
            return False

    try:
        abs_root = os.path.realpath(allowlisted_root)
        abs_file = os.path.realpath(os.path.join(abs_root, file_path))
        return os.path.commonpath([abs_root, abs_file]) == abs_root
    except Exception:  # noqa: BLE001
        return False
