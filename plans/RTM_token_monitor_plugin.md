# RTM: token_monitor_plugin

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_plugin.md`
> **Companions:** `plans/ACM_token_monitor_plugin.md`, `plans/NFR_token_monitor_plugin.md`, `plans/DFD_token_monitor_plugin.md`

---

## Requirement Traceability Matrix

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Copy token-monitor core modules verbatim into `.opencode/plugin/token-monitor/` (config.ts, index.ts, lifecycle.ts, solid-runtime.ts, store-runtime.ts, token-state.ts, token-panel.tsx) | Copy goal | P0 | `.opencode/plugin/token-monitor/{config,index,lifecycle,solid-runtime,store-runtime,token-state}.ts`, `token-panel.tsx` | `tests/unit/test_token_monitor_manifest.py::test_r001_core_files_present` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-002 | Create `.opencode/tui.json` with `"plugin": ["./plugin/token-monitor"]` so TUI host loads the plugin | Source `.opencode/tui.json` | P0 | `.opencode/tui.json` | `tests/unit/test_token_monitor_manifest.py::test_r002_tui_json_entry` | `tests/qa-evidence/token-monitor/tui_json.log` | Passed |
| R-003 | Bump `@opencode-ai/plugin` to `^1.18.12`; add runtime deps `solid-js@1.9.12`, `@opentui/core@0.4.5`, `@opentui/solid@0.4.5` | Dep analysis (installed 1.14.40 lacks sdk `v2/types` export) | P0 | `.opencode/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r003_dependencies_pinned` | `tests/qa-evidence/token-monitor/npm_install.log` | Passed |
| R-004 | Add dev deps `vitest`, `typescript`, `@types/node`, `bun-types`; add `test` + `type-check` npm scripts | Test infra gap | P1 | `.opencode/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r004_devdeps_and_scripts` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |
| R-005 | Port `index.test.ts` + `index.integration.test.ts` verbatim; suite passes under vitest | Test copy goal | P0 | `.opencode/plugin/token-monitor/index.test.ts`, `index.integration.test.ts` | `.opencode/plugin/token-monitor/index.test.ts` (29+ cases) | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-006 | Add `.opencode/vitest.config.ts` with `include: ["plugin/**/*.test.ts"]` | Vitest config gap | P1 | `.opencode/vitest.config.ts` | `tests/unit/test_token_monitor_manifest.py::test_r006_vitest_config` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |
| R-007 | Add `.opencode/tsconfig.json` (noEmit, moduleResolution bundler) + `.opencode/plugin/tsconfig.typecheck.json` extending it, including `token-monitor/**/*.ts(x)` | Type-check infra gap | P1 | `.opencode/tsconfig.json`, `.opencode/plugin/tsconfig.typecheck.json` | `tests/unit/test_token_monitor_manifest.py::test_r007_tsconfig` | `tests/qa-evidence/token-monitor/typecheck.log` | Passed |
| R-008 | Strip TEMPORARY debug logging block from copied `index.ts` (debug-only `/tmp/token-monitor-debug.log`, source comment "Remove before finalizing") | Source TODO + portability (Constitution Art.9.1) | P1 | `.opencode/plugin/token-monitor/index.ts` | `tests/unit/test_token_monitor_manifest.py::test_r008_no_debug_log` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-009 | Mirror all 9 plugin files into `src/ockit/templates/plugin/token-monitor/` | Scaffold goal (ockit AGENTS.md: templates live in `src/ockit/templates/`) | P0 | `src/ockit/templates/plugin/token-monitor/*` | `tests/unit/test_token_monitor_manifest.py::test_r009_templates_mirror` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-010 | Add `src/ockit/templates/tui.json` mirroring active `.opencode/tui.json` | Scaffold goal | P0 | `src/ockit/templates/tui.json` | `tests/unit/test_token_monitor_manifest.py::test_r010_templates_tui_json` | `tests/qa-evidence/token-monitor/sync_check.log` | Passed |
| R-011 | Add `src/ockit/templates/package.json` declaring plugin runtime deps so `ockit init` targets can `npm install` | Scaffold dep gap | P1 | `src/ockit/templates/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r011_templates_package_json` | `tests/qa-evidence/token-monitor/npm_install.log` | Passed |
| R-012 | `ockit sync --check` reports zero drift for `.opencode/plugin/token-monitor`, `.opencode/tui.json`, `.opencode/package.json` vs templates | ockit AGENTS.md sync rule | P0 | `.opencode/plugin/token-monitor/**`, `.opencode/tui.json`, `src/ockit/templates/**` | `tests/unit/test_sync.py::test_r012_token_monitor_no_drift` | `tests/qa-evidence/token-monitor/sync_check.log` | Passed |
| R-013 | Token aggregation correctness: per-model input/output/cache-read/cache-write/reasoning/cost/messageCount; dedup by message id; getModels sorted by total tokens desc | Ported tests | P0 | `.opencode/plugin/token-monitor/token-state.ts` | `index.test.ts::aggregateMessage` (8 cases) + `aggregateStep` (6 cases) + `getModels ordering` | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-014 | Poll interval clamped 5s–300s default 30s; `startPolling` honors AbortSignal and cleans up | Ported tests | P1 | `.opencode/plugin/token-monitor/config.ts`, `lifecycle.ts` | `index.test.ts::parsePollInterval` (7 cases) + `startPolling` (3 cases) | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-015 | TUI module contract: default export `{ id, tui }`; registers `sidebar_content`; subscribes `message.updated` + `session.next.step.started/ended`; onDispose cleanup | Ported integration tests | P0 | `.opencode/plugin/token-monitor/index.ts` | `index.integration.test.ts` (4 cases) | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-016 | Formatters round display only; store keeps full precision (cost 0.0000003 → `$0.00`, token K/M suffixes, percent no-NaN) | Ported tests | P1 | `.opencode/plugin/token-monitor/token-panel.tsx` | `index.test.ts::formatToken` (9) + `formatCost` (6) + `formatPercent` (5) | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-017 | No secrets/personal paths/machine-specific pins in plugin or templates (portable `opencode.json`, no leaked config) | ockit AGENTS.md + Constitution Art.1 | P0 | `.opencode/plugin/token-monitor/**`, `src/ockit/templates/**` | `tests/unit/test_no_leaked_config.py` + `test_token_monitor_manifest.py::test_r017_no_leaks` | `tests/qa-evidence/token-monitor/portable_scan.log` | Passed |
| R-018 | Plugin test command documented + runnable: `npm --prefix .opencode test`; `run_tdd` compatibility noted | Usability | P2 | `.opencode/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r018_test_command` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |

## Coverage Summary

| Priority | Count | IDs |
|----------|------:|-----|
| P0 | 10 | R-001, R-002, R-003, R-005, R-009, R-010, R-012, R-013, R-015, R-017 |
| P1 | 7 | R-004, R-006, R-007, R-008, R-011, R-014, R-016 |
| P2 | 1 | R-018 |
| **Total** | **18** | R-001 … R-018 |

## Source → Requirement Map

| Source artefact | Requirements |
|-----------------|--------------|
| Source plugin `/Users/giapminh79/code/GitHub/ducgv-ai-code-forge/.opencode/plugin/token-monitor/` | R-001, R-005, R-008, R-013, R-014, R-015, R-016 |
| Source `.opencode/tui.json` | R-002, R-010 |
| Source `.opencode/package.json` (deps: @opencode-ai/plugin 1.18.12, solid-js 1.9.12, @opentui/core 0.4.5, @opentui/solid 0.4.5) | R-003, R-004, R-011 |
| Source `.opencode/tsconfig.json` + `plugin/tsconfig.typecheck.json` | R-007 |
| Source root `vitest.config.ts` | R-006 |
| ockit AGENTS.md (templates in `src/ockit/templates/`, no leaked config, TDD) | R-009, R-010, R-011, R-017, R-018 |
| ockit `sync.py` drift contract | R-012 |
| Ported test suites | R-013, R-014, R-015, R-016 |

## Out-of-Scope (explicit non-trace)

- Modifying `/Users/giapminh79/code/GitHub/ducgv-ai-code-forge/` — source is READ-ONLY.
- Changing ockit Python implementation (`src/ockit/*.py`) — not required; package-data glob already ships new templates.
- Altering existing `.opencode/plugin/ockit-*.js` plugins or `opencode.json` `plugin` array — token-monitor registers via `tui.json` only.
- Compiling TS → JS — opencode TUI runtime (Bun) loads TS natively; no build step.
- Rewriting token-monitor logic beyond stripping TEMPORARY debug block (R-008).
- Adding network CVE scanning, telemetry, or bundled `node_modules`.
