#!/usr/bin/env python3
"""
generate_verify_contract.py — Regenerate ba-expert verify-contract.md from verify.py constants.

Ensures the documentation inside the ba-expert skill reference stays in sync with the
actual verify engine implementation. Run via:

    python scripts/generate_verify_contract.py

Test `tests/unit/test_verify_contract_fresh.py` asserts the committed copy is identical
to a freshly generated one, preventing silent staleness.
"""

from __future__ import annotations

import os
import sys
from textwrap import dedent

# Ensure src/ is importable when running from repo root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))

from ockit.verify import (  # noqa: E402
    ALLOWED_BIN_WRAPPERS,
    BUILTIN_CLOBBER_NAMES,
    VALID_AGENT_MODES,
    VERIFY_SUITES,
    _AGENT_CONTENT_MARKERS,
    _SKILL_CONTENT_MARKERS,
)

_OUTPUT = os.path.join(
    _ROOT,
    "src",
    "ockit",
    "templates",
    "skill",
    "ba-expert",
    "references",
    "verify-contract.md",
)


def _skill_markers_table() -> str:
    rows = []
    for skill, markers in _SKILL_CONTENT_MARKERS.items():
        rows.append(f"| {skill} | `{'`, `'.join(markers)}` |")
    return "\n".join(rows)


def _agent_markers_table() -> str:
    rows = []
    for filename, (any_markers, all_markers) in _AGENT_CONTENT_MARKERS.items():
        any_str = ", ".join(f"`{m}`" for m in any_markers) if any_markers else "(none)"
        all_str = ", ".join(f"`{m}`" for m in all_markers) if all_markers else "(none)"
        rows.append(f"| `{filename}` | {any_str} | {all_str} |")
    return "\n".join(rows)


def generate() -> str:
    suites = ", ".join(VERIFY_SUITES)
    clobber = ", ".join(sorted(BUILTIN_CLOBBER_NAMES))
    modes = ", ".join(sorted(VALID_AGENT_MODES))
    wrappers = ", ".join(sorted(ALLOWED_BIN_WRAPPERS))
    return f"""# Reference: Verify Contract

> **AUTO-GENERATED from `src/ockit/verify.py` by `scripts/generate_verify_contract.py`.**
> Do NOT edit manually — changes will be overwritten.
> Test `tests/unit/test_verify_contract_fresh.py` enforces freshness.

---

## Suites

`ockit verify --suite {{{suites}}}`

| Suite | Checks |
|---|---|
| `all` (default) | Runs all 4 suites below |
| `traceability` | SPEC_TEMPLATE + active SPEC_*.md: RTM table, Edge Case, 3-State Verification |
| `ba-qa` | 4 BA/QA skills mirrored + content markers; SPEC_TEMPLATE Phase 10 sections; agent Phase 10 refs; README present |
| `agents` | .opencode/agent/*.md frontmatter: name/description/mode; mode in {{{modes}}}; no built-in clobber |
| `commands` | .opencode/command/*.md: no init.md clobber; no dead bin/*.sh refs outside allowlist |

---

## traceability Suite — Exact Checks

Source: `verify.py:_verify_traceability`

| # | Check | Level | Trigger |
|---|---|---|---|
| T1 | `plans/` directory exists | FAIL | plans/ missing |
| T2 | `plans/SPEC_TEMPLATE.md` exists | FAIL | file missing |
| T3 | SPEC_TEMPLATE contains RTM section | FAIL | no `| Req ID |` table header OR missing "RTM"/"Requirement Traceability Matrix" string |
| T4 | SPEC_TEMPLATE contains Edge Case section | FAIL | string "Edge Case" absent |
| T5 | SPEC_TEMPLATE contains "3-State Verification" | FAIL | string absent |
| T6 | Each `SPEC_*.md` (excl. TEMPLATE) has RTM section | FAIL | no `| Req ID |` header |
| T7 | RTM rows missing Unit Test Reference cell | WARN | cell empty or in {{N/A, -, None, TBD, TODO, pending}} |
| T8 | Each SPEC_*.md has Edge Case section | WARN | string "Edge Case" absent |

**RTM row detection regex:** `^R-\\d+` — only rows starting with `R-<number>` are counted.

---

## ba-qa Suite — Exact Checks

Source: `verify.py:_verify_ba_qa`

### BA/QA Skills (4 mandatory)

For each skill in `{{ba-expert, qa-auditor, qa-test-gen, qa-reproducer}}`:

| # | Check | Level |
|---|---|---|
| B1 | Active copy exists at `.opencode/skill/<name>/SKILL.md` | FAIL |
| B2 | Template copy exists at `templates/skill/<name>/SKILL.md` | FAIL |
| B3 | Active == Template (byte-identical mirror) | FAIL |
| B4 | Content markers present in active copy | FAIL |

**Content markers per skill:**

| Skill | Required markers (ALL must be present) |
|---|---|
{_skill_markers_table()}

### SPEC_TEMPLATE Phase 10 Sections

| # | Check | Level |
|---|---|---|
| B5 | SPEC_TEMPLATE contains ALL of: `RTM`, `ACM`, `NFR`, `DFD` | FAIL |

### Agent Phase 10 References

For each agent file in `.opencode/agent/`:

| Agent file | Any-of markers | All-of markers |
|---|---|---|
{_agent_markers_table()}

Missing agent file or missing markers → **FAIL**.

### Documentation

| # | Check | Level |
|---|---|---|
| B6 | `README.md` exists in project root | WARN |

---

## agents Suite — Exact Checks

Source: `verify.py:_verify_agents`

| # | Check | Level | Trigger |
|---|---|---|---|
| A1 | `.opencode/agent/` directory exists | FAIL | missing |
| A2 | At least 1 `.md` file in agent dir | FAIL | empty |
| A3 | Agent name NOT in `{{{clobber}}}` | FAIL | built-in clobber |
| A4 | Frontmatter parseable (`---` delimiters) | FAIL | malformed |
| A5 | Frontmatter has `name` key | FAIL | missing |
| A6 | Frontmatter has `description` key | FAIL | missing |
| A7 | Frontmatter has `mode` key | FAIL | missing |
| A8 | `mode` value in `{{{modes}}}` | FAIL | invalid mode |

---

## commands Suite — Exact Checks

Source: `verify.py:_verify_commands`

| # | Check | Level | Trigger |
|---|---|---|---|
| C1 | `.opencode/command/` directory exists | FAIL | missing |
| C2 | No `init.md` file (clobbers OC `/init`) | FAIL | init.md present |
| C3 | Every `bin/<script>.sh` reference in `ALLOWED_BIN_WRAPPERS` | FAIL | dead reference |

**Allowed bin wrappers:** `{{{wrappers}}}`

**Bin reference regex:** `(?:\\./)?bin/([A-Za-z0-9_.-]+\\.sh)`

---

## Exit Contract (R-020)

| Condition | Exit code |
|---|---|
| `error_count == 0` (warnings allowed) | 0 |
| `error_count > 0` (any FAIL finding) | 1 |

Finding levels: `OK` / `WARN` / `FAIL`. Output format: `[OK]` / `[WARN]` / `[FAIL]` prefixes.
"""


def main() -> int:
    content = generate()
    os.makedirs(os.path.dirname(_OUTPUT), exist_ok=True)
    with open(_OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Generated: {os.path.relpath(_OUTPUT, _ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
