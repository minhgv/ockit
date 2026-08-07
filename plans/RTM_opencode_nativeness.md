# RTM: opencode_nativeness

> **Status:** Draft  
> **Author:** Planner Agent (ba-expert)  
> **Date:** 2026-08-07  
> **Parent SPEC:** `plans/SPEC_opencode_nativeness.md`  
> **Companions:** `plans/ACM_opencode_nativeness.md`, `plans/NFR_opencode_nativeness.md`, `plans/DFD_opencode_nativeness.md`

---

## Requirement Traceability Matrix

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Implement real `ockit verify`: audit SPEC_TEMPLATE + active `plans/SPEC_*.md` for RTM / Edge Case / 3-State sections; exit 1 on FAIL | Variant-A#1 + agy-kit `validate-traceability.sh` | P0 | `src/ockit/verify.py`, `src/ockit/cli.py` | `tests/unit/test_verify.py::test_r001_verify_template_ok` | `tests/qa-evidence/cli/verify_pass.log` | Pending |
| R-002 | `ockit verify` audits BA-QA suite (skills mirror, SPEC_TEMPLATE RTM/ACM/NFR/DFD markers) — absorbs `validate-phase10-ba-qa.sh` logic | Variant-B + DoD | P0 | `src/ockit/verify.py` | `tests/unit/test_verify.py::test_r002_ba_qa_suite` | `tests/qa-evidence/cli/verify_ba_qa.log` | Pending |
| R-003 | Implement real `ockit sync`: drift-detect active `.opencode/{agent,command,plugin,skill}` vs packaged templates; `--check` exit 1 on drift; `--sync` write templates ← active | Variant-A#1 stub + `sync_templates.py` | P0 | `src/ockit/sync.py`, `src/ockit/cli.py` | `tests/unit/test_sync.py::test_r003_sync_check_drift` | `tests/qa-evidence/cli/sync_check.log` | Pending |
| R-004 | Move templates into package: `src/templates/` → `src/ockit/templates/`; fix `pyproject.toml` package-data; installer resolves via `importlib.resources` / `Path(__file__).parent / "templates"` | Variant-A#2 | P0 | `src/ockit/templates/**`, `pyproject.toml`, `src/ockit/installer.py`, `src/ockit/cli.py` | `tests/unit/test_installer.py::test_r004_templates_packaged` | `tests/qa-evidence/cli/pip_install_init.log` | Pending |
| R-005 | `ockit init` copies packaged templates into `--target/.opencode/`; supports `--force`, `--dry-run`; writes root `AGENTS.md` from template when missing | Variant-A#2 + B init | P0 | `src/ockit/installer.py`, `src/ockit/cli.py` | `tests/unit/test_installer.py::test_r005_init_copies` | `tests/qa-evidence/cli/init_target.log` | Pending |
| R-006 | Path safety: `--target` must resolve inside CWD or explicit allowlist; reject `..`, absolute escape outside intended root, symlink escape | Security + ACM | P0 | `src/ockit/validators.py`, `src/ockit/installer.py`, `src/ockit/cli.py` | `tests/unit/test_validators.py::test_r006_target_traversal` | `tests/qa-evidence/cli/init_traversal_deny.log` | Pending |
| R-007 | Init idempotent: second `ockit init` without `--force` skips existing files, exit 0, reports skipped count | Variant-A + ACM | P0 | `src/ockit/installer.py` | `tests/unit/test_installer.py::test_r007_init_idempotent` | `tests/qa-evidence/cli/init_idempotent.log` | Pending |
| R-008 | Agent modes: `orchestrator.md` stays `mode: primary`; `planner/coder/reviewer/qa` set `mode: subagent`; stop shipping `explore.md`/`general.md`/`compaction.md` that clobber OC built-ins | Variant-A#3 | P0 | `src/ockit/templates/agent/*.md`, `.opencode/agent/*.md` | `tests/unit/test_agents_frontmatter.py::test_r008_modes` | `tests/qa-evidence/agents/mode_audit.log` | Pending |
| R-009 | Create root `AGENTS.md` (project rules) + ship as init template | Variant-A#4 | P0 | `AGENTS.md`, `src/ockit/templates/AGENTS.md` | `tests/unit/test_installer.py::test_r009_agents_md` | `tests/qa-evidence/cli/agents_md_present.log` | Pending |
| R-010 | Defer `WorktreeManager` CLI wiring: document DEFERRED; no new subcommand this release; keep module importable | Variant-A#5 | P2 | `src/ockit/worktree.py`, `plans/SPEC_opencode_nativeness.md` §1.1 Non-Goals | `tests/unit/test_worktree.py::test_r010_importable` | N/A (defer note) | Pending |
| R-011 | Thin compat wrappers in `bin/`: `validate-traceability.sh` → `exec ockit verify`; `validate-phase10-ba-qa.sh` → `exec ockit verify --suite ba-qa` | DoD + B strategy | P0 | `bin/validate-traceability.sh`, `bin/validate-phase10-ba-qa.sh` | `tests/unit/test_bin_wrappers.py::test_r011_wrappers` | `tests/qa-evidence/bin/wrapper_exit.log` | Pending |
| R-012 | Port `scan-dependencies.sh` → `ockit scan-deps` (slopsquat patterns, unpinned warn); optional thin `bin/scan-dependencies.sh` wrapper | Variant-B | P0 | `src/ockit/scan_deps.py`, `src/ockit/cli.py`, `bin/scan-dependencies.sh` | `tests/unit/test_scan_deps.py::test_r012_slopsquat` | `tests/qa-evidence/cli/scan_deps.log` | Pending |
| R-013 | Extend `ockit doctor` with agy-doctor checks: git repo, AGENTS.md present, agent frontmatter valid, plugin files, skill dirs, command files, optional gitleaks/trufflehog warn, node optional | Variant-B doctor | P0 | `src/ockit/doctor.py`, `src/ockit/cli.py` | `tests/unit/test_doctor.py::test_r013_doctor_agents_md` | `tests/qa-evidence/cli/doctor_full.log` | Pending |
| R-014 | Fold `validate-agents` + `validate-workflows-sync` into `ockit verify --suite agents` and `--suite commands` (frontmatter keys, required command set, no dead `bin/*.sh` refs after nativization) | Variant-B migrate | P0 | `src/ockit/verify.py` | `tests/unit/test_verify.py::test_r014_agents_commands_suite` | `tests/qa-evidence/cli/verify_agents_cmds.log` | Pending |
| R-015 | Rewrite command MDs: replace `./bin/<script>.sh` with `!ockit <cmd>` shell blocks; drop `safe-agent-run.sh` in favor of OC `agent:` / `subtask:` frontmatter | Variant-B nativization | P0 | `.opencode/command/*.md`, `src/ockit/templates/command/*.md` | `tests/unit/test_commands_native.py::test_r015_no_dead_bin_refs` | `tests/qa-evidence/commands/native_audit.log` | Pending |
| R-016 | Rename slash `/init` → `/ockit-init` (file `ockit-init.md`); body calls `!ockit init`; remove or redirect old `init.md` | Variant-B#5 | P0 | `.opencode/command/ockit-init.md`, delete/redirect `init.md` | `tests/unit/test_commands_native.py::test_r016_ockit_init` | `tests/qa-evidence/commands/ockit_init.log` | Pending |
| R-017 | Portable `opencode.json` template: strip personal absolute paths (`/Users/giapminh79/...`), personal provider apiKey placeholders, enable only ockit local plugins by default; document optional MCP | Variant-B#6 | P0 | `src/ockit/templates/opencode.json`, `.opencode/opencode.json` (dev may keep local overrides gitignored pattern) | `tests/unit/test_portable_config.py::test_r017_no_homedir` | `tests/qa-evidence/config/portable_scan.log` | Pending |
| R-018 | Merge `check-path-boundaries` residual checks into `ockit-quality-gate.js` + Python `validators.py` (symlink escape, forbidden `.env`/`.git`/`.ssh`) | Variant-B plugin | P1 | `.opencode/plugin/ockit-quality-gate.js`, `src/ockit/templates/plugin/ockit-quality-gate.js`, `src/ockit/validators.py` | `tests/unit/test_validators.py::test_r018_symlink_escape` | `tests/qa-evidence/plugin/quality_gate.log` | Pending |
| R-019 | `safe-pipeline.md` uses native OC subtask isolation (`subtask: true` / agent frontmatter) instead of `safe-agent-run.sh`; checkpoint via git stash/commit only | Variant-B#3 | P0 | `.opencode/command/safe-pipeline.md`, templates twin | `tests/unit/test_commands_native.py::test_r019_safe_pipeline` | `tests/qa-evidence/commands/safe_pipeline.log` | Pending |
| R-020 | `ockit verify` exit contract: 0 = pass (warns OK), 1 = errors; structured stdout sections `[OK]/`/`[WARN]`/`[FAIL]` | NFR + CLI UX | P0 | `src/ockit/verify.py` | `tests/unit/test_verify.py::test_r020_exit_codes` | `tests/qa-evidence/cli/verify_exit.log` | Pending |
| R-021 | `ockit sync` default mode = `--check` when neither flag; require explicit `--sync` to write (safer than agy-kit default-write) | Safety decision | P1 | `src/ockit/sync.py`, `src/ockit/cli.py` | `tests/unit/test_sync.py::test_r021_default_check` | `tests/qa-evidence/cli/sync_default.log` | Pending |
| R-022 | Partial-failure atomicity: init uses per-file copy; on mid-copy interrupt, re-run is safe (idempotent); manifest of copied files printed | ACM interrupt | P1 | `src/ockit/installer.py` | `tests/unit/test_installer.py::test_r022_partial_rerun` | `tests/qa-evidence/cli/init_partial.log` | Pending |
| R-023 | Doctor expected inventories match post-nativization reality (5 custom agents, 4 plugins, skills list, commands include `ockit-init` not bare `init`) | Consistency | P0 | `src/ockit/doctor.py` | `tests/unit/test_doctor.py::test_r023_inventory` | `tests/qa-evidence/cli/doctor_inventory.log` | Pending |
| R-024 | README accuracy: document real CLI surface (`init`, `doctor`, `verify`, `sync`, `scan-deps`); paths `.opencode/agent` singular; no claim of missing features | Variant-A fidelity | P1 | `README.md` | N/A (doc review) | `tests/qa-evidence/docs/readme_cli.log` | Pending |
| R-025 | Unit tests + destructive harness cover path traversal, null target, concurrent init race, portable-config leak scan | ACM + QA | P0 | `tests/unit/test_*.py` | self | `tests/qa-evidence/destructive/report.json` | Pending |
| R-026 | Optional thin wrappers only for scripts still referenced by external DoD/CI: `validate-traceability.sh`, `validate-phase10-ba-qa.sh`, `scan-dependencies.sh`; do NOT restore full 20-script bin surface | Scope control | P1 | `bin/*.sh` (3 wrappers max) | `tests/unit/test_bin_wrappers.py` | `tests/qa-evidence/bin/surface.log` | Pending |
| R-027 | Provenance: wrappers and Python ports cite agy-kit source script name in file header comment | Audit | P2 | all new/port files headers | grep CI check | N/A | Pending |
| R-028 | CLI argparse: `verify [--suite {all,traceability,ba-qa,agents,commands}]`; `sync [--check|--sync]`; `scan-deps`; `init --target --lang --force --dry-run` | Interface | P0 | `src/ockit/cli.py` | `tests/unit/test_cli.py::test_r028_argparse` | `tests/qa-evidence/cli/help.log` | Pending |

---

## Coverage Summary

| Priority | Count | IDs |
|----------|------:|-----|
| P0 | 20 | R-001–R-009, R-011–R-017, R-019–R-020, R-023, R-025, R-028 |
| P1 | 6 | R-018, R-021–R-022, R-024, R-026 |
| P2 | 2 | R-010, R-027 |
| **Total** | **28** | R-001 … R-028 |

## Source → Requirement Map

| Source artefact | Requirements |
|-----------------|--------------|
| Variant A fidelity | R-001, R-003–R-010, R-024 |
| Variant B nativization | R-002, R-011–R-019, R-021, R-026–R-028 |
| Security / ACM | R-006, R-017–R-018, R-022, R-025 |
| DoD template §8 | R-011, R-002 |

## Out-of-Scope (explicit non-trace)

- Full `safe-agent-run.sh` worktree isolation CLI (deferred R-010)
- Restoring unused agy-kit scripts: `synthesize-skill.sh`, `fix_linter.py` (logic partially in plugin), `run-destructive-tests.sh`, `verify-eval-harness.sh`, `validate-brainstorm-skills.sh`, `agy-pipeline.sh`
- Changing OpenCode core / upstream built-in agent implementations
