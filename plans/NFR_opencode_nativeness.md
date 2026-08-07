# NFR: opencode_nativeness

> **Status:** Draft  
> **Author:** Planner Agent (ba-expert)  
> **Date:** 2026-08-07  
> **Parent SPEC:** `plans/SPEC_opencode_nativeness.md`

---

## Non-Functional Requirements

| NFR ID | Category | Target Metric / Floor Threshold | Verification Method | Related Req |
|--------|----------|--------------------------------|---------------------|-------------|
| NFR-001 | Latency (p95) | `ockit verify` (≤20 SPECs, default suite) < 2.0 s local SSD | `time ockit verify` in QA evidence | R-001 |
| NFR-002 | Latency (p95) | `ockit doctor` < 3.0 s (no network MCP probes) | `time ockit doctor` | R-013 |
| NFR-003 | Latency (p95) | `ockit init` fresh target ≤200 template files < 5.0 s | timed init in tmpdir | R-005 |
| NFR-004 | Latency (p95) | `ockit sync --check` < 3.0 s for default tree | timed sync | R-003 |
| NFR-005 | Latency (p95) | `ockit scan-deps` < 1.0 s (grep-class scan, no network audit) | timed scan-deps | R-012 |
| NFR-006 | Throughput | ≥ 20 sequential `ockit verify` runs/min without FD growth | loop + `lsof` sample | E-010 |
| NFR-007 | Error Rate | CLI false-positive FAIL rate 0% on golden fixture tree | fixture repo under `tests/fixtures/golden_scaffold/` | R-020 |
| NFR-008 | Error Clarity | Every non-zero exit includes 3-part error: What / Context / Fix (stdout or stderr) | unit assert on message shape | Constitution Art.3 |
| NFR-009 | Reliability / Idempotency | 10× repeated init without `--force` → bitwise-identical tree after first | `diff -qr` | R-007 |
| NFR-010 | Packaging | `pip install .` wheel contains `ockit/templates/**`; `importlib.resources` can open `opencode.json` | build wheel + inspect | R-004 |
| NFR-011 | Portability | Zero matches of author home path regex `/Users/[^/]+/` or `C:\\Users\\` inside shipped templates | CI grep gate | R-017 |
| NFR-012 | Portability | Zero hardcoded secrets/apiKey non-placeholder values in templates | secret scan + unit | R-017, R-030 ACM |
| NFR-013 | Compatibility | Python 3.9–3.13 supported; no 3.10-only syntax without guard | tox/pyenv matrix or CI | pyproject |
| NFR-014 | Compatibility | OpenCode command frontmatter remains valid YAML; no unknown required keys that break OC parse | load YAML smoke | R-015 |
| NFR-015 | Security | Path traversal attempts never create files outside resolved safe root | destructive tests | R-006 |
| NFR-016 | Security | Quality-gate plugin deny on sensitive patterns before tool body | plugin unit / integration | R-018 |
| NFR-017 | Maintainability | Dead bin script references in `.opencode/command/*.md` = 0 after nativization | `ockit verify --suite commands` | R-015 |
| NFR-018 | Maintainability | Custom agents clobbering OC built-in names (`explore`,`general`,`compaction`) = 0 in shipped templates | verify agents suite | R-008 |
| NFR-019 | Coverage Floor | ≥ 85% lines, ≥ 70% branches on `src/ockit/{cli,installer,doctor,verify,sync,scan_deps,validators}.py` | `pytest --cov=ockit` | R-025 |
| NFR-020 | MTTR (dev) | Broken init recoverable by re-run ≤ 60 s (no manual cleanup required except optional backup dir) | interrupt+rerun drill | R-022 |
| NFR-021 | Observability | verify/doctor/sync/scan-deps emit section headers + counts (errors, warnings) | stdout contract tests | R-020 |
| NFR-022 | Binary surface | `bin/` contains ≤ 3 thin wrappers; each ≤ 30 lines; only `exec`/call `ockit` | wc + policy test | R-026 |
| NFR-023 | Docs fidelity | README CLI list matches `ockit --help` subcommands 1:1 | scripted diff | R-024 |
| NFR-024 | Dependency hygiene | Runtime deps remain minimal (`jsonschema` only unless justified); no new heavy frameworks for ported shell logic | pyproject review | R-027 |

---

## Performance Budgets (summary)

| Command | p95 ceiling | Notes |
|---------|------------:|-------|
| `verify` | 2 s | Local, ≤20 SPECs |
| `doctor` | 3 s | No network |
| `init` | 5 s | ≤200 files |
| `sync --check` | 3 s | Default tree |
| `scan-deps` | 1 s | Pattern scan only |

## Quality Floors

| Metric | Floor |
|--------|------:|
| Line coverage (core modules) | ≥ 85% |
| Branch coverage (core modules) | ≥ 70% |
| Portable path violations in templates | 0 |
| Dead `./bin/*.sh` refs in commands (except documented wrappers) | 0 |
| Agents with `mode: all` | 0 |
| Shipped agents named explore/general/compaction | 0 |

## Explicit Non-Goals (NFR)

- Network vulnerability DB lookups (OSV/Snyk) in `scan-deps` v1 — pattern-only
- Sub-100ms CLI cold start guarantees
- Multi-tenant SaaS SLOs
