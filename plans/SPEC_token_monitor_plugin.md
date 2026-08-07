> **APPROVED** — 2026-08-07. User review locked: (D1) bump @opencode-ai/plugin to ^1.18.12; (D2) JS tests via `npm --prefix .opencode test`, root stays Python-only; (D3) template ships package.json + AGENTS.md note; (D4) strip debug logging (R-008); (D5) render E2E = manual opencode TUI smoke test. DO NOT regenerate this SPEC; extend it only with explicit user approval.

# SPEC: token_monitor_plugin

> **Status:** Approved (user review 2026-08-07)
> **Author:** Planner Agent (ba-expert)
> **Date:** 2026-08-07
> **Associated Artefacts:** `plans/RTM_token_monitor_plugin.md`, `plans/ACM_token_monitor_plugin.md`, `plans/NFR_token_monitor_plugin.md`, `plans/DFD_token_monitor_plugin.md`

---

## 1. Executive Summary & Business Analysis

### 1.1 Primary Goals & Non-Goals

- **Goals:**
  1. **Copy** the working token-monitor TUI plugin from `/Users/giapminh79/code/GitHub/ducgv-ai-code-forge/.opencode/plugin/token-monitor/` into this repo (ockit) at `.opencode/plugin/token-monitor/` — keep the proven TypeScript implementation, no rewrite.
  2. **Adapt** registration to ockit conventions: create `.opencode/tui.json` (TUI plugin registry — ockit has none today), bump `@opencode-ai/plugin` to a version that ships `@opencode-ai/sdk/v2/types` (source proven on 1.18.12; ockit has 1.14.40 which lacks it), add runtime deps (`solid-js`, `@opentui/core`, `@opentui/solid`) and dev deps (`vitest`, `typescript`, `@types/node`) to `.opencode/package.json`.
  3. **Scaffold**: mirror the plugin into the packaged template suite `src/ockit/templates/plugin/token-monitor/` + `src/ockit/templates/tui.json` so future `ockit init --target <dir>` targets receive a functional token-monitor sidebar panel, per repo rule "packaged templates live in `src/ockit/templates/`".
  4. **Activate**: plugin renders the TUI `sidebar_content` slot showing per-model token/cost/message usage in the ockit repo itself, wired through `tui.json`.
  5. **Verify**: ported unit + integration tests keep passing under a new vitest harness; existing ockit Python test suite (`pytest`) stays green; `ockit sync` reports no drift for the mirrored files.

- **Non-Goals:**
  1. Do NOT modify `/Users/giapminh79/code/GitHub/ducgv-ai-code-forge/` (READ-ONLY source).
  2. Do NOT touch ockit Python implementation (`src/ockit/cli.py`, `verify.py`, `sync.py`, `installer.py`, `validators.py`, `scan_deps.py`, `doctor.py`, `worktree.py`) unless strictly required — none is required for this feature (package-data glob `templates/**/*` already ships new template files).
  3. Do NOT change the four existing JS plugins (`ockit-*.js`) or the `opencode.json` `plugin` array — token-monitor is a TUI plugin and registers via `tui.json`, not `opencode.json`.
  4. Do NOT compile TS → JS. opencode's TUI runtime is Bun-based and loads `.ts`/`.tsx` natively (source repo ships zero compiled output, `noEmit: true`). No build step is added.
  5. Do NOT rewrite token-monitor logic. Any deviation from source is limited to: stripping the source's explicit "TEMPORARY debug logging" block (source comment says "Remove before finalizing"), fixing import extension style if the runtime requires it, and pinning dependencies.
  6. Do NOT add network-based CVE scanning or telemetry.
  7. Do NOT bundle `node_modules` into templates.

### 1.2 Requirement Traceability Matrix (RTM) (`plans/RTM_token_monitor_plugin.md`)

Full matrix: **18 requirements** `R-001` … `R-018`. Summary:

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | Copy token-monitor core modules verbatim into `.opencode/plugin/token-monitor/` (7 source files) | Copy goal | P0 | `.opencode/plugin/token-monitor/*.ts(x)` | `tests/unit/test_token_monitor_manifest.py::test_r001_core_files_present` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-002 | Create `.opencode/tui.json` registering `./plugin/token-monitor` | Source `.opencode/tui.json` | P0 | `.opencode/tui.json` | `tests/unit/test_token_monitor_manifest.py::test_r002_tui_json_entry` | `tests/qa-evidence/token-monitor/tui_json.log` | Passed |
| R-003 | Bump `@opencode-ai/plugin` to `^1.18.12` and add runtime deps (`solid-js@1.9.12`, `@opentui/core@0.4.5`, `@opentui/solid@0.4.5`) | Dep analysis (sdk v2/types missing in 1.14.40) | P0 | `.opencode/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r003_dependencies_pinned` | `tests/qa-evidence/token-monitor/npm_install.log` | Passed |
| R-004 | Add dev deps (`vitest`, `typescript`, `@types/node`, `bun-types`) + `test`/`type-check` scripts | Test infra gap | P1 | `.opencode/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r004_devdeps_and_scripts` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |
| R-005 | Port `index.test.ts` + `index.integration.test.ts` verbatim and make them pass under vitest | Test copy goal | P0 | `.opencode/plugin/token-monitor/index.test.ts`, `index.integration.test.ts`, `.opencode/vitest.config.ts` | `.opencode/plugin/token-monitor/index.test.ts` suite | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-006 | Add `.opencode/vitest.config.ts` scoped to `plugin/**/*.test.ts` | Vitest config gap | P1 | `.opencode/vitest.config.ts` | `tests/unit/test_token_monitor_manifest.py::test_r006_vitest_config` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |
| R-007 | Add `.opencode/tsconfig.json` + `plugin/tsconfig.typecheck.json` for `tsc --noEmit` type-check of TS plugins | Type-check infra gap | P1 | `.opencode/tsconfig.json`, `.opencode/plugin/tsconfig.typecheck.json` | `tests/unit/test_token_monitor_manifest.py::test_r007_tsconfig` | `tests/qa-evidence/token-monitor/typecheck.log` | Passed |
| R-008 | Strip source TEMPORARY debug logging block from `index.ts` (debug-only, `/tmp` log) | Source TODO + portability | P1 | `.opencode/plugin/token-monitor/index.ts` | `tests/unit/test_token_monitor_manifest.py::test_r008_no_debug_log` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-009 | Mirror plugin into `src/ockit/templates/plugin/token-monitor/` (7 source + 2 test files) | Scaffold goal | P0 | `src/ockit/templates/plugin/token-monitor/*` | `tests/unit/test_token_monitor_manifest.py::test_r009_templates_mirror` | `tests/qa-evidence/token-monitor/files_manifest.log` | Passed |
| R-010 | Add `src/ockit/templates/tui.json` mirroring active `.opencode/tui.json` | Scaffold goal | P0 | `src/ockit/templates/tui.json` | `tests/unit/test_token_monitor_manifest.py::test_r010_templates_tui_json` | `tests/qa-evidence/token-monitor/sync_check.log` | Passed |
| R-011 | Add template `package.json` (or documented install step) so scaffolded targets can install plugin deps | Scaffold dep gap | P1 | `src/ockit/templates/package.json` | `tests/unit/test_token_monitor_manifest.py::test_r011_templates_package_json` | `tests/qa-evidence/token-monitor/npm_install.log` | Passed |
| R-012 | `ockit sync --check` reports zero drift between active `.opencode/plugin/token-monitor`, `tui.json`, `package.json` + mirrored harness (`tsconfig.json`, `vitest.config.ts`, `plugin/tsconfig.typecheck.json`, `.gitignore`) and templates | ockit AGENTS.md sync rule | P0 | `.opencode/plugin/token-monitor/**`, `.opencode/tui.json`, `.opencode/package.json`, `src/ockit/templates/**` | `tests/unit/test_sync.py::test_r012_token_monitor_no_drift` | `tests/qa-evidence/token-monitor/sync_check.log` | Passed |
| R-013 | Token aggregation correctness: input/output/cache read/cache write/reasoning/cost/messageCount per model, dedup by message id, ordering by total tokens desc | Ported tests | P0 | `.opencode/plugin/token-monitor/token-state.ts` | `index.test.ts::aggregateMessage / aggregateStep suites` | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-014 | Poll interval clamp (5s–300s, default 30s) + AbortSignal-aware polling cleanup | Ported tests | P1 | `.opencode/plugin/token-monitor/config.ts`, `lifecycle.ts` | `index.test.ts::parsePollInterval / startPolling suites` | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-015 | TUI module contract: default export `{ id, tui }`, registers `sidebar_content` slot, subscribes to `message.updated` + `session.next.step.started/ended`, disposes cleanly | Ported integration tests | P0 | `.opencode/plugin/token-monitor/index.ts` | `index.integration.test.ts` | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-016 | Formatters (`formatToken`, `formatCost`, `formatPercent`) display-only rounding; store keeps full precision | Ported tests | P1 | `.opencode/plugin/token-monitor/token-panel.tsx` | `index.test.ts::formatToken / formatCost / formatPercent suites` | `tests/qa-evidence/token-monitor/vitest_pass.log` | Passed |
| R-017 | No secrets / personal paths / machine-specific pins in shipped plugin or templates | ockit AGENTS.md portability | P0 | `.opencode/plugin/token-monitor/**`, `src/ockit/templates/**` | `tests/unit/test_no_leaked_config.py` (existing) + `test_token_monitor_manifest.py::test_r017_no_leaks` | `tests/qa-evidence/token-monitor/portable_scan.log` | Passed |
| R-018 | `run_tdd` / docs: plugin test command documented and runnable via `npm --prefix .opencode test` | Usability | P2 | `.opencode/package.json`, `AGENTS.md` (no change needed if scripts present) | `tests/unit/test_token_monitor_manifest.py::test_r018_test_command` | `tests/qa-evidence/token-monitor/vitest_run.log` | Passed |

Coverage summary and source→requirement reverse index: see `plans/RTM_token_monitor_plugin.md`.

> **R-012 note (scope + exclusions):** the sync-mirror contract covers
> `plugin/token-monitor/**`, `tui.json`, `package.json` and the mirrored dev-harness
> files (`tsconfig.json`, `vitest.config.ts`, `plugin/tsconfig.typecheck.json`,
> `.gitignore`). `.opencode/package-lock.json` is **deliberately active-only**: it is
> a dev lockfile, never scaffolded (wheel bloat, frozen resolved pins), and is
> therefore excluded from R-012 — `ockit sync --check` reports it as the sole
> residual `missing_in_templates` item by design.

### 1.3 Domain Modeling & Ubiquitous Language Glossary

- **Domain Entities:**
  - `AssistantMessage` — opencode v2 assistant message carrying `tokens` + `cost` + `time.completed` (`@opencode-ai/sdk/v2/types`).
  - `PerModelTotals` — per `providerID/modelID` aggregate: input/cacheRead/output/cacheWrite/reasoning tokens, cost, messageCount.
  - `TokenStore` — Solid store (`Record<modelKey, PerModelTotals>`) + shared `seen: Set<messageID>` dedup guard + `getModels()` (sorted by total tokens desc).
  - `StepTokenUsage` — `{ assistantMessageID, tokens }` from `session.next.step.ended`.
  - `TuiPluginModule` — default-export `{ id, tui }` contract from `@opencode-ai/plugin/tui`.
- **Ubiquitous Language:**
  | Term | Definition & Rules | Implementation Entity / Type |
  |---|---|---|
  | Token Monitor | TUI sidebar panel aggregating per-model token usage | `plugin/token-monitor/` module |
  | modelKey | `${providerID}/${modelID}` unique aggregation key | `modelKey()` in `token-state.ts` |
  | Dedup guard | assistantMessageID counted once even if `message.updated` + `step.ended` both arrive | `TokenStore.seen: Set<string>` |
  | Sidebar Content Slot | host TUI slot rendering the panel | `api.slots.register({ slots: { sidebar_content } })` |
  | Poll Tick | 30s interval signal forcing panel repaint (clock refresh) | `createSignal` + `startPolling` in `index.ts` |
  | Provider/Model Split | aggregate keyed by provider + model, not message | `PerModelTotals.providerID/modelID` |
- **User Journey:** Actor `[OpenCode TUI User]` → opens session → assistant messages stream → plugin aggregates tokens per model → TUI sidebar `sidebar_content` shows `Model Requests` panel with per-model In/Out/CacheR/CacheW/Reasoning/Cost + totals; panel refreshes every 30s and on every new aggregated message.

### 1.4 User Stories & Behavioral Acceptance Criteria (BDD / Gherkin Matrix)

#### Story US-01: TUI Sidebar Token Panel
- **As a** `TUI user running ockit`
- **I want to** `see per-model token and cost usage in the sidebar while chatting`
- **So that** `I can track spend and context usage without leaving the session`

##### Happy Path Scenario (Success Flow)
- **Given** `opencode TUI loads with tui.json registering token-monitor`
- **When** `an assistant message with tokens completes (message.updated role=assistant)`
- **Then** `the Model Requests panel appears/updates with per-model input/output/cache/reasoning tokens, cost, and message count`

##### Fail Path Scenarios
- **Scenario FP-01 (Missing Event Payload)**: **Given** `message.updated event lacks tokens or time.completed` **When** `handler runs` **Then** `aggregation is skipped, no crash, store unchanged`
- **Scenario FP-02 (Plugin Unregistered)**: **Given** `tui.json missing or plugin path wrong` **When** `TUI starts` **Then** `panel absent; no other plugins affected`
- **Scenario FP-03 (Missing Runtime Deps)**: **Given** `solid-js/@opentui not installed in .opencode/node_modules` **When** `TUI loads plugin` **Then** `plugin fails to load — documented install step must be run (npm --prefix .opencode install)`
- **Scenario FP-04 (Double Count)**: **Given** `same assistantMessageID arrives via both message.updated and session.next.step.ended` **When** `both handlers run` **Then** `tokens counted exactly once (dedup guard)`
- **Scenario FP-05 (Dispose)**: **Given** `TUI session closes / lifecycle disposes` **When** `onDispose fires` **Then** `event subscriptions unregistered, polling stopped, stepModels map cleared`

#### Story US-02: Scaffolded Targets Get the Panel
- **As a** `ockit init user`
- **I want to** `get a working token-monitor plugin in my scaffolded .opencode`
- **So that** `I can monitor tokens without manual plugin installation`

##### Happy Path Scenario (Success Flow)
- **Given** `templates ship token-monitor + tui.json + package.json`
- **When** `user runs ockit init --target <dir> and installs node deps per README`
- **Then** `scaffolded .opencode/tui.json registers ./plugin/token-monitor and the panel renders`

##### Fail Path Scenarios
- **Scenario FP-01 (Missing Template)**: **Given** `token-monitor absent from src/ockit/templates/` **When** `init runs` **Then** `target gets no plugin and tui.json references a missing path — documented as broken scaffold (must fail test)`
- **Scenario FP-02 (Missing Deps Doc)**: **Given** `scaffolded target has no package.json template or install instructions` **When** `user starts opencode TUI` **Then** `plugin import fails on missing solid-js — must be documented in template README/AGENTS.md`
- **Scenario FP-03 (Drift)**: **Given** `active plugin diverges from templates` **When** `ockit sync --check runs` **Then** `drift reported with path + kind (missing_in_templates / content_mismatch)`

---

## 2. Architecture & Data Flow Diagram (DFD) (`plans/DFD_token_monitor_plugin.md`)

```mermaid
graph LR
    subgraph Untrusted["External / Host Runtime"]
        OC[OpenCode TUI Host]
        EV[SDK Event Stream]
    end
    subgraph Trust["Plugin Boundary .opencode/plugin/token-monitor"]
        IDX[index.ts: tui() entry]
        EVH[event.on handlers]
        ST[token-state.ts store]
        SR[solid-runtime.ts]
        SRA[store-runtime.ts]
        LP[lifecycle.ts polling]
        PANEL[token-panel.tsx]
    end
    OC -->|loads tui.json plugin| IDX
    EV -->|message.updated| EVH
    EV -->|session.next.step.started/ended| EVH
    EVH -->|aggregateMessage/aggregateStep| ST
    ST -->|getModels| PANEL
    LP -->|tick signal 30s| PANEL
    PANEL -->|sidebar_content slot| OC
    SR -->|createSignal/createMemo/For| PANEL
    SRA -->|createStore/produce| ST
```

- **Main Data Flow:** TUI host loads plugin via `tui.json` → `index.ts` registers slot + event listeners → SDK events aggregate into Solid store → `token-panel.tsx` reads store + tick signal → host renders `sidebar_content`.
- **Trust Boundaries:** SDK event payloads are treated as untrusted input (validated defensively — missing `tokens`/`time.completed` skipped). Store + formatters live inside the plugin boundary. No network, no shell, no filesystem writes except optional debug log which R-008 strips.

---

## 3. Interface & Schema Specification (Zod & Pydantic)

### API Endpoints

| Method | Path | Request Body | Response Schema | Status Codes |
|--------|------|-------------|-----------------|--------------|
| TUI | `.opencode/tui.json` → `./plugin/token-monitor` | `TuiPluginModule { id?, tui }` | `TuiPluginApi` (slots/event/lifecycle) | Load OK / Load fail |

No HTTP endpoints. Plugin is a pure TUI extension.

### Zod / Pydantic Data Validation Schemas

The plugin has no I/O schema; opencode SDK types serve as the contract. Ported tests validate payload shapes via TS types at compile time (`tsc --noEmit`) and runtime assertions in vitest. For future config validation (not in scope now), a Zod schema is recommended:

```typescript
import { z } from "zod";

export const TokenMonitorOptionsSchema = z.object({
  pollIntervalMs: z.number().int().min(5000).max(300000).optional(),
});
export type TokenMonitorOptions = z.infer<typeof TokenMonitorOptionsSchema>;
```

Runtime defensiveness (missing `tokens`, missing `time.completed`, non-finite poll interval) is handled in code per R-013/R-014 — no user-facing validation errors are emitted (best-effort plugin per Constitution Art.7.3).

---

## 4. Non-Functional Requirements (NFR) (`plans/NFR_token_monitor_plugin.md`)

| Category | Target Metric / Floor Threshold | Verification Method |
|----------|--------------------------------|---------------------|
| Reliability | Plugin never throws on malformed/missing event payloads | `index.test.ts` skip-cases + `index.integration.test.ts` mock api |
| Coverage Floor | Ported vitest suite 100% green (≥29 tests) | `npm --prefix .opencode test` |
| Portability | Zero hardcoded paths/secrets/machine-specific pins in plugin + templates | `test_no_leaked_config.py` + `test_r017_no_leaks` |
| Compatibility | `@opencode-ai/plugin` ≥1.18.12 (sdk `v2/types` export), solid-js 1.9.12, @opentui 0.4.5 | `test_r003_dependencies_pinned` |
| Observability | Event subscription + polling cleanup on dispose; no zombie intervals | `index.test.ts::startPolling abort` cases |
| Security | No shell exec, no network egress, no file writes (debug log stripped R-008) | `test_r008_no_debug_log` |
| Maintainability | `ockit sync --check` zero drift for mirrored files | `test_sync.py::test_r012_token_monitor_no_drift` |

---

## 5. File Mutation Manifest

| Action | File Path | Rationale & Responsibility |
|--------|-----------|----------------------------|
| Create | `.opencode/plugin/token-monitor/config.ts` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/index.ts` | Copy minus TEMPORARY debug block (R-001, R-008) |
| Create | `.opencode/plugin/token-monitor/lifecycle.ts` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/solid-runtime.ts` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/store-runtime.ts` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/token-state.ts` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/token-panel.tsx` | Verbatim copy (R-001) |
| Create | `.opencode/plugin/token-monitor/index.test.ts` | Verbatim copy (R-005) |
| Create | `.opencode/plugin/token-monitor/index.integration.test.ts` | Verbatim copy (R-005) |
| Create | `.opencode/tui.json` | TUI plugin registry (R-002) |
| Create | `.opencode/vitest.config.ts` | Vitest config scoped to `plugin/**/*.test.ts` (R-006) |
| Create | `.opencode/tsconfig.json` | TS type-check base (R-007) |
| Create | `.opencode/plugin/tsconfig.typecheck.json` | Extends base; includes token-monitor `.ts/.tsx` (R-007) |
| Modify | `.opencode/package.json` | Deps + devDeps + scripts (R-003, R-004, R-018) |
| Modify | `.opencode/package-lock.json` | Regenerated via `npm install --prefix .opencode` (R-003) |
| Create | `src/ockit/templates/plugin/token-monitor/*` (9 files) | Mirror of active plugin (R-009) |
| Create | `src/ockit/templates/tui.json` | Template TUI registry (R-010) |
| Create | `src/ockit/templates/package.json` | Dependency manifest for scaffolded targets (R-011) |
| Create | `tests/unit/test_token_monitor_manifest.py` | Python manifest/drift/no-leak assertions (R-001…R-018) |
| Modify | `tests/unit/test_plugin_smoke.py` | Document TS/TUI plugin exclusion from node ESM probe (R-005) — annotate, no behavior change to existing 4 plugins |
| Modify | `src/ockit/templates/AGENTS.md` | Add token-monitor install/usage note (R-011) — optional, if template package.json alone insufficient |

> **Constraint:** Subagents MUST NOT create or modify files outside this manifest. Do NOT touch `src/ockit/*.py`, existing `.opencode/plugin/ockit-*.js`, or `.opencode/opencode.json`.

---

## 6. Test Plan & 12-Dimensional Edge Case Matrix (ACM) (`plans/ACM_token_monitor_plugin.md`)

### 6.1 Unit / Integration Tests (Given-When-Then)

- **Given** an assistant message with tokens + completed time **When** `aggregateMessage(store, msg)` **Then** store contains one `PerModelTotals` row with correct counts (R-013).
- **Given** two messages for same model **When** aggregated **Then** counts accumulate, messageCount=2 (R-013).
- **Given** same `assistantMessageID` via `aggregateMessage` then `aggregateStep` **When** both run **Then** second call returns false, counted once (R-013).
- **Given** `pollIntervalMs` below 5000 **When** `parsePollInterval` **Then** clamped to 5000 (R-014).
- **Given** AbortSignal aborted mid-polling **When** `startPolling` **Then** interval cleared, no further ticks (R-014).
- **Given** mocked TuiPluginApi **When** `tui(api)` runs **Then** `sidebar_content` slot registered, 3 event types subscribed, `onDispose` registered (R-015).
- **Given** cost 0.0000003 **When** `formatCost` **Then** `"$0.00"` while store keeps full precision (R-016).

### 6.2 12-Dimensional Business Edge Case Matrix (ACM)

Full 12-dimension matrix (E-001 … E-018): see `plans/ACM_token_monitor_plugin.md`. Summary:

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID |
|---------|----------------|---------------|------------------------|---------|
| E-001 | 1. Null / Missing | `message.updated` with `tokens: undefined` | aggregation skipped, no crash | T-EDGE-001 |
| E-002 | 2. Precision Loss | 3× tiny costs (0.0000001) accumulate | store keeps 0.0000003; display `$0.00` | T-EDGE-002 |
| E-003 | 3. Concurrency | `message.updated` + `step.ended` race for same id | counted once via shared `seen` | T-EDGE-003 |
| E-004 | 4. Rate Limit / Burst | Rapid event stream with many models | store bounded to `MAX_MODEL_ENTRIES=50` | T-EDGE-004 |
| E-005 | 5. Schema Drift | SDK v2 event shape changes | `tsc --noEmit` + defensive guards catch breakage | T-EDGE-005 |
| E-006 | 6. Idempotency | Duplicate message id replay | second aggregate returns false | T-EDGE-006 |
| E-007 | 7. Partial Failure | One event handler throws | isolated; other handlers + slot unaffected | T-EDGE-007 |
| E-008 | 8. Security Fallback | Plugin load failure in TUI | other plugins/session unaffected (TUI isolation) | T-EDGE-008 |
| E-009 | 9. Context Overflow | >50 distinct model keys | lowest-token entry evicted | T-EDGE-009 |
| E-010 | 10. Resource Leak | Dispose mid-poll / abort signal | interval cleared, listeners removed | T-EDGE-010 |
| E-011 | 11. Tenant / Cross-project Leak | Multiple sessions share plugin instance | store is per-`tui()` invocation, no cross-session bleed | T-EDGE-011 |
| E-012 | 12. Task Interrupt | SIGINT / TUI reload during aggregation | `onDispose` clears state; no zombie timers | T-EDGE-012 |

---

## 7. Backward Compatibility & Security Audit

- [x] OWASP-AI-01 Slopsquatting scanned: deps are exact pins from proven source (`solid-js@1.9.12`, `@opentui/core@0.4.5`, `@opentui/solid@0.4.5`, `@opencode-ai/plugin@^1.18.12`) — no hallucinated packages.
- [x] OWASP-AI-02 IDOR authorization: no data access layer; store is in-memory per plugin instance.
- [x] OWASP-AI-03 Input sanitization: SDK payloads defensively validated (missing `tokens`/`time.completed` skipped); no eval/shell/raw SQL.
- [x] OWASP-AI-04 Hardcoded secrets scan: plugin writes no secrets; debug log stripped (R-008); templates portable (R-017).
- [x] OWASP-AI-05 Excessive agency & path sandboxing: plugin has no file writes, no shell, no network; only reads SDK events.
- Backward compatibility: existing 4 JS plugins untouched; `opencode.json` `plugin` array untouched; Python CLI untouched; source repo READ-ONLY.

---

## 8. Definition of Done & 3-State Verification

- [ ] All RTM (`R-001` … `R-018`) requirements mapped 1:1 to passing tests (vitest + pytest)
- [ ] 12-Dimensional Edge Case Matrix (ACM E-001 … E-018) covered in test suite
- [ ] Non-Functional Requirements (NFR) validated against quality floors
- [ ] Data Flow Diagram (DFD) trust boundaries verified
- [ ] 3-State Verification audit completed (`Confirmed` state on all claims)
- [ ] Stamped `plan-review` approval recorded
- [ ] `bin/validate-traceability.sh` and `bin/validate-phase10-ba-qa.sh` passed cleanly
- [ ] `ockit verify` passed cleanly (RTM header, Edge Case, 3-State Verification present)
- [ ] `npm --prefix .opencode test` green (ported token-monitor suite)
- [ ] `pytest tests/ -q` green (existing + new manifest tests)
- [ ] `ockit sync --check` zero drift for token-monitor files
- [ ] Conventional Commits recorded (e.g. `feat(plugin): port token-monitor TUI plugin`)

## Open Questions

1. **Plugin version bump scope**: ockit pins `@opencode-ai/plugin@1.14.40`; source plugin needs `@opencode-ai/sdk/v2/types` (only shipped ≥1.18.x). Decision: bump `@opencode-ai/plugin` to `^1.18.12` in `.opencode/package.json`. **User must confirm** bump is acceptable (it also updates `effect`/`zod` transitively).
2. **Test runner location**: ockit root is a Python package (no root `package.json`). JS tests run via `npm --prefix .opencode test` (vitest installed inside `.opencode/node_modules`). **User must confirm** this is the accepted runner entry point vs adding a root `package.json`.
3. **Template dependency story**: scaffolded targets need `solid-js`/`@opentui` at runtime. Plan adds `src/ockit/templates/package.json` + AGENTS.md note. **User must confirm** shipping a template `package.json` is desired (new file in templates/ set) vs documenting a manual `npm install` one-liner only.
4. **Debug logging strip**: source `index.ts` contains an explicit "TEMPORARY debug logging (verify runtime event delivery only) … Remove before finalizing" block. Plan strips it (R-008). **User must confirm** strip vs keep behind `TOKEN_MONITOR_DEBUG=1`.
5. **TUI runtime verification**: vitest cannot exercise the actual OpenTUI FFI render path (Bun-only). Confirmation that the panel renders requires running opencode TUI after implementation (manual E2E). **User must confirm** manual smoke-test acceptance is acceptable for R-015.
