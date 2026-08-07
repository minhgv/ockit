"""
installer.py — Project scaffolder logic for `ockit init`

Ports the behavior of agy-kit's ``bin/init-agy-kit.sh`` into Python, with
path-safety validation (R-006), dry-run / force-with-backup (R-005, E-024),
idempotent re-runs (R-007), atomic per-file writes (R-022, E-018) and root
``AGENTS.md`` scaffolding (R-009).

Source reference: https://github.com/giapminh79/agy-kit/tree/main/bin/init-agy-kit.sh
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time

from ockit.validators import resolve_safe_target

# Junk entries skipped when walking packaged templates (E-026).
_IGNORED_FILES = {".DS_Store"}
_IGNORED_DIRS = {"__pycache__", ".git"}

_DEFAULT_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)


class OckitInstaller:
    def __init__(self, templates_dir: str | None = None):
        if templates_dir is None:
            templates_dir = _DEFAULT_TEMPLATES_DIR
        self.templates_dir = os.path.abspath(templates_dir)

    # -- public API ---------------------------------------------------------

    def install(
        self,
        target: str,
        lang: str = "python",
        force: bool = False,
        dry_run: bool = False,
    ) -> dict[str, str | list[str]]:
        """
        Scaffolds ``target/.opencode/`` + root ``AGENTS.md`` from packaged templates.

        Returns an InitResult-shaped dict:
        ``{status, target_dir, opencode_dir, copied_files[], skipped_files[]}``.
        - ``dry_run=True``: reports what WOULD be copied, writes nothing,
          ``status`` is ``"dry_run"``.
        - without ``force``: existing files are skipped (never overwritten).
        - with ``force``: existing files are overwritten, but originals are
          first backed up into ``target/.opencode.bak-<timestamp>`` (E-024).

        Raises ValueError (What/Context/Fix) on unsafe targets or missing
        packaged templates.
        """
        target_dir = str(resolve_safe_target(target))
        opencode_dir = os.path.join(target_dir, ".opencode")

        if not os.path.isdir(self.templates_dir):
            raise ValueError(
                "What=packaged templates missing; "
                f"Context=expected templates directory at '{self.templates_dir}'; "
                "Fix=reinstall ockit (pip install --force-reinstall ockit)"
            )

        plan = self._plan_files()  # list of relative template paths
        if dry_run:
            return {
                "status": "dry_run",
                "target_dir": target_dir,
                "opencode_dir": opencode_dir,
                "copied_files": sorted(plan),
                "skipped_files": [],
            }

        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(opencode_dir, exist_ok=True)

        backup_dir = None
        if force:
            existing = [
                rel
                for rel in plan
                if os.path.exists(self._dest(opencode_dir, target_dir, rel))
            ]
            if existing:
                backup_dir = self._create_backup_dir(target_dir, existing, opencode_dir)

        copied_files: list[str] = []
        skipped_files: list[str] = []

        for rel in plan:
            src = os.path.join(self.templates_dir, rel)
            dst = self._dest(opencode_dir, target_dir, rel)
            if os.path.exists(dst) and not force:
                skipped_files.append(rel)
                continue
            self._atomic_copy(src, dst)
            copied_files.append(rel)

        return {
            "status": "success",
            "target_dir": target_dir,
            "opencode_dir": opencode_dir,
            "copied_files": copied_files,
            "skipped_files": skipped_files,
        }

    def initialize_project(
        self, target_dir: str, lang: str = "python", force: bool = False
    ) -> dict[str, str | list[str]]:
        """Backward-compatible alias for ``install()`` (pre-R-005 API)."""
        return self.install(target=target_dir, lang=lang, force=force)

    # -- internals ----------------------------------------------------------

    def _plan_files(self) -> list[str]:
        """Relative paths of every template file to ship (junk excluded)."""
        rels: list[str] = []
        for root, dirs, files in os.walk(self.templates_dir):
            dirs[:] = [d for d in dirs if d not in _IGNORED_DIRS]
            for f in files:
                if f in _IGNORED_FILES:
                    continue
                full = os.path.join(root, f)
                rels.append(os.path.relpath(full, self.templates_dir))
        return rels

    @staticmethod
    def _dest(opencode_dir: str, target_dir: str, rel: str) -> str:
        """Destination path: root AGENTS.md → target root, everything else → .opencode/."""
        if rel == "AGENTS.md":
            return os.path.join(target_dir, "AGENTS.md")
        return os.path.join(opencode_dir, rel)

    def _create_backup_dir(
        self, target_dir: str, rels: list[str], opencode_dir: str
    ) -> str:
        timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        backup_dir = os.path.join(target_dir, f".opencode.bak-{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        for rel in rels:
            src = self._dest(opencode_dir, target_dir, rel)
            dst = os.path.join(backup_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        return backup_dir

    @staticmethod
    def _atomic_copy(src: str, dst: str) -> None:
        """
        Copies ``src`` → ``dst`` atomically: write to a temp file in the same
        directory, then ``os.replace``. A kill mid-copy can only leave an
        orphan ``.ockit-tmp-*`` file, never a corrupt destination (R-022).
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
