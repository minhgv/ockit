"""
validators.py — Path safety, traversal, and boundary security validators for ockit
"""

from __future__ import annotations

import os
from pathlib import Path

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


def is_within(base: Path, child: Path) -> bool:
    """
    True when ``child`` resolves inside (or equal to) ``base``.

    Both paths are fully resolved (symlinks + ``..``) before comparison, so a
    symlink that points outside ``base`` is correctly reported as outside.
    """
    try:
        base_resolved = str(base.resolve(strict=False))
        child_resolved = str(child.resolve(strict=False))
        return os.path.commonpath([base_resolved, child_resolved]) == base_resolved
    except ValueError:
        # Different drives (Windows) or other commonpath failures → not contained
        return False


def resolve_safe_target(target: str) -> Path:
    """
    Canonicalizes a CLI ``--target`` and verifies it stays within the safe root (cwd).

    Guards:
    - NUL / newline / carriage-return characters in the raw string.
    - Path traversal (``..`` / absolute paths escaping cwd).
    - Symlink escape (a resolved symlink pointing outside cwd).

    Raises ValueError with a What / Context / Fix message on any violation.
    """
    if not isinstance(target, str):
        raise ValueError(
            "What=invalid target type; "
            f"Context=expected str, got {type(target).__name__}; "
            "Fix=pass a plain directory path"
        )
    target = target.strip()
    if not target:
        raise ValueError(
            "What=empty target; "
            "Context=target string is blank; "
            "Fix=pass a non-empty directory path"
        )
    if "\x00" in target or "\n" in target or "\r" in target:
        raise ValueError(
            "What=invalid target; "
            "Context=NUL or newline character present in path; "
            "Fix=pass a plain directory path"
        )

    safe_root = Path.cwd().resolve()
    raw_abs = Path(os.path.abspath(target))
    resolved = raw_abs.resolve(strict=False)

    if not is_within(safe_root, resolved):
        raise ValueError(
            "What=unsafe target path; "
            f"Context=resolved target '{resolved}' escapes safe root "
            f"'{safe_root}' (traversal or symlink escape); "
            "Fix=choose a target directory inside the current working directory"
        )
    return resolved


def validate_target_arg(target: str) -> str:
    """
    CLI pre-validation hook: validates ``target`` and returns the canonical
    absolute path string (already symlink/``..``-resolved).
    """
    return str(resolve_safe_target(target))
