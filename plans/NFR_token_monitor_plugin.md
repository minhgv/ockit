# NFR: token_monitor_plugin

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_plugin.md`

---

## Non-Functional Requirements

| NFR ID | Category | Target Metric / Floor Threshold | Verification Method | Related Req |
|--------|----------|--------------------------------|---------------------|-------------|
| NFR-001 | Reliability | 0 crashes on malformed/missing event payloads (tokens/time.completed absent) | ported `index.test.ts` skip-cases + integration mock api | R-013, R-015 |
| NFR-002 | Coverage Floor | Ported vitest suite 100% green (≥29 tests, ≥1 per edge case E-001..E-032) | `npm --prefix .opencode test` | R-005 |
| NFR-003 | Error Clarity | Plugin never emits raw errors to user; best-effort silent skip per Constitution Art.7.3 | unit assert on skip paths (returns false, no throw) | R-013 |
| NFR-004 | Idempotency | Duplicate message id / assistantMessageID → identical store state on N retries | ported dedup tests (aggregateMessage+aggregateStep shared `seen`) | R-013 |
| NFR-005 | Portability | Zero hardcoded paths/secrets/machine pins in shipped plugin + templates; debug log stripped | `test_no_leaked_config.py` + `test_r017_no_leaks` + `test_r008_no_debug_log` | R-008, R-017 |
| NFR-006 | Compatibility | `@opencode-ai/plugin` `^1.18.12` (sdk `v2/types` export present); `solid-js@1.9.12`; `@opentui/core@0.4.5`; `@opentui/solid@0.4.5` | `test_r003_dependencies_pinned` + `npm install --prefix .opencode` success | R-003 |
| NFR-007 | Reliability | Polling lifecycle: interval cleared on abort/dispose; no zombie timers | ported `startPolling` abort cases (count frozen after abort) | R-014, R-015 |
| NFR-008 | Security | No shell exec, no network egress, no filesystem writes by plugin runtime | static audit (code review) + debug-strip test | R-008, R-017 |
| NFR-009 | Maintainability | `ockit sync --check` zero drift between active `.opencode/plugin/token-monitor`, `.opencode/tui.json` and templates | `test_sync.py::test_r012_token_monitor_no_drift` + manual `ockit sync --check` | R-012 |
| NFR-010 | Compatibility | Existing 4 JS plugins + `opencode.json` plugin array untouched; Python CLI untouched | `pytest tests/ -q` green (existing suite unchanged) | R-017, R-012 |
| NFR-011 | Observability | Store bounded: `MAX_MODEL_ENTRIES=50`, eviction of lowest-token model | ported/edge E-023 test | R-013 |
| NFR-012 | Performance | Per-event aggregation O(1) amortized (map access); render re-evaluates only on signal change (createMemo) | code review (no nested loops in hot path) + reactivity test | R-013, R-015 |
| NFR-013 | Portability | `ockit init --target <dir>` scaffolds functional token-monitor (files + tui.json + package.json) | `test_r009_templates_mirror`, `test_r010_templates_tui_json`, `test_r011_templates_package_json` | R-009, R-010, R-011 |

## Performance Budgets

| Command / Endpoint | p95 ceiling | Notes |
|--------------------|------------:|-------|
| Event handler (`message.updated` / `step.ended`) | < 5 ms | O(1) store map + dedup set |
| Panel re-render (per tick/signal) | < 50 ms | Solid `createMemo` diffing; only repaints changed text nodes |
| Poll tick | 30 s default (5 s min) | bounded by `parsePollInterval` clamp |

## Quality Floors

| Metric | Floor |
|--------|------:|
| Line coverage (token-state.ts, config.ts, lifecycle.ts, token-panel.tsx) | >= 90% via ported suite |
| Ported test cases passing | 100% |
| `ockit sync --check` drift (token-monitor files) | 0 |
| Hardcoded secrets / personal paths | 0 |
| `tsc --noEmit` errors | 0 |

## Explicit Non-Goals (NFR)

- No performance guarantee for the OpenTUI FFI render path — Bun-only, verified manually in opencode TUI (Open Question 5).
- No coverage floor for `index.ts` glue (event wiring) beyond integration mock tests — thin adapter.
- No multi-machine/remote TUI support; plugin is local to the running opencode TUI host.
