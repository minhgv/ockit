# NFR: token_monitor_hardening

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_hardening.md`
> **Extends:** `plans/NFR_token_monitor_plugin.md` (NFR-001..NFR-013 baseline). Numbering restarts per feature (repo convention).

---

## Non-Functional Requirements

| NFR ID | Category | Target Metric / Floor Threshold | Verification Method | Related Req |
|--------|----------|--------------------------------|---------------------|-------------|
| NFR-001 | Reliability | 0 crashes in any of the 3 event handlers on malformed/missing payloads (`time`, `model`, `properties` absent) | new hardening tests + 4 integration tests regression | R-001, R-004 |
| NFR-002 | Memory bounded | `seen` set ≤ 10,000 entries; `stepModels` map ≤ concurrent in-flight steps (not session length); `models` ≤ 50 entries | seen-cap test (E-008), eviction test (E-006), code review | R-002, R-003, R-005, R-006 |
| NFR-003 | Performance | Per-event aggregation O(1) amortized including FIFO eviction (`seen.values().next()` + `delete`); no new nested loops in hot path | code review of `recordSeen`/`addTokensToModel` hot path + full vitest suite runtime | R-003 |
| NFR-004 | Compatibility | 48 ported vitest tests + 4 integration tests pass verbatim; `createTokenStore()` return shape `{ models, seen, getModels, _setModels }` unchanged; `aggregateMessage`/`aggregateStep` signatures unchanged; `MAX_MODEL_ENTRIES=50` unchanged; only additive export `MAX_SEEN_ENTRIES` | `npm --prefix .opencode test` + `npm --prefix .opencode run type-check` + `pytest tests/ -q` (253 green) | R-001..R-006 |
| NFR-005 | Portability | `console.error` is the only new output sink; zero `/tmp` files, zero debug-log additions; R-008 (`test_r008_no_debug_log`) and R-017 (`test_r017_no_leaks`) stay green | `tests/unit/test_token_monitor_manifest.py` + `test_no_leaked_config.py` | R-004, R-007 |
| NFR-006 | Observability | Handler failures surface as one non-PII line: `[token-monitor] <event-type> handler failed: <error message>` (error message only — never the raw event payload) | code review of all 3 catch blocks | R-004 |
| NFR-007 | Maintainability | Zero sync drift after mirroring modified files into templates | `tests/unit/test_sync.py::test_r012_token_monitor_no_drift` + `test_r009_templates_mirror` | R-007 |

---

## Performance Budgets

| Command / Endpoint | p95 ceiling | Notes |
|--------------------|------------:|-------|
| Event handler (`message.updated` / `step.started` / `step.ended`) | < 5 ms | unchanged from parent; try/catch + optional chaining add no measurable cost; FIFO eviction amortized O(1) |
| seen-cap full eviction cycle (10,001 aggregates) | < 1 s in vitest | single model row, produce() per aggregate |
| Panel re-render (per tick/signal) | < 50 ms | untouched render path (parent NFR-012) |

---

## Quality Floors

| Metric | Floor |
|--------|------:|
| Ported + hardening vitest suite passing | 100% (48 + 4 regression + 4 new hardening) |
| `tsc --noEmit` errors | 0 |
| `ockit sync --check` drift (token-monitor files) | 0 |
| Hardcoded secrets / personal paths / `/tmp` writes | 0 |
| `pytest tests/ -q` (ockit suite) | 253 passed (existing count, no regressions) |

---

## Explicit Non-Goals (NFR)

- No performance guarantee for the OpenTUI FFI render path (Bun-only, manual smoke test — parent Open Question 5).
- No new unit tests for the private `stepModels` delete / try-catch throw paths (masked by shared `seen` dedup; verified by code review + regression — documented in ACM note).
- No coverage floor increase for `index.ts` glue beyond the 4 integration regression tests.
