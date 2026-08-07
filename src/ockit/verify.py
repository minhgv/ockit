"""
verify.py — Requirement traceability & workflow audit engine for `ockit verify`

Ports the behavior of agy-kit's ``bin/validate-traceability.sh``,
``bin/validate-phase10-ba-qa.sh``, ``bin/validate_agents.py`` and
``bin/validate-workflows-sync.sh`` into Python with OpenCode-native paths
(R-001, R-002, R-014, R-020).

Source references:
- https://github.com/giapminh79/agy-kit/tree/main/bin/validate-traceability.sh
- https://github.com/giapminh79/agy-kit/tree/main/bin/validate-phase10-ba-qa.sh
- https://github.com/giapminh79/agy-kit/tree/main/bin/validate_agents.py
- https://github.com/giapminh79/agy-kit/tree/main/bin/validate-workflows-sync.sh

Exit contract (R-020): exit 0 when error_count == 0 (warnings allowed),
exit 1 when any FAIL finding is present. Findings print as ``[OK]``/``[WARN]``/``[FAIL]``.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# Suite names accepted by ``--suite`` (R-028 / VerifySuite enum).
VERIFY_SUITES = ("all", "traceability", "ba-qa", "agents", "commands")

_DEFAULT_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)

# Built-in OpenCode agent names that ockit must never ship (E-012 / D5).
BUILTIN_CLOBBER_NAMES = {"explore", "general", "compaction"}

# Valid OpenCode agent modes (doctor + verify policy).
VALID_AGENT_MODES = {"primary", "subagent"}

# Allowed thin-wrapper bin scripts referenced from command bodies (R-011/R-014).
ALLOWED_BIN_WRAPPERS = {
    "validate-traceability.sh",
    "validate-phase10-ba-qa.sh",
    "scan-dependencies.sh",
}

# Regex matching a ``bin/<script>.sh`` reference inside command Markdown (E-011).
_BIN_REF_RE = re.compile(r"(?:\./)?bin/([A-Za-z0-9_.-]+\.sh)")


@dataclass
class VerifyFinding:
    """Single audit result line. ``level`` is one of OK / WARN / FAIL."""

    level: str  # "OK" | "WARN" | "FAIL"
    message: str
    path: str | None = None


@dataclass
class VerifyReport:
    """Structured audit result (VerifyReport schema, section 3)."""

    suite: str
    findings: list[VerifyFinding] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.level == "FAIL")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.level == "WARN")

    @property
    def exit_code(self) -> int:
        return 1 if self.error_count > 0 else 0


def parse_frontmatter(content: str) -> dict:
    """
    Minimal YAML-frontmatter parser for OpenCode agent Markdown.

    Returns a dict of ``key: value`` pairs. Raises ValueError (What/Context/Fix)
    when the file has no ``---`` delimiters or malformed delimiters.
    """
    if not content.startswith("---"):
        raise ValueError(
            "What=malformed agent frontmatter; "
            "Context=file does not start with a '---' frontmatter marker; "
            "Fix=add YAML frontmatter with name, description and mode keys"
        )
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(
            "What=malformed agent frontmatter; "
            "Context=frontmatter delimiters are not closed; "
            "Fix=close the frontmatter block with a trailing '---' line"
        )
    data: dict = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip("'\"")
    return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_verify(
    suite: str = "all",
    project_root: str | None = None,
    plans_dir: str | None = None,
    templates_dir: str | None = None,
    agents_dir: str | None = None,
    commands_dir: str | None = None,
) -> VerifyReport:
    """
    Runs the requested audit suite against ``project_root`` (default cwd).

    Directories default to OpenCode-native paths under ``project_root``:
    ``plans/``, ``.opencode/agent/``, ``.opencode/command/``. ``templates_dir``
    defaults to the packaged ``ockit/templates`` tree (used by the ba-qa
    mirror checks).

    Raises ValueError with a What/Context/Fix message for unknown suites.
    """
    if suite not in VERIFY_SUITES:
        raise ValueError(
            f"What=unknown verify suite; Context=got '{suite}', expected one of "
            f"{', '.join(VERIFY_SUITES)}; Fix=pass --suite {VERIFY_SUITES[0]} or a "
            "listed suite name"
        )

    root = os.path.abspath(project_root or os.getcwd())
    plans = os.path.abspath(plans_dir) if plans_dir else os.path.join(root, "plans")
    tpl = os.path.abspath(templates_dir) if templates_dir else _DEFAULT_TEMPLATES_DIR
    agents = (
        os.path.abspath(agents_dir)
        if agents_dir
        else os.path.join(root, ".opencode", "agent")
    )
    commands = (
        os.path.abspath(commands_dir)
        if commands_dir
        else os.path.join(root, ".opencode", "command")
    )

    report = VerifyReport(suite=suite)

    if suite in ("all", "traceability"):
        _verify_traceability(report, plans)
    if suite in ("all", "ba-qa"):
        _verify_ba_qa(report, root, plans, tpl)
    if suite in ("all", "agents"):
        _verify_agents(report, agents)
    if suite in ("all", "commands"):
        _verify_commands(report, commands)

    return report


# ---------------------------------------------------------------------------
# R-001 — traceability suite
# ---------------------------------------------------------------------------


def _has_rtm_section(content: str) -> bool:
    """RTM section = RTM marker plus a ``| Req ID |`` table header (R-001)."""
    return (
        "RTM" in content or "Requirement Traceability Matrix" in content
    ) and "| Req ID |" in content


def _has_edge_case_section(content: str) -> bool:
    return "Edge Case" in content


def _unit_test_ref_missing(content: str) -> tuple[int, int]:
    """
    Counts RTM table rows whose ``Unit Test Reference`` cell is empty.

    Returns ``(missing, total)``. A missing/absent column counts every row as
    missing. Separator rows (``|---|---|``) are ignored.
    """
    lines = content.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if "| Req ID |" in line:
            header_idx = i
            break
    if header_idx is None:
        return 0, 0
    header_cells = [c.strip() for c in lines[header_idx].split("|")]
    if len(header_cells) >= 2 and header_cells[0] == "" and header_cells[-1] == "":
        header_cells = header_cells[1:-1]
    col = None
    for idx, cell in enumerate(header_cells):
        if cell == "Unit Test Reference":
            col = idx
            break
    missing = 0
    total = 0
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        # separator row like |---|---|
        if set(stripped) <= set("|- "):
            continue
        cells = [c.strip() for c in stripped.split("|")]
        if len(cells) >= 2 and cells[0] == "" and cells[-1] == "":
            cells = cells[1:-1]
        # Only RTM requirement rows (R-<n>) belong to this table; other tables
        # (e.g. Edge Case E-<n>) must not be counted against unit-test refs.
        if not cells or not re.match(r"^R-\d+", cells[0]):
            continue
        total += 1
        cell = cells[col] if col is not None and col < len(cells) else ""
        if not cell or cell in {"N/A", "-", "None", "TBD", "TODO", "pending"}:
            missing += 1
    return missing, total


def _verify_traceability(report: VerifyReport, plans_dir: str) -> None:
    template_path = os.path.join(plans_dir, "SPEC_TEMPLATE.md")

    if not os.path.isdir(plans_dir):
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "SPEC_TEMPLATE.md not found: plans/ directory missing "
                "(run ockit verify from the repository root)",
                path=plans_dir,
            )
        )
        return

    if not os.path.isfile(template_path):
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "SPEC_TEMPLATE.md not found at plans/SPEC_TEMPLATE.md",
                path=template_path,
            )
        )
        return

    with open(template_path, "r", encoding="utf-8") as fh:
        template_content = fh.read()

    if _has_rtm_section(template_content):
        report.findings.append(
            VerifyFinding(
                "OK",
                "SPEC_TEMPLATE.md contains Requirement Traceability Matrix (RTM).",
                path=template_path,
            )
        )
    else:
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "SPEC_TEMPLATE.md missing RTM section (requires a '| Req ID |' table)",
                path=template_path,
            )
        )

    if _has_edge_case_section(template_content):
        report.findings.append(
            VerifyFinding(
                "OK",
                "SPEC_TEMPLATE.md contains Edge Case Matrix section.",
                path=template_path,
            )
        )
    else:
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "SPEC_TEMPLATE.md missing Edge Case Matrix section",
                path=template_path,
            )
        )

    if "3-State Verification" in template_content:
        report.findings.append(
            VerifyFinding(
                "OK",
                "SPEC_TEMPLATE.md contains 3-State Verification definition.",
                path=template_path,
            )
        )
    else:
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "SPEC_TEMPLATE.md missing 3-State Verification section",
                path=template_path,
            )
        )

    # Audit active SPEC_*.md files (exclude the template).
    spec_files = sorted(
        f
        for f in os.listdir(plans_dir)
        if f.startswith("SPEC_") and f.endswith(".md") and f != "SPEC_TEMPLATE.md"
    )

    if not spec_files:
        report.findings.append(
            VerifyFinding("OK", "[OK] No active feature SPECs found in plans/")
        )
        return

    for spec_name in spec_files:
        spec_path = os.path.join(plans_dir, spec_name)
        with open(spec_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        if _has_rtm_section(content):
            report.findings.append(
                VerifyFinding("OK", f"{spec_name} has RTM section.", path=spec_path)
            )
            missing_refs, _ = _unit_test_ref_missing(content)
            if missing_refs:
                report.findings.append(
                    VerifyFinding(
                        "WARN",
                        f"{spec_name}: {missing_refs} RTM row(s) missing a Unit Test Reference cell",
                        path=spec_path,
                    )
                )
            else:
                report.findings.append(
                    VerifyFinding(
                        "OK",
                        f"{spec_name}: RTM rows have Unit Test Reference cells.",
                        path=spec_path,
                    )
                )
        else:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"{spec_name} missing RTM table section (requires a '| Req ID |' table)",
                    path=spec_path,
                )
            )

        if _has_edge_case_section(content):
            report.findings.append(
                VerifyFinding(
                    "OK", f"{spec_name} has Edge Case section.", path=spec_path
                )
            )
        else:
            report.findings.append(
                VerifyFinding(
                    "WARN",
                    f"{spec_name} missing Edge Case section (12-Dimensional Edge Case Matrix)",
                    path=spec_path,
                )
            )


# ---------------------------------------------------------------------------
# R-002 — ba-qa suite (phase10 port, adapted to OpenCode paths)
# ---------------------------------------------------------------------------

_BA_QA_SKILLS = ("ba-expert", "qa-auditor", "qa-test-gen", "qa-reproducer")

_SKILL_CONTENT_MARKERS = {
    "ba-expert": ("12-Dimensional", "Bounded Contexts", "User Stories", "Zod"),
    "qa-auditor": ("audit_summary", "Runtime Risk Matrix"),
    "qa-test-gen": ("test_plan", "Gherkin"),
    "qa-reproducer": ("reproduction_summary", "Minimal Reproduction"),
}

_AGENT_CONTENT_MARKERS = {
    "planner.md": (("ba-expert",), ("12-Dimensional",)),
    "coder.md": (("qa-test-gen", "qa-auditor"), ()),
    "reviewer.md": (("ba-expert", "qa-auditor"), ("reviewer",)),
    "qa.md": (("qa-reproducer", "qa-test-gen"), ()),
}


def _verify_ba_qa(
    report: VerifyReport, project_root: str, plans_dir: str, templates_dir: str
) -> None:
    active_skills = os.path.join(project_root, ".opencode", "skill")

    for skill in _BA_QA_SKILLS:
        active_file = os.path.join(active_skills, skill, "SKILL.md")
        tpl_file = os.path.join(templates_dir, "skill", skill, "SKILL.md")
        active_exists = os.path.isfile(active_file)
        tpl_exists = os.path.isfile(tpl_file)

        if active_exists:
            report.findings.append(
                VerifyFinding(
                    "OK", f"Skill {skill} found in .opencode/skill/", path=active_file
                )
            )
        else:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"Skill {skill} missing from .opencode/skill/",
                    path=active_file,
                )
            )
        if tpl_exists:
            report.findings.append(
                VerifyFinding(
                    "OK",
                    f"Skill {skill} found in packaged templates/skill/",
                    path=tpl_file,
                )
            )
        else:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"Skill {skill} missing from packaged templates/skill/",
                    path=tpl_file,
                )
            )

        if active_exists and tpl_exists:
            with open(active_file, "rb") as fa, open(tpl_file, "rb") as ft:
                mirrored = fa.read() == ft.read()
            if mirrored:
                report.findings.append(
                    VerifyFinding(
                        "OK", f"Skill {skill} mirrored between active and templates."
                    )
                )
            else:
                report.findings.append(
                    VerifyFinding(
                        "FAIL",
                        f"Skill {skill} not mirrored: content mismatch between active and "
                        "templates (run ockit sync)",
                        path=active_file,
                    )
                )

        # Skill content requirements (validated against the ACTIVE copy).
        if active_exists:
            with open(active_file, "r", encoding="utf-8") as fh:
                content = fh.read()
            markers = _SKILL_CONTENT_MARKERS[skill]
            missing = [m for m in markers if m not in content]
            if missing:
                report.findings.append(
                    VerifyFinding(
                        "FAIL",
                        f"Skill {skill} missing mandatory content markers: {', '.join(missing)}",
                        path=active_file,
                    )
                )
            else:
                report.findings.append(
                    VerifyFinding(
                        "OK", f"Skill {skill} content requirements satisfied."
                    )
                )

    # SPEC_TEMPLATE Phase 10 artefacts: RTM / ACM / NFR / DFD.
    template_path = os.path.join(plans_dir, "SPEC_TEMPLATE.md")
    if os.path.isfile(template_path):
        with open(template_path, "r", encoding="utf-8") as fh:
            tpl_content = fh.read()
        missing_sections = [
            s for s in ("RTM", "ACM", "NFR", "DFD") if s not in tpl_content
        ]
        if missing_sections:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"SPEC_TEMPLATE.md missing Phase 10 sections: {', '.join(missing_sections)}",
                    path=template_path,
                )
            )
        else:
            report.findings.append(
                VerifyFinding(
                    "OK", "SPEC_TEMPLATE.md contains RTM, ACM, NFR and DFD sections."
                )
            )
    else:
        report.findings.append(
            VerifyFinding(
                "FAIL", "SPEC_TEMPLATE.md not found for ba-qa audit", path=template_path
            )
        )

    # Agent markdown Phase 10 instruction references.
    agents_dir = os.path.join(project_root, ".opencode", "agent")
    for filename, (any_markers, all_markers) in _AGENT_CONTENT_MARKERS.items():
        agent_path = os.path.join(agents_dir, filename)
        if not os.path.isfile(agent_path):
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"Agent spec {filename} missing for ba-qa audit",
                    path=agent_path,
                )
            )
            continue
        with open(agent_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        ok_any = any(m in content for m in any_markers)
        ok_all = all(m in content for m in all_markers)
        if ok_any and ok_all:
            report.findings.append(
                VerifyFinding(
                    "OK", f"{filename} updated with Phase 10 BA/QA instructions."
                )
            )
        else:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"{filename} missing Phase 10 BA/QA instruction references",
                    path=agent_path,
                )
            )

    # Documentation presence (adapted: ockit ships README.md, not .agents docs/).
    readme_path = os.path.join(project_root, "README.md")
    if os.path.isfile(readme_path):
        report.findings.append(
            VerifyFinding("OK", "README.md documentation present.", path=readme_path)
        )
    else:
        report.findings.append(
            VerifyFinding(
                "WARN",
                "README.md missing from project root (documentation gap)",
                path=readme_path,
            )
        )


# ---------------------------------------------------------------------------
# R-014 — agents suite
# ---------------------------------------------------------------------------


def _verify_agents(report: VerifyReport, agents_dir: str) -> None:
    if not os.path.isdir(agents_dir):
        report.findings.append(
            VerifyFinding(
                "FAIL",
                ".opencode/agent directory missing",
                path=agents_dir,
            )
        )
        return

    md_files = sorted(f for f in os.listdir(agents_dir) if f.endswith(".md"))
    if not md_files:
        report.findings.append(
            VerifyFinding(
                "FAIL",
                "No Markdown agent files found in .opencode/agent",
                path=agents_dir,
            )
        )
        return

    for filename in md_files:
        agent_path = os.path.join(agents_dir, filename)
        agent_name = os.path.splitext(filename)[0]

        if agent_name in BUILTIN_CLOBBER_NAMES:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"built-in clobber: agent file '{filename}' overrides the OpenCode "
                    f"built-in '{agent_name}' agent; remove it from the ship set",
                    path=agent_path,
                )
            )
            continue

        with open(agent_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        try:
            data = parse_frontmatter(content)
        except ValueError as exc:
            report.findings.append(VerifyFinding("FAIL", str(exc), path=agent_path))
            continue

        for key in ("name", "description", "mode"):
            value = data.get(key, "")
            if not value:
                report.findings.append(
                    VerifyFinding(
                        "FAIL",
                        f"agent '{agent_name}' missing required frontmatter key '{key}'",
                        path=agent_path,
                    )
                )
        mode = data.get("mode")
        if mode and mode not in VALID_AGENT_MODES:
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    f"agent '{agent_name}' has invalid mode '{mode}' "
                    f"(expected one of {', '.join(sorted(VALID_AGENT_MODES))})",
                    path=agent_path,
                )
            )


# ---------------------------------------------------------------------------
# R-014 — commands suite
# ---------------------------------------------------------------------------


def _verify_commands(report: VerifyReport, commands_dir: str) -> None:
    if not os.path.isdir(commands_dir):
        report.findings.append(
            VerifyFinding(
                "FAIL",
                ".opencode/command directory missing",
                path=commands_dir,
            )
        )
        return

    md_files = sorted(f for f in os.listdir(commands_dir) if f.endswith(".md"))

    for filename in md_files:
        command_path = os.path.join(commands_dir, filename)

        if filename == "init.md":
            report.findings.append(
                VerifyFinding(
                    "FAIL",
                    "init.md present: must be renamed to ockit-init.md (avoid OpenCode "
                    "built-in /init clobber)",
                    path=command_path,
                )
            )

        with open(command_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        for match in _BIN_REF_RE.finditer(content):
            script = match.group(1)
            if script not in ALLOWED_BIN_WRAPPERS:
                report.findings.append(
                    VerifyFinding(
                        "FAIL",
                        f"dead bin reference './bin/{script}' in '{filename}'; "
                        f"rewrite to '!ockit ...' (allowed wrappers: "
                        f"{', '.join(sorted(ALLOWED_BIN_WRAPPERS))})",
                        path=command_path,
                    )
                )
