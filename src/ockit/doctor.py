"""
doctor.py — Environment health probe & diagnostics for ockit
"""
from __future__ import annotations

import os
import shutil
import subprocess


def run_doctor(project_root: str) -> dict[str, str | list[str] | bool]:
    results = {
        "git_installed": False,
        "opencode_installed": False,
        "python_version": "",
        "agents_valid": False,
        "plugins_valid": False,
        "errors": [],
        "warnings": [],
    }

    # 1. Check CLI tools
    if shutil.which("git"):
        results["git_installed"] = True
    else:
        results["errors"].append("git is not installed")

    if shutil.which("opencode"):
        results["opencode_installed"] = True
    else:
        results["warnings"].append("opencode CLI not found in PATH")

    # 2. Check Python
    results["python_version"] = subprocess.getoutput("python3 --version")

    # 3. Check .opencode directory structure
    opencode_dir = os.path.join(project_root, ".opencode")
    agents_dir = os.path.join(opencode_dir, "agents")
    plugins_dir = os.path.join(opencode_dir, "plugins")

    expected_agents = ["planner.md", "coder.md", "reviewer.md", "qa.md"]
    missing_agents = []

    if os.path.exists(agents_dir):
        for ag in expected_agents:
            ag_path = os.path.join(agents_dir, ag)
            if not os.path.exists(ag_path):
                missing_agents.append(ag)
        if not missing_agents:
            results["agents_valid"] = True
        else:
            results["errors"].append(f"Missing subagent specs: {missing_agents}")
    else:
        results["errors"].append(".opencode/agents directory missing")

    # 4. Check plugins
    expected_plugins = ["ockit-quality-gate.js", "ockit-ba-traceability.js", "ockit-tdd-runner.js"]
    missing_plugins = []

    if os.path.exists(plugins_dir):
        for pl in expected_plugins:
            pl_path = os.path.join(plugins_dir, pl)
            if not os.path.exists(pl_path):
                missing_plugins.append(pl)
        if not missing_plugins:
            results["plugins_valid"] = True
        else:
            results["warnings"].append(f"Missing recommended plugins: {missing_plugins}")
    else:
        results["errors"].append(".opencode/plugins directory missing")

    return results
