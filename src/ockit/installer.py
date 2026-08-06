"""
installer.py — Project scaffolder logic for `ockit init`
"""
from __future__ import annotations

import os
import shutil


class OckitInstaller:

    def __init__(self, templates_dir: str):
        self.templates_dir = os.path.abspath(templates_dir)

    def initialize_project(self, target_dir: str, lang: str = "python", force: bool = False) -> dict[str, str | list[str]]:
        target_dir = os.path.abspath(target_dir)
        opencode_dir = os.path.join(target_dir, ".opencode")

        os.makedirs(opencode_dir, exist_ok=True)
        copied_files: list[str] = []

        subdirs = ["agents", "plugins", "workflows", "prompts", "skills"]
        for sd in subdirs:
            src_sd = os.path.join(self.templates_dir, sd)
            dst_sd = os.path.join(opencode_dir, sd)
            os.makedirs(dst_sd, exist_ok=True)

            if os.path.exists(src_sd):
                for root, dirs, files in os.walk(src_sd):
                    rel_path = os.path.relpath(root, src_sd)
                    target_root = os.path.join(dst_sd, rel_path) if rel_path != "." else dst_sd
                    os.makedirs(target_root, exist_ok=True)

                    for f in files:
                        s_file = os.path.join(root, f)
                        d_file = os.path.join(target_root, f)
                        if not os.path.exists(d_file) or force:
                            shutil.copy2(s_file, d_file)
                            copied_files.append(d_file)

        # Copy opencode.json config file
        src_opencode_json = os.path.join(self.templates_dir, "opencode.json")
        dst_opencode_json = os.path.join(opencode_dir, "opencode.json")
        if os.path.exists(src_opencode_json) and (not os.path.exists(dst_opencode_json) or force):
            shutil.copy2(src_opencode_json, dst_opencode_json)
            copied_files.append(dst_opencode_json)

        # Copy mcp_config.json if available
        src_mcp = os.path.join(self.templates_dir, "mcp_config.json")
        dst_mcp = os.path.join(opencode_dir, "mcp_config.json")
        if os.path.exists(src_mcp) and (not os.path.exists(dst_mcp) or force):
            shutil.copy2(src_mcp, dst_mcp)
            copied_files.append(dst_mcp)

        return {
            "status": "success",
            "target_dir": target_dir,
            "opencode_dir": opencode_dir,
            "copied_files": copied_files,
        }
