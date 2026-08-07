# Reference: Verify Contract

> **AUTO-GENERATED from `src/ockit/verify.py` by `scripts/generate_verify_contract.py`.**
> Do NOT edit manually — changes will be overwritten.
> Test `tests/unit/test_verify_contract_fresh.py` enforces freshness.

---

## Suites

`ockit verify --suite {all, traceability, ba-qa, agents, commands}`

| Suite | Checks |
|---|---|
| `all` (default) | Runs all 4 suites below |
| `traceability` | SPEC_TEMPLATE + active SPEC_*.md: RTM table, Edge Case, 3-State Verification |
| `ba-qa` | 4 BA/QA skills mirrored + content markers; SPEC_TEMPLATE Phase 10 sections; agent Phase 10 refs; README present |
| `agents` | .opencode/agent/*.md frontmatter: name/description/mode; mode in {primary, subagent}; no built-in clobber |
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
| T7 | RTM rows missing Unit Test Reference cell | WARN | cell empty or in {N/A, -, None, TBD, TODO, pending} |
| T8 | Each SPEC_*.md has Edge Case section | WARN | string "Edge Case" absent |

**RTM row detection regex:** `^R-\d+` — only rows starting with `R-<number>` are counted.

---

## ba-qa Suite — Exact Checks

Source: `verify.py:_verify_ba_qa`

### BA/QA Skills (4 mandatory)

For each skill in `{ba-expert, qa-auditor, qa-test-gen, qa-reproducer}`:

| # | Check | Level |
|---|---|---|
| B1 | Active copy exists at `.opencode/skill/<name>/SKILL.md` | FAIL |
| B2 | Template copy exists at `templates/skill/<name>/SKILL.md` | FAIL |
| B3 | Active == Template (byte-identical mirror) | FAIL |
| B4 | Content markers present in active copy | FAIL |

**Content markers per skill:**

| Skill | Required markers (ALL must be present) |
|---|---|
| ba-expert | `12-Dimensional`, `Bounded Contexts`, `User Stories`, `Zod` |
| qa-auditor | `audit_summary`, `Runtime Risk Matrix` |
| qa-test-gen | `test_plan`, `Gherkin` |
| qa-reproducer | `reproduction_summary`, `Minimal Reproduction` |

### SPEC_TEMPLATE Phase 10 Sections

| # | Check | Level |
|---|---|---|
| B5 | SPEC_TEMPLATE contains ALL of: `RTM`, `ACM`, `NFR`, `DFD` | FAIL |

### Agent Phase 10 References

For each agent file in `.opencode/agent/`:

| Agent file | Any-of markers | All-of markers |
|---|---|---|
| `planner.md` | `ba-expert` | `12-Dimensional` |
| `coder.md` | `qa-test-gen`, `qa-auditor` | (none) |
| `reviewer.md` | `ba-expert`, `qa-auditor` | `reviewer` |
| `qa.md` | `qa-reproducer`, `qa-test-gen` | (none) |

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
| A3 | Agent name NOT in `{compaction, explore, general}` | FAIL | built-in clobber |
| A4 | Frontmatter parseable (`---` delimiters) | FAIL | malformed |
| A5 | Frontmatter has `name` key | FAIL | missing |
| A6 | Frontmatter has `description` key | FAIL | missing |
| A7 | Frontmatter has `mode` key | FAIL | missing |
| A8 | `mode` value in `{primary, subagent}` | FAIL | invalid mode |

---

## commands Suite — Exact Checks

Source: `verify.py:_verify_commands`

| # | Check | Level | Trigger |
|---|---|---|---|
| C1 | `.opencode/command/` directory exists | FAIL | missing |
| C2 | No `init.md` file (clobbers OC `/init`) | FAIL | init.md present |
| C3 | Every `bin/<script>.sh` reference in `ALLOWED_BIN_WRAPPERS` | FAIL | dead reference |

**Allowed bin wrappers:** `{scan-dependencies.sh, validate-phase10-ba-qa.sh, validate-traceability.sh}`

**Bin reference regex:** `(?:\./)?bin/([A-Za-z0-9_.-]+\.sh)`

---

## Exit Contract (R-020)

| Condition | Exit code |
|---|---|
| `error_count == 0` (warnings allowed) | 0 |
| `error_count > 0` (any FAIL finding) | 1 |

Finding levels: `OK` / `WARN` / `FAIL`. Output format: `[OK]` / `[WARN]` / `[FAIL]` prefixes.
