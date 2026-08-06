"""
doctor.py — Environment health probe & diagnostics for ockit
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess


def run_doctor(project_root: str) -> dict[str, str | list[str] | bool]:
    results = {
        "git_installed": False,
        "opencode_installed": False,
        "python_version": "",
        "config_json_valid": False,
        "agents_valid": False,
        "plugins_valid": False,
        "skills_valid": False,
        "workflows_valid": False,
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

    # 3. Check .opencode/opencode.json
    opencode_dir = os.path.join(project_root, ".opencode")
    config_json_path = os.path.join(opencode_dir, "opencode.json")

    if os.path.exists(config_json_path):
        try:
            with open(config_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "provider" in data and "agent" in data:
                    results["config_json_valid"] = True
                else:
                    results["warnings"].append(".opencode/opencode.json missing 'provider' or 'agent' keys")
        except Exception as e:  # noqa: BLE001
            results["errors"].append(f".opencode/opencode.json invalid JSON: {e}")
    else:
        results["errors"].append(".opencode/opencode.json configuration file missing")

    # 4. Check .opencode agents, plugins, skills, workflows
    agents_dir = os.path.join(opencode_dir, "agents")
    plugins_dir = os.path.join(opencode_dir, "plugins")
    skills_dir = os.path.join(opencode_dir, "skills")
    workflows_dir = os.path.join(opencode_dir, "workflows")

    expected_agents = ["orchestrator.md", "planner.md", "coder.md", "reviewer.md", "qa.md"]
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

    # Check plugins
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

    # Check skills (12 skills)
    expected_skills = [
        "ba-expert", "brainstorming", "grill-me", "problem-solving",
        "qa-auditor", "qa-reproducer", "qa-test-gen", "quality-gate",
        "tdd-workflow", "writing-skills"
    ]
    missing_skills = []

    if os.path.exists(skills_dir):
        for sk in expected_skills:
            sk_path = os.path.join(skills_dir, sk, "SKILL.md")
            if not os.path.exists(sk_path):
                missing_skills.append(sk)
        if not missing_skills:
            results["skills_valid"] = True
        else:
            results["warnings"].append(f"Missing production skills: {missing_skills}")
    else:
        results["errors"].append(".opencode/skills directory missing")

    # Check 14 Workflows
    expected_workflows = [
        "brainstorm.md", "doctor.md", "gate.md", "grill.md", "init.md",
        "learn.md", "migrate.md", "pipeline.md", "plan.md", "qa.md",
        "review.md", "safe-pipeline.md", "schedule.md", "solve.md"
    ]
    missing_workflows = []

    if os.path.exists(workflows_dir):
        for wf in expected_workflows:
            wf_path = os.path.join(workflows_dir, wf)
            if not os.path.exists(wf_path):
                missing_workflows.append(wf)
        if not missing_workflows:
            results["workflows_valid"] = True
        else:
            results["warnings"].append(f"Missing workflows: {missing_workflows}")
    else:
        results["errors"].append(".opencode/workflows directory missing")

    return results
