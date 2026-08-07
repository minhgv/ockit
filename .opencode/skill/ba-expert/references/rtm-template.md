# Reference: RTM (Requirement Traceability Matrix) Template

> **Verify contract:** `ockit verify --suite traceability` requires the string `| Req ID |` in the table header. Rows must start with `R-<number>`.

---

## File Header

```markdown
# RTM: <feature_name>

> **Status:** Draft | In Review | Approved
> **Author:** Planner Agent (ba-expert)
> **Date:** YYYY-MM-DD
> **Parent SPEC:** `plans/SPEC_<feature>.md`
> **Companions:** `plans/ACM_<feature>.md`, `plans/NFR_<feature>.md`, `plans/DFD_<feature>.md`
```

---

## RTM Table Schema (8 columns — ALL mandatory)

```markdown
| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|--------|----------------------------------|--------|----------|-------------------------|---------------------|---------------------|--------|
| R-001 | <what the requirement does> | <where it came from> | P0 | `src/<file>` | `tests/<file>::test_r001_<name>` | `tests/qa-evidence/<path>.log` | Pending |
```

### Column Definitions

| Column | Rules |
|---|---|
| Req ID | MUST be `R-<number>` (zero-padded 3 digits). Sequential. |
| Business Requirement Description | One sentence, testable, no implementation detail. |
| Source | Provenance: interview, arch decision, NFR, ACM edge. |
| Priority | `P0` (blocker) / `P1` (important) / `P2` (nice-to-have). |
| Target Component / File | Concrete file path(s) that implement this requirement. |
| Unit Test Reference | `tests/<file>::test_r<NNN>_<name>` — MUST trace Req ID. Empty = WARN from verify. |
| E2E QA Verification | Path to QA evidence log/script. `N/A` acceptable for deferred/doc-only. |
| Status | `Pending` → `In Progress` → `Confirmed` (3-State Verification). |

---

## Coverage Summary (after table)

```markdown
## Coverage Summary

| Priority | Count | IDs |
|----------|------:|-----|
| P0 | <n> | R-001–R-0NN |
| P1 | <n> | ... |
| P2 | <n> | ... |
| **Total** | **<n>** | R-001 … R-0NN |
```

---

## Source → Requirement Map (traceability reverse index)

```markdown
## Source → Requirement Map

| Source artefact | Requirements |
|-----------------|--------------|
| <interview / arch doc / NFR> | R-001, R-003 |
```

---

## Out-of-Scope (explicit non-trace)

```markdown
## Out-of-Scope (explicit non-trace)

- <feature explicitly excluded and why>
- <deferred item with defer reason>
```

---

## Verify Contract Notes

- `ockit verify` checks Unit Test Reference cells: if empty or `N/A`/`-`/`None`/`TBD`/`TODO`/`pending` → **WARN** (exit 0).
- Missing RTM table entirely in SPEC → **FAIL** (exit 1).
- Header must be exactly `| Req ID |` (case-sensitive).
