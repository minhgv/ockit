"""
sync.py — Drift check & template synchronization for `ockit sync`

Ports agy-kit's ``bin/sync_templates.py`` into Python, comparing the active
``.opencode/`` tree (default cwd) against the packaged ``ockit/templates/``
tree (R-003, R-021). ``--check`` is the safe default (D7): it only reports
drift and exits 1 on drift; ``--sync`` copies templates → active with atomic
per-file writes (E-031).

Source reference: https://github.com/giapminh79/agy-kit/tree/main/bin/sync_templates.py
"""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass, field

# Junk entries skipped when walking both trees (E-026).
_IGNORED_FILES = {".DS_Store"}
_IGNORED_DIRS = {"__pycache__", ".git", "node_modules"}

# ``AGENTS.md`` lives in the packaged tree but is installed to the project
# ROOT by ``ockit init`` (R-009), not into ``.opencode/``. Comparing it against
# ``.opencode/AGENTS.md`` would produce permanent phantom drift, so sync
# excludes it (init owns that contract).
_IGNORED_RELS = {"AGENTS.md"}

_DEFAULT_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)


@dataclass
class DriftItem:
    """A path where active ``.opencode`` content differs from the template."""

    relative_path: str
    kind: str  # "missing_in_templates" | "missing_in_active" | "content_mismatch"


@dataclass
class SyncReport:
    """Structured sync result (SyncReport schema, section 3)."""

    mode: str  # "check" | "sync"
    drift: list[DriftItem] = field(default_factory=list)
    synced: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        # Safe default: check mode fails on any drift; sync mode always 0.
        if self.mode == "check" and self.drift:
            return 1
        return 0


def _walk_rel(root: str) -> set[str]:
    """Relative file paths under ``root``, skipping junk entries (E-026)."""
    rels: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _IGNORED_DIRS]
        for name in filenames:
            if name in _IGNORED_FILES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if rel in _IGNORED_RELS:
                continue
            rels.add(rel)
    return rels


def _atomic_write(src: str, dst: str) -> None:
    """
    Copies ``src`` → ``dst`` atomically: write to a temp file in the same
    directory, then ``os.replace``. A kill mid-copy can only leave an orphan
    ``.ockit-tmp-*`` file, never a corrupt destination (E-031).
    """
    dest_dir = os.path.dirname(dst)
    os.makedirs(dest_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".ockit-tmp-", dir=dest_dir)
    try:
        with os.fdopen(fd, "wb") as fh, open(src, "rb") as sf:
            shutil.copyfileobj(sf, fh)
        shutil.copystat(src, tmp)
        os.replace(tmp, dst)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def run_sync(
    active_dir: str | None = None,
    templates_dir: str | None = None,
    mode: str = "check",
) -> SyncReport:
    """
    Compares active ``.opencode/`` (default cwd/.opencode) against the packaged
    templates tree (R-003).

    DriftItem kinds:
    - ``missing_in_templates`` — file exists in active but not in templates
    - ``missing_in_active`` — file exists in templates but not in active
    - ``content_mismatch`` — file exists in both, content bytes differ

    ``mode="sync"`` copies templates → active for ``missing_in_active`` and
    ``content_mismatch`` items. Active-only files are never deleted (copy
    direction is one-way; templates are the source of truth).

    Raises ValueError with a What/Context/Fix message when the templates tree
    is missing (E-032) or ``mode`` is invalid.
    """
    if mode not in ("check", "sync"):
        raise ValueError(
            f"What=invalid sync mode; Context=got '{mode}', expected 'check' or 'sync'; "
            "Fix=pass --check (default) or --sync"
        )

    active = (
        os.path.abspath(active_dir)
        if active_dir
        else os.path.join(os.getcwd(), ".opencode")
    )
    templates = (
        os.path.abspath(templates_dir) if templates_dir else _DEFAULT_TEMPLATES_DIR
    )

    if not os.path.isdir(templates):
        raise ValueError(
            "What=packaged templates missing; "
            f"Context=expected templates directory at '{templates}'; "
            "Fix=reinstall ockit (pip install --force-reinstall ockit)"
        )

    report = SyncReport(mode=mode)
    active_rels = _walk_rel(active) if os.path.isdir(active) else set()
    tpl_rels = _walk_rel(templates)

    for rel in sorted(active_rels | tpl_rels):
        active_path = os.path.join(active, rel)
        tpl_path = os.path.join(templates, rel)
        active_exists = os.path.isfile(active_path)
        tpl_exists = os.path.isfile(tpl_path)

        if active_exists and not tpl_exists:
            report.drift.append(DriftItem(rel, "missing_in_templates"))
        elif tpl_exists and not active_exists:
            report.drift.append(DriftItem(rel, "missing_in_active"))
        elif active_exists and tpl_exists:
            with open(active_path, "rb") as fa, open(tpl_path, "rb") as ft:
                if fa.read() != ft.read():
                    report.drift.append(DriftItem(rel, "content_mismatch"))

    if mode == "sync":
        for item in report.drift:
            if item.kind in ("missing_in_active", "content_mismatch"):
                _atomic_write(
                    os.path.join(templates, item.relative_path),
                    os.path.join(active, item.relative_path),
                )
                report.synced.append(item.relative_path)
        # After a successful sync, template-side drift is cleared; re-compute
        # so callers see the post-sync truth (E-017).
        report.drift = [
            item for item in report.drift if item.kind == "missing_in_templates"
        ]

    return report
