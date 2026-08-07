# RTM: token_monitor_hardening

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_hardening.md`
> **Companions:** `plans/ACM_token_monitor_hardening.md`, `plans/NFR_token_monitor_hardening.md`, `plans/DFD_token_monitor_hardening.md`
> **Extends:** `plans/SPEC_token_monitor_plugin.md` (APPROVED port) — parent requirement IDs referenced in Source, not duplicated.

---

## Requirement Traceability Matrix

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Guard `msg.time` access in `aggregateMessage` with optional chaining (`msg.time?.completed`) so an event payload missing `time` cannot throw TypeError inside the `message.updated` handler (schema drift / older API) | Post-merge review P3-1; extends parent R-013 (ACM E-002) | P1 | `.opencode/plugin/token-monitor/token-state.ts` | `.opencode/plugin/token-monitor/index.test.ts::createTokenStore + aggregateMessage::skips messages where time is undefined (hardening P3-1)` | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-002 | Delete the `stepModels` entry for an `assistantMessageID` in the `session.next.step.ended` handler after successful lookup so the map holds only in-flight steps and cannot grow one entry per completed step for the whole session | Post-merge review P3-2a; extends parent R-015 | P1 | `.opencode/plugin/token-monitor/index.ts` | `.opencode/plugin/token-monitor/index.integration.test.ts::Token Monitor Plugin Module` (regression: subscriptions + dispose intact) | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-003 | Cap the `seen` dedup set at `MAX_SEEN_ENTRIES = 10000` with FIFO eviction of the oldest entry via an O(1) amortized helper in token-state.ts; first-payload-wins (parent E-016) retained within the cap, relaxed only for replays older than the eviction window | Post-merge review P3-2b; extends parent R-013 (ACM E-016) | P1 | `.opencode/plugin/token-monitor/token-state.ts` | `.opencode/plugin/token-monitor/index.test.ts::hardening: seen dedup cap::caps seen at MAX_SEEN_ENTRIES with FIFO eviction` | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-004 | Isolate all three event handlers (`message.updated`, `session.next.step.started`, `session.next.step.ended`) with try/catch + non-PII `console.error` so one handler failure cannot skip later listeners or crash the host emitter; guard missing `event.properties.model` in `step.started` | Post-merge review P3-3; extends parent R-015 (ACM E-018/E-019) | P1 | `.opencode/plugin/token-monitor/index.ts` | `.opencode/plugin/token-monitor/index.integration.test.ts::Token Monitor Plugin Module` (regression: `tui()` tolerates minimal mock api, registers slot + 3 subscriptions) | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-005 | Add unit tests proving `MAX_MODEL_ENTRIES=50` eviction (51 distinct models → store keeps ≤50 entries, lowest-total-token entry evicted, survivors intact) and composite `modelKey` rows (same modelID under different providers → 2 distinct rows) | Post-merge review P3-4a/4b; closes parent ACM E-023/E-029 coverage gap (claimed ported, never implemented) | P1 | `.opencode/plugin/token-monitor/index.test.ts` | `.opencode/plugin/token-monitor/index.test.ts::hardening: MAX_MODEL_ENTRIES eviction` + `::hardening: composite modelKey` | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-006 | Add unit test proving the `seen` cap: `MAX_SEEN_ENTRIES+1` distinct message ids evict the oldest FIFO entry; within-window duplicates still dedup (return false); evicted-id replay re-counts (documented E-016 relaxation) | Post-merge review P3-4c (optional → implemented); extends parent ACM E-016 | P1 | `.opencode/plugin/token-monitor/index.test.ts` | `.opencode/plugin/token-monitor/index.test.ts::hardening: seen dedup cap` | `tests/qa-evidence/token-monitor/vitest_pass.log` (regenerate) | Pending |
| R-007 | Mirror every modified active file byte-identically into `src/ockit/templates/plugin/token-monitor/` (`token-state.ts`, `index.ts`, `index.test.ts`) so the sync contract stays zero-drift | Parent R-009/R-012 (sync contract) | P0 | `src/ockit/templates/plugin/token-monitor/{token-state.ts,index.ts,index.test.ts}` | `tests/unit/test_token_monitor_manifest.py::test_r009_templates_mirror` + `tests/unit/test_sync.py::test_r012_token_monitor_no_drift` | `tests/qa-evidence/token-monitor/sync_check.log` (regenerate) | Pending |

## Coverage Summary

| Priority | Count | IDs |
|----------|------:|-----|
| P0 | 1 | R-007 |
| P1 | 6 | R-001, R-002, R-003, R-004, R-005, R-006 |
| P2 | 0 | — |
| **Total** | **7** | R-001 … R-007 |

## Source → Requirement Map

| Source artefact | Requirements |
|-----------------|--------------|
| Post-merge security/quality review finding P3-1 (`token-state.ts:117` unguarded `msg.time.completed`) | R-001 |
| Post-merge security/quality review finding P3-2a (`stepModels` unbounded across session) | R-002 |
| Post-merge security/quality review finding P3-2b (`seen` set unbounded across session) | R-003 |
| Post-merge security/quality review finding P3-3 (no try/catch in 3 handlers; unguarded `p.model.providerID`) | R-004 |
| Post-merge security/quality review finding P3-4a/4b (no eviction / composite-key tests) | R-005 |
| Post-merge security/quality review finding P3-4c (no seen-cap test) | R-006 |
| Parent SPEC_token_monitor_plugin.md R-009/R-012 mirror + sync contract | R-007 |
| Constitution Art.9.2 (semantic invariance), Art.7.3 (graceful degradation), Art.1 (no secret leakage) | R-001, R-003, R-004 |

## Out-of-Scope (explicit non-trace)

- Rewriting token-monitor aggregation/render/formatter logic — hardening is DEFENSIVE GUARDS only (parent SPEC non-goal #5 deviation documented in `plans/SPEC_token_monitor_hardening.md` §1.1).
- Changing `index.integration.test.ts` — 4 integration tests stay verbatim; handler throw-path isolation is verified by code review + integration regression (map-bounding is masked by shared `seen` dedup in black-box tests).
- Modifying `tests/unit/test_token_monitor_manifest.py` — existing manifest tests are the enforcement gate; no changes needed (`console.error` does not trip R-008/R-017 forbidden patterns).
- Adding new dependencies, changing `package.json` / `tsconfig.json` / `vitest.config.ts` / `tui.json`, or touching `src/ockit/*.py`.
- Changing `MAX_MODEL_ENTRIES` (stays 50) or the `createTokenStore()` return shape `{ models, seen, getModels, _setModels }`.
- Fixing other P3 findings outside the 4 listed (none exist in review scope).
