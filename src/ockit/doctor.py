"""
doctor.py — Environment health probe & diagnostics for ockit

Ports agy-kit's ``bin/agy-doctor.sh`` adapted to OpenCode-native paths
(R-013). The required custom agent inventory is the post-nativization set of
five (orchestrator/planner/coder/reviewer/qa); explore/general/compaction are
OpenCode built-ins and are NOT required (D5, R-023).

Source reference: https://github.com/giapminh79/agy-kit/tree/main/bin/agy-doctor.sh
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

# Required custom agents after nativization (R-023 / D5).
EXPECTED_AGENTS = ["orchestrator.md", "planner.md", "coder.md", "reviewer.md", "qa.md"]
EXPECTED_PLUGINS = [
    "ockit-quality-gate.js",
    "ockit-ba-traceability.js",
    "ockit-tdd-runner.js",
    "ockit-linter-fixer.js",
]
VALID_AGENT_MODES = {"primary", "subagent"}


def _run_probe(cmd: list[str], timeout: float = 5.0, label: str = "probe") -> str:
    """
    Runs a subprocess probe with a hard timeout (E-027).

    Returns decoded stdout+stderr, stripped. Raises TimeoutExpired when the
    probe exceeds ``timeout`` seconds — callers must handle it so no zombie
    processes or unbounded hangs leak into doctor runs.
    """
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return (proc.stdout + proc.stderr).strip()


def _parse_frontmatter(content: str) -> dict:
    """Minimal YAML-frontmatter parse; returns {} when absent/malformed."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        data[key.strip()] = val.strip().strip("'\"")
    return data


def run_doctor(project_root: str) -> dict[str, str | list[str] | bool]:
    results: dict[str, str | list[str] | bool] = {
        "git_installed": False,
        "opencode_installed": False,
        "node_installed": False,
        "python_version": "",
        "config_json_valid": False,
        "agents_md_present": False,
        "agents_valid": False,
        "agent_modes_valid": True,
        "plugins_valid": False,
        "skills_valid": False,
        "commands_valid": False,
        "errors": [],
        "warnings": [],
    }

    # 1. Check CLI tools (git is required; opencode/node are recommended).
    if shutil.which("git"):
        results["git_installed"] = True
    else:
        results["errors"].append("git is not installed")

    if shutil.which("opencode"):
        results["opencode_installed"] = True
    else:
        results["warnings"].append("opencode CLI not found in PATH")

    if shutil.which("node"):
        results["node_installed"] = True
    else:
        results["warnings"].append(
            "node not installed (optional for Python-only workflows)"
        )

    # 2. Check Python version via a timed subprocess (E-027).
    try:
        results["python_version"] = _run_probe(
            ["python3", "--version"], timeout=5.0, label="python3 --version"
        )
    except subprocess.TimeoutExpired:
        results["errors"].append("python3 --version probe timed out")
        results["python_version"] = "unknown"
    except OSError as exc:
        results["errors"].append(f"python3 probe failed: {exc}")
        results["python_version"] = "unknown"

    # 3. Check root AGENTS.md (R-013).
    agents_md_path = os.path.join(project_root, "AGENTS.md")
    if os.path.isfile(agents_md_path):
        results["agents_md_present"] = True
    else:
        results["errors"].append(
            "AGENTS.md missing from repository root (run ockit init)"
        )

    # 4. Check .opencode/opencode.json
    opencode_dir = os.path.join(project_root, ".opencode")
    config_json_path = os.path.join(opencode_dir, "opencode.json")

    if os.path.exists(config_json_path):
        try:
            with open(config_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                results["config_json_valid"] = True
            else:
                results["errors"].append(
                    ".opencode/opencode.json must contain a JSON object"
                )
        except Exception as e:  # noqa: BLE001
            results["errors"].append(f".opencode/opencode.json invalid JSON: {e}")
    else:
        results["errors"].append(".opencode/opencode.json configuration file missing")

    # 5. Check .opencode agent, plugin, skill, command directories.
    agents_dir = os.path.join(opencode_dir, "agent")
    plugins_dir = os.path.join(opencode_dir, "plugin")
    skills_dir = os.path.join(opencode_dir, "skill")
    commands_dir = os.path.join(opencode_dir, "command")

    missing_agents = []
    if os.path.exists(agents_dir):
        for ag in EXPECTED_AGENTS:
            if not os.path.exists(os.path.join(agents_dir, ag)):
                missing_agents.append(ag)
        if not missing_agents:
            results["agents_valid"] = True
        else:
            results["errors"].append(f"Missing custom agent specs: {missing_agents}")
    else:
        results["errors"].append(".opencode/agent directory missing")

    # Agent frontmatter validity: name/description/mode present, mode in
    # {primary, subagent} (R-013).
    frontmatter_errors: list[str] = []
    if os.path.exists(agents_dir):
        for filename in sorted(os.listdir(agents_dir)):
            if not filename.endswith(".md"):
                continue
            agent_path = os.path.join(agents_dir, filename)
            with open(agent_path, "r", encoding="utf-8") as fh:
                data = _parse_frontmatter(fh.read())
            missing_keys = [
                k for k in ("name", "description", "mode") if not data.get(k)
            ]
            if missing_keys:
                frontmatter_errors.append(
                    f"{filename} missing frontmatter key(s): {', '.join(missing_keys)}"
                )
                continue
            if data["mode"] not in VALID_AGENT_MODES:
                frontmatter_errors.append(
                    f"{filename} has invalid mode '{data['mode']}' (expected primary or subagent)"
                )
    if frontmatter_errors:
        results["agent_modes_valid"] = False
        results["errors"].extend(frontmatter_errors)

    # Check plugins
    missing_plugins = []
    if os.path.exists(plugins_dir):
        for pl in EXPECTED_PLUGINS:
            if not os.path.exists(os.path.join(plugins_dir, pl)):
                missing_plugins.append(pl)
        if not missing_plugins:
            results["plugins_valid"] = True
        else:
            results["warnings"].append(
                f"Missing recommended plugins: {missing_plugins}"
            )
    else:
        results["errors"].append(".opencode/plugin directory missing")

    # Check skills
    expected_skills = [
        "ba-expert",
        "brainstorming",
        "grill-me",
        "problem-solving",
        "qa-auditor",
        "qa-reproducer",
        "qa-test-gen",
        "quality-gate",
        "tdd-workflow",
        "writing-skills",
    ]
    missing_skills = []
    if os.path.exists(skills_dir):
        for sk in expected_skills:
            if not os.path.exists(os.path.join(skills_dir, sk, "SKILL.md")):
                missing_skills.append(sk)
        if not missing_skills:
            results["skills_valid"] = True
        else:
            results["warnings"].append(f"Missing production skills: {missing_skills}")
    else:
        results["errors"].append(".opencode/skill directory missing")

    # Check commands (14 commands, incl. ockit-init replacing init)
    expected_commands = [
        "brainstorm.md",
        "doctor.md",
        "gate.md",
        "grill.md",
        "ockit-init.md",
        "learn.md",
        "migrate.md",
        "pipeline.md",
        "plan.md",
        "qa.md",
        "review.md",
        "safe-pipeline.md",
        "schedule.md",
        "solve.md",
    ]
    missing_commands = []
    if os.path.exists(commands_dir):
        for cmd in expected_commands:
            if not os.path.exists(os.path.join(commands_dir, cmd)):
                missing_commands.append(cmd)
        if not missing_commands:
            results["commands_valid"] = True
        else:
            results["warnings"].append(f"Missing commands: {missing_commands}")
    else:
        results["errors"].append(".opencode/command directory missing")

    return results
