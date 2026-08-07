# ACM: token_monitor_hardening — 12-Dimensional Edge Case Matrix

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_hardening.md`
> **Domain adaptation:** In-process TUI plugin — no HTTP, no DB, no network. Delta matrix over `plans/ACM_token_monitor_plugin.md` (E-001..E-032 baseline): only NEW hardening edges are enumerated here; untouched dimensions remain covered by the parent baseline edges, which the 48 ported + 4 integration tests enforce.

---

## Dimension Mapping (TUI Plugin Domain)

| # | Classic Dimension | TUI Plugin Adaptation |
|---|-------------------|-----------------------|
| 1 | Null / Missing | SDK event payloads missing `time` / `model` / `properties` (cast without runtime validation) |
| 2 | Precision Loss | Cost/token aggregation in floating point — untouched by hardening (parent E-005..E-007 baseline) |
| 3 | Concurrency | `message.updated` + `session.next.step.ended` race for same `assistantMessageID` — untouched (parent E-008..E-011 baseline) |
| 4 | Rate Limit | Rapid event stream — untouched (parent E-012..E-013 baseline) |
| 5 | Schema Drift | SDK v2 event shape drift — hardening adds null-guards where the parent skipped only `tokens`/`time.completed` |
| 6 | Idempotency | Duplicate message id replay — hardening bounds the dedup window (seen cap); first-payload-wins relaxed beyond cap |
| 7 | Partial Failure | One event handler throws — hardening isolates handlers with try/catch so later listeners + slot survive |
| 8 | Security Fallback | Plugin load failure, missing deps, host isolation — untouched (parent E-020..E-022 baseline) |
| 9 | Context Overflow | >50 distinct model keys — eviction was implemented but UNTESTED (parent E-023 gap); hardening adds tests |
| 10 | Resource Leak | Event subscriptions, `stepModels` map, `seen` set, polling on dispose — hardening bounds stepModels + seen |
| 11 | Tenant Leak | Composite `modelKey` collision (`openai/claude` vs `anthropic/claude`) — was claimed but UNTESTED (parent E-029 gap); hardening adds tests |
| 12 | Task Interrupt | SIGINT, TUI reload, plugin unload mid-aggregation — untouched (parent E-030..E-032 baseline) |

---

## 12-Dimensional Edge Case Matrix — Hardening Delta (6 columns)

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID | Req |
|---------|----------------|---------------|------------------------|---------|-----|
| E-001 | 1. Null / Missing | `aggregateMessage` invoked with `time: undefined` (payload cast from `event.properties?.info` with no runtime validation; sdk `v2/types` says `time` required but schema drift / older API omits it) | `if (!msg.time?.completed)` short-circuits to `undefined` → returns `false`; store unchanged; **no TypeError**; handler survives | T-EDGE-H01 | R-001 |
| E-002 | 1. Null / Missing | `session.next.step.started` payload missing `event.properties.model` (or `event.properties` entirely) | optional-chain guard `p?.assistantMessageID` / `model?.providerID` / `model?.id` → handler returns silently; **no throw**; no `stepModels` entry created; try/catch catches any residual | T-EDGE-H02 | R-004 |
| E-003 | 7. Partial Failure | `message.updated` handler throws an unexpected error mid-execution | try/catch logs one non-PII line `[token-monitor] message.updated handler failed: <error message>` to console.error; later listeners + `sidebar_content` slot render unaffected (Node-style emitter isolation restored) | T-EDGE-H03 | R-004 |
| E-004 | 10. Resource Leak | 100k steps complete across a long session — `stepModels` entries for completed steps | each `session.next.step.ended` deletes its entry after successful lookup → map bounded to concurrent in-flight steps (~session depth), **not** session length | T-EDGE-H04 | R-002 |
| E-005 | 10. Resource Leak | `step.started` fires but matching `step.ended` never arrives (interrupted step) | entry stays until `onDispose` clears the map — bounded by max in-flight steps; documented acceptable (dispose clears) | T-EDGE-H05 | R-002 |
| E-006 | 9. Context Overflow | 51 distinct model keys: 49 high-token models + `lowest` (1 token) fill the store to 50; 51st key `extra` arrives | `MAX_MODEL_ENTRIES=50` eviction removes `lowest` (lowest total tokens among the 50 at insert time); 50 survivors (`extra` + 49 high) intact with unchanged counts; `getModels()` length == 50 | T-EDGE-H06 | R-005 |
| E-007 | 11. Tenant / Cross-project Leak | Same modelID `claude` aggregated under providers `openai` and `anthropic` | composite `modelKey` (`providerID/modelID`) → 2 distinct `PerModelTotals` rows, independent counts (extends parent E-029 which was claimed ported but never implemented) | T-EDGE-H07 | R-005 |
| E-008 | 6. Idempotency | `MAX_SEEN_ENTRIES + 1` distinct message ids aggregated (same model, distinct ids); then replay evicted oldest `m0` and in-window `m10000` | `m0` re-counts (`aggregateMessage` → `true`, first-payload-wins relaxed beyond cap — documented E-016 relaxation for replays older than the window); `m10000` returns `false` (dedup intact); store keeps 1 model row, messageCount reflects re-count | T-EDGE-H08 | R-006 |

---

## Dimension Coverage Checklist

Every dimension covered — new hardening edge(s) listed, untouched dimensions covered by parent ACM baseline (still enforced by the 48 ported + 4 integration tests, which must pass verbatim):

| Dim | Hardening Edges | Parent Baseline Edges (unchanged) | Covered |
|-----|----------------|-----------------------------------|:-------:|
| 1 Null/Missing | E-001, E-002 | E-001..E-004 | Yes |
| 2 Precision Loss | — | E-005..E-007 (no code path touched) | Yes |
| 3 Concurrency | — | E-008..E-011 (no code path touched) | Yes |
| 4 Rate/Burst | — | E-012..E-013 (no code path touched) | Yes |
| 5 Schema drift | E-001, E-002 (guards) | E-014..E-015 | Yes |
| 6 Idempotency | E-008 | E-016..E-017 | Yes |
| 7 Partial failure | E-003 | E-018..E-019 | Yes |
| 8 Security | — | E-020..E-022 (no code path touched) | Yes |
| 9 Scale | E-006 | E-023..E-024 | Yes |
| 10 Resource leak | E-004, E-005 | E-025..E-027 | Yes |
| 11 Tenant/Cross-project leak | E-007 | E-028..E-029 | Yes |
| 12 Interrupt | — | E-030..E-032 (no code path touched) | Yes |

**Total hardening edges:** 8 (E-001 … E-008); parent baseline 32 (E-001 … E-032) remain enforced.

---

## Test ID → Test Mapping

| Test ID | Test location | Status |
|---------|--------------|--------|
| T-EDGE-H01 | `index.test.ts::createTokenStore + aggregateMessage` — new `it("skips messages where time is undefined (hardening P3-1)")` | New (append-only) |
| T-EDGE-H02 | Static: code review of optional-chain guard in `index.ts` step.started handler + `npm --prefix .opencode run type-check` | Code review |
| T-EDGE-H03 | Static: code review of try/catch isolation in `index.ts` + integration regression (`tui()` minimal mock api resolves) | Code review + regression |
| T-EDGE-H04 | Static: code review of `stepModels.delete` in step.ended + integration regression (no double-count path intact) | Code review + regression |
| T-EDGE-H05 | Static: code review (delete-on-ended bounds map; dispose clears remainder) | Code review |
| T-EDGE-H06 | `index.test.ts::hardening: MAX_MODEL_ENTRIES eviction` — new describe | New |
| T-EDGE-H07 | `index.test.ts::hardening: composite modelKey` — new describe | New |
| T-EDGE-H08 | `index.test.ts::hardening: seen dedup cap` — new describe | New |

> **Note:** T-EDGE-H02/H03/H04/H05 are marked code-review + regression because the private handler internals are not observable black-box through the ported integration mock (the shared `seen` dedup masks the `stepModels` delete). The unit-verifiable surface (E-001, E-006, E-007, E-008) is covered by new vitest cases.
