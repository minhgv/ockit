# ACM: token_monitor_plugin — 12-Dimensional Edge Case Matrix

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Parent SPEC:** `plans/SPEC_token_monitor_plugin.md`
> **Domain adaptation:** In-process TUI plugin — no HTTP, no DB, no network. Dimensions map to event-stream, in-memory store, and plugin-lifecycle surfaces.

---

## Dimension Mapping (TUI Plugin Domain)

| # | Classic Dimension | TUI Plugin Adaptation |
|---|-------------------|-----------------------|
| 1 | Null / Missing | SDK event payloads missing `tokens` / `time.completed` / `info` |
| 2 | Precision Loss | Cost aggregation in floating point — display rounding must not corrupt store |
| 3 | Concurrency | `message.updated` + `session.next.step.ended` racing for same `assistantMessageID`; multi-event bursts |
| 4 | Rate Limit | Rapid event stream (many messages/steps per second) overwhelming store/render |
| 5 | Schema Drift | opencode SDK v1→v2 event shape changes; plugin API version mismatch (1.14.40 vs 1.18.12) |
| 6 | Idempotency | Duplicate message id / assistantMessageID replay counted once |
| 7 | Partial Failure | One event handler throws — other handlers + slot render must survive |
| 8 | Security Fallback | Plugin load failure, missing deps, TUI host isolation |
| 9 | Context Overflow | >50 distinct model keys — store eviction strategy |
| 10 | Resource Leak | Event subscriptions, `stepModels` map, polling interval on dispose/abort |
| 11 | Tenant Leak | Multiple sessions / workspaces sharing one plugin instance — store isolation |
| 12 | Task Interrupt | SIGINT, TUI reload, plugin unload mid-aggregation |

---

## 12-Dimensional Edge Case Matrix (6 columns)

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID | Req |
|---------|----------------|---------------|------------------------|---------|-----|
| E-001 | 1. Null / Missing | `aggregateMessage` with `tokens: undefined` | returns false; store unchanged; no crash | T-EDGE-001 | R-013 |
| E-002 | 1. Null / Missing | `aggregateMessage` with `time: { created }` (no `completed`) — streaming in-flight message | returns false; not counted | T-EDGE-002 | R-013 |
| E-003 | 1. Null / Missing | `aggregateStep` with `tokens: undefined` | returns false; no crash | T-EDGE-003 | R-013 |
| E-004 | 1. Null / Missing | `parsePollInterval({ pollIntervalMs: "fast" })` non-number | default 30000 returned | T-EDGE-004 | R-014 |
| E-005 | 2. Precision Loss | 3× cost 0.0000001 accumulated | store = 0.0000003 (full precision); display `$0.00` (round only at display) | T-EDGE-005 | R-016 |
| E-006 | 2. Precision Loss | Cumulative costs 0.0036+0.0004+0.0005+0.0012+0.0022 | monotonic accumulation, closeTo 6dp at each step | T-EDGE-006 | R-013 |
| E-007 | 2. Precision Loss | `formatPercent(10, 0)` total zero | `"0%"` — no NaN/Infinity | T-EDGE-007 | R-016 |
| E-008 | 3. Concurrency | `aggregateMessage(msg-1)` then `aggregateStep(assistantMessageID=msg-1)` | second call returns false; counted once (shared `seen` set) | T-EDGE-008 | R-013 |
| E-009 | 3. Concurrency | `aggregateStep` first then `aggregateMessage` for same id | same dedup; counted once | T-EDGE-009 | R-013 |
| E-010 | 3. Concurrency | `step.started` for model X then `step.ended` (no tokens on started) — model attribution via `stepModels` map | ended attributed to correct model via remembered providerID/modelID | T-EDGE-010 | R-015 |
| E-011 | 3. Concurrency | Multiple models interleaved (claude + gpt-4) | separate `PerModelTotals` rows, independent counts | T-EDGE-011 | R-013 |
| E-012 | 4. Rate Limit / Burst | Rapid fire of many messages in one tick window | all aggregated correctly; render reads latest via tick | T-EDGE-012 | R-015 |
| E-013 | 4. Rate Limit / Burst | Poll interval clamped: 1000 → 5000; 999999 → 300000; NaN → 30000 | clamp boundaries honored | T-EDGE-013 | R-014 |
| E-014 | 5. Schema Drift | `@opencode-ai/sdk/v2/types` shape changes (AssistantMessage fields) | `tsc --noEmit` type-check fails loudly; runtime guards skip missing fields | T-EDGE-014 | R-007 |
| E-015 | 5. Schema Drift | Plugin API version mismatch (installed 1.14.40 lacks `sdk/v2/types`) | dependency bump to `^1.18.12` enforced by manifest test | T-EDGE-015 | R-003 |
| E-016 | 6. Idempotency | Duplicate `aggregateMessage` with same id, different token payload | counted once (first payload wins) | T-EDGE-016 | R-013 |
| E-017 | 6. Idempotency | Duplicate `aggregateStep` same `assistantMessageID` | second returns false | T-EDGE-017 | R-013 |
| E-018 | 7. Partial Failure | `tui()` factory invoked with minimal mock api (no `lifecycle.signal`) | resolves undefined; slot registered; no throw | T-EDGE-018 | R-015 |
| E-019 | 7. Partial Failure | `tui()` invoked with api missing `slots.register` | `undefined` tolerated or guarded; integration test uses complete mock | T-EDGE-019 | R-015 |
| E-020 | 8. Security Fallback | Plugin entry missing from `tui.json` | TUI starts; panel absent; other plugins unaffected | T-EDGE-020 | R-002 |
| E-021 | 8. Security Fallback | Runtime deps missing in `.opencode/node_modules` | documented npm install step; manifest test asserts deps declared | T-EDGE-021 | R-003 |
| E-022 | 8. Security Fallback | Debug log path `/tmp/token-monitor-debug.log` present in shipped source | R-008 strips TEMPORARY debug block; manifest test asserts absence | T-EDGE-022 | R-008 |
| E-023 | 9. Context Overflow | >50 distinct model keys aggregated | store evicts lowest-total-token entry; `MAX_MODEL_ENTRIES=50` honored | T-EDGE-023 | R-013 |
| E-024 | 9. Context Overflow | Single model with very large token counts (≥999950) | `formatToken` → `"1.0M"`; no overflow/NaN | T-EDGE-024 | R-016 |
| E-025 | 10. Resource Leak | AbortSignal aborted mid-polling | interval cleared; no further ticks (count frozen) | T-EDGE-025 | R-014 |
| E-026 | 10. Resource Leak | Signal already aborted before `startPolling` | never fires; cleanup called immediately | T-EDGE-026 | R-014 |
| E-027 | 10. Resource Leak | `onDispose` registered in `tui()` | unsubs event listeners, clears `stepModels`, stops polling | T-EDGE-027 | R-015 |
| E-028 | 11. Tenant / Cross-project Leak | Two `tui()` invocations (two sessions/workspaces) | each has own `createTokenStore()`; no shared state bleed | T-EDGE-028 | R-015 |
| E-029 | 11. Tenant / Cross-project Leak | Model key collision across providers (`gh/claude` vs `openai/claude`) | distinct keys via `providerID/modelID` composite | T-EDGE-029 | R-013 |
| E-030 | 12. Task Interrupt | TUI reload / SIGINT mid-aggregation | `lifecycle.signal` abort → polling stops; dispose clears state | T-EDGE-030 | R-015 |
| E-031 | 12. Task Interrupt | `startPolling` cleanup called twice (idempotent cleanup) | second cleanup no-op; no double clearInterval crash | T-EDGE-031 | R-014 |
| E-032 | 12. Task Interrupt | `ockit sync --check` after template mirror | zero drift for token-monitor files (interrupt-safe scaffold state) | T-EDGE-032 | R-012 |

## Dimension Coverage Checklist

| Dim | Edges | Covered |
|-----|------:|:-------:|
| 1 Null/Missing | E-001..E-004 | Yes |
| 2 Precision Loss | E-005..E-007 | Yes |
| 3 Concurrency | E-008..E-011 | Yes |
| 4 Rate/Burst | E-012..E-013 | Yes |
| 5 Schema drift | E-014..E-015 | Yes |
| 6 Idempotency | E-016..E-017 | Yes |
| 7 Partial failure | E-018..E-019 | Yes |
| 8 Security | E-020..E-022 | Yes |
| 9 Scale | E-023..E-024 | Yes |
| 10 Resource leak | E-025..E-027 | Yes |
| 11 Tenant/Cross-project leak | E-028..E-029 | Yes |
| 12 Interrupt | E-030..E-032 | Yes |

**Total edges:** 32 (E-001 … E-032)

## Test ID → Ported/New Test Mapping

| Test ID | Test location | Status |
|---------|--------------|--------|
| T-EDGE-001..E-011, E-016, E-017, E-023, E-029 | `index.test.ts` (ported, verbatim) | Pending port |
| T-EDGE-004, E-013, E-025, E-026, E-031 | `index.test.ts::parsePollInterval` / `startPolling` (ported) | Pending port |
| T-EDGE-005..E-007, E-024 | `index.test.ts::formatToken/formatCost/formatPercent` (ported) | Pending port |
| T-EDGE-008..E-010, E-018, E-019, E-027, E-028, E-030 | `index.integration.test.ts` (ported) | Pending port |
| T-EDGE-012, E-015, E-020, E-021, E-022, E-032 | `tests/unit/test_token_monitor_manifest.py` (new Python) | Pending create |
| T-EDGE-014 | `npm --prefix .opencode run type-check` (tsc --noEmit) | Pending create |

**Total tests planned:** 32 edge cases + 18 RTM requirements covered across ported vitest suite and new Python manifest suite.
