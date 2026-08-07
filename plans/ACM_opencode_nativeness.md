# ACM: opencode_nativeness — 12-Dimensional Edge Case Matrix

> **Status:** Draft  
> **Author:** Planner Agent (ba-expert)  
> **Date:** 2026-08-07  
> **Parent SPEC:** `plans/SPEC_opencode_nativeness.md`  
> **Domain adaptation:** Scaffold / CLI / template packaging (not multi-tenant SaaS)

---

## Dimension Mapping (Scaffold Domain)

| # | Classic Dimension | Scaffold/CLI Adaptation |
|---|-------------------|-------------------------|
| 1 | Null / Missing | Missing templates dir, empty `--target`, absent SPEC files, missing AGENTS.md |
| 2 | Precision Loss | N/A currency → **path/canonicalization loss** (symlink resolve, trailing slash, Unicode NFKC) |
| 3 | Concurrency | Parallel `ockit init` / `ockit sync` on same target |
| 4 | Rate Limit | Burst CLI invocations (CI matrix); doctor subprocess storms |
| 5 | Schema Drift | `opencode.json` schema version drift; legacy agent frontmatter keys; old command bin refs |
| 6 | Idempotency | Re-run init/sync/verify without side-effect accumulation |
| 7 | Partial Failure | Mid-copy interrupt; half-written tree; verify finds partial SPEC |
| 8 | Security Fallback | Path traversal `--target`; sensitive path write; personal config leak ship |
| 9 | Context Overflow | Huge monorepo walk; oversized opencode.json; thousands of SPEC files |
| 10 | Resource Leak | Temp files from deferred worktree; open file handles during walk |
| 11 | Tenant Leak | **Cross-project leak:** init copies personal absolute paths into foreign repo |
| 12 | Task Interrupt | SIGINT mid-init/sync; incomplete package data after pip install |

---

## 12-Dimensional Edge Case Matrix

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID | Req |
|---------|----------------|---------------|------------------------|---------|-----|
| E-001 | 1. Null / Missing | `ockit init` when packaged `templates/` absent (broken wheel) | Exit 1; error: `What=templates missing; Context=resolved path; Fix=reinstall ockit` | T-EDGE-001 | R-004, R-005 |
| E-002 | 1. Null / Missing | `ockit verify` with no `plans/SPEC_*.md` but valid SPEC_TEMPLATE | Exit 0; `[OK] No active feature SPECs` | T-EDGE-002 | R-001 |
| E-003 | 1. Null / Missing | `ockit doctor` without `.opencode/` | Exit 1; errors list missing config/agents | T-EDGE-003 | R-013 |
| E-004 | 1. Null / Missing | `ockit sync --check` empty templates dir | Exit 1; actionable missing-templates error | T-EDGE-004 | R-003 |
| E-005 | 2. Path Canonicalization | `--target ./foo/../foo` vs `--target foo` | Same resolved dest; no double-nest `.opencode` | T-EDGE-005 | R-006 |
| E-006 | 2. Path Canonicalization | Symlink target pointing outside allowlisted root | Reject; exit 1 path-safety | T-EDGE-006 | R-006, R-018 |
| E-007 | 2. Path Canonicalization | Unicode / NFC-NFD path components in `--target` | Resolve via `realpath`; no crash | T-EDGE-007 | R-006 |
| E-008 | 3. Concurrency | Two parallel `ockit init --force` same target | No corrupt half-files; final tree complete (last-writer-wins OK) OR file lock fails second with clear error | T-EDGE-008 | R-005, R-022 |
| E-009 | 3. Concurrency | Parallel `ockit sync --sync` + edit of active agent | No truncated agent md (write via temp+replace preferred) | T-EDGE-009 | R-003 |
| E-010 | 4. Rate / Burst | 50× `ockit verify` in loop | All complete < NFR budget; no FD exhaustion | T-EDGE-010 | R-001, NFR |
| E-011 | 5. Schema Drift | Active command still references `./bin/validate-traceability.sh` after nativization | `ockit verify --suite commands` FAIL with file:line hint | T-EDGE-011 | R-014, R-015 |
| E-012 | 5. Schema Drift | Agent frontmatter still `mode: all` | `ockit verify --suite agents` FAIL | T-EDGE-012 | R-008, R-014 |
| E-013 | 5. Schema Drift | Shipped `opencode.json` missing `$schema` or invalid JSON | doctor / verify FAIL | T-EDGE-013 | R-017, R-013 |
| E-014 | 5. Schema Drift | Legacy `init.md` present alongside `ockit-init.md` | verify WARN or FAIL (policy: FAIL if both claim /init) | T-EDGE-014 | R-016 |
| E-015 | 6. Idempotency | `ockit init` twice without `--force` | 2nd: 0 overwrites; exit 0; skipped ≥ prior copied | T-EDGE-015 | R-007 |
| E-016 | 6. Idempotency | `ockit verify` twice identical tree | Identical exit code + stable section order | T-EDGE-016 | R-020 |
| E-017 | 6. Idempotency | `ockit sync --check` after clean sync | Exit 0 no drift | T-EDGE-017 | R-003, R-021 |
| E-018 | 7. Partial Failure | Kill -9 during multi-file init copy | Re-run without `--force` completes missing files only | T-EDGE-018 | R-022 |
| E-019 | 7. Partial Failure | SPEC missing RTM but has Edge Case | verify WARN per-file; overall exit 0 if only warns (errors only for template/framework hard fails) | T-EDGE-019 | R-001 |
| E-020 | 7. Partial Failure | `scan-deps` finds clean pyproject but dirty package-lock | FAIL overall if any ecosystem fails | T-EDGE-020 | R-012 |
| E-021 | 8. Security Fallback | `--target /etc/ockit-evil` or `../../../etc` | Deny; exit 1; no write | T-EDGE-021 | R-006 |
| E-022 | 8. Security Fallback | Template contains absolute `/Users/giapminh79/` path | `test_r017` + verify portable scan FAIL pre-release | T-EDGE-022 | R-017 |
| E-023 | 8. Security Fallback | Quality-gate plugin sees path `../.env` | Throw deny before tool execute | T-EDGE-023 | R-018 |
| E-024 | 8. Security Fallback | Init would overwrite existing foreign `.opencode` with `--force` without backup | Policy: with `--force`, write `.opencode_backup_<ts>` first (from init-agy-kit) | T-EDGE-024 | R-005 |
| E-025 | 9. Context / Scale | 500 synthetic SPEC files in plans/ | verify completes within NFR; no OOM | T-EDGE-025 | R-001 |
| E-026 | 9. Context / Scale | Skill tree with 10k tiny files | init/sync walk bounded; skip `node_modules`/`.DS_Store` | T-EDGE-026 | R-003, R-005 |
| E-027 | 10. Resource Leak | doctor subprocess calls (python --version, which) | No zombie procs; use timeout | T-EDGE-027 | R-013 |
| E-028 | 10. Resource Leak | Future worktree create then exception | `remove_worktree` in finally (unit on WorktreeManager even if CLI deferred) | T-EDGE-028 | R-010 |
| E-029 | 11. Cross-Project Leak | Portable template ships `external_directory` allow for author home | Forbidden; must use generic `*` ask or omit personal paths | T-EDGE-029 | R-017 |
| E-030 | 11. Cross-Project Leak | Provider block with real `apiKey` string in template | Forbidden; empty / env-var placeholder only | T-EDGE-030 | R-017 |
| E-031 | 12. Task Interrupt | SIGINT during `ockit sync --sync` | Partial writes via temp+replace leave either old or new full file | T-EDGE-031 | R-003 |
| E-032 | 12. Task Interrupt | pip install wheel missing package-data | doctor/init detect; clear reinstall message | T-EDGE-032 | R-004 |

---

## Dimension Coverage Checklist

| Dim | Edges | Covered |
|-----|------:|:-------:|
| 1 Null/Missing | E-001–E-004 | Yes |
| 2 Path canonicalization | E-005–E-007 | Yes |
| 3 Concurrency | E-008–E-009 | Yes |
| 4 Burst | E-010 | Yes |
| 5 Schema drift | E-011–E-014 | Yes |
| 6 Idempotency | E-015–E-017 | Yes |
| 7 Partial failure | E-018–E-020 | Yes |
| 8 Security | E-021–E-024 | Yes |
| 9 Scale | E-025–E-026 | Yes |
| 10 Resource leak | E-027–E-028 | Yes |
| 11 Cross-project leak | E-029–E-030 | Yes |
| 12 Interrupt | E-031–E-032 | Yes |

**Total edges:** 32 (E-001 … E-032)
