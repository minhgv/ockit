"""
worktree.py — Git worktree isolation manager & safe apply checker for ockit
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile


class WorktreeManager:
    def __init__(self, project_root: str, run_id: str):
        self.project_root: str = project_root
        self.run_id: str = run_id
        self.worktree_dir: str | None = None

    def create_isolated_worktree(self, feature: str) -> str:
        branch_name = f"ockit-wt-{feature}-{self.run_id}"
        temp_dir = tempfile.mkdtemp(prefix=f"ockit-wt-{self.run_id}-")
        try:
            cmd = [
                "git",
                "-C",
                self.project_root,
                "worktree",
                "add",
                "-b",
                branch_name,
                temp_dir,
                "HEAD",
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        except BaseException:
            # E-028: never leak the temp dir when git worktree add fails.
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
        self.worktree_dir = temp_dir
        return temp_dir

    def check_patch_apply(self, patch_file: str) -> bool:
        """Pre-checks if patch can be applied cleanly using git apply --check."""
        if not os.path.exists(patch_file):
            return False
        cmd = ["git", "-C", self.project_root, "apply", "--check", patch_file]
        res = subprocess.run(cmd, capture_output=True, check=False)
        return res.returncode == 0

    def remove_worktree(self):
        if self.worktree_dir and os.path.exists(self.worktree_dir):
            subprocess.run(
                [
                    "git",
                    "-C",
                    self.project_root,
                    "worktree",
                    "remove",
                    "--force",
                    self.worktree_dir,
                ],
                capture_output=True,
                check=False,
            )
