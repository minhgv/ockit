# Reference: ACM (12-Dimensional Edge Case Matrix) Template

> **Verify contract:** `ockit verify` requires the string `Edge Case` in the SPEC. Rows must start with `E-<number>`.

---

## File Header

```markdown
# ACM: <feature_name> — 12-Dimensional Edge Case Matrix

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** YYYY-MM-DD
> **Parent SPEC:** `plans/SPEC_<feature>.md`
> **Domain adaptation:** <one-line domain context>
```

---

## Step 1: Dimension Mapping (adapt 12 dims to your domain)

The 12 classic dimensions may need adaptation to the project domain. Map each before generating edge cases:

```markdown
## Dimension Mapping (<domain> Domain)

| # | Classic Dimension | <Domain> Adaptation |
|---|-------------------|---------------------|
| 1 | Null / Missing | <what "missing" means in this domain> |
| 2 | Precision Loss | <what precision means here; N/A if not currency> |
| 3 | Concurrency | <parallel mutation surfaces> |
| 4 | Rate Limit | <burst surfaces> |
| 5 | Schema Drift | <versioning / legacy surfaces> |
| 6 | Idempotency | <retry / replay surfaces> |
| 7 | Partial Failure | <multi-step mutation surfaces> |
| 8 | Security Fallback | <auth / path / leak surfaces> |
| 9 | Context Overflow | <scale / size surfaces> |
| 10 | Resource Leak | <FD / connection / handle surfaces> |
| 11 | Tenant Leak | <cross-tenant or cross-project surfaces> |
| 12 | Task Interrupt | <crash / SIGINT surfaces> |
```

---

## Step 2: 12-Dimensional Edge Case Matrix (6 columns)

```markdown
| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID | Req |
|---------|----------------|---------------|------------------------|---------|-----|
| E-001 | 1. Null / Missing | <scenario> | <expected result + exit/HTTP code> | T-EDGE-001 | R-001 |
| E-002 | 2. Precision Loss | <scenario> | <expected> | T-EDGE-002 | R-003 |
| ... | ... | ... | ... | ... | ... |
| E-012 | 12. Task Interrupt | <scenario> | <expected> | T-EDGE-012 | R-007 |
```

### Column Definitions

| Column | Rules |
|---|---|
| Edge ID | MUST be `E-<number>` (zero-padded 3 digits). |
| Risk Dimension | `<n>. <Dimension Name>` — maps to dimension mapping table. |
| Test Scenario | Concrete input/action description. No abstraction. |
| Expected Result & Code | Exact behavior + HTTP status / exit code / error message. |
| Test ID | `T-EDGE-<NNN>` — traces to test function. |
| Req | Traces back to RTM `R-<NNN>`. **Mandatory** for bidirectional traceability. |

---

## Step 3: Dimension Coverage Checklist

EVERY dimension MUST have at least 1 edge case. Verify coverage:

```markdown
## Dimension Coverage Checklist

| Dim | Edges | Covered |
|-----|------:|:-------:|
| 1 Null/Missing | E-001 | Yes |
| 2 Precision Loss | E-002 | Yes |
| 3 Concurrency | E-003 | Yes |
| 4 Rate/Burst | E-004 | Yes |
| 5 Schema drift | E-005 | Yes |
| 6 Idempotency | E-006 | Yes |
| 7 Partial failure | E-007 | Yes |
| 8 Security | E-008 | Yes |
| 9 Scale | E-009 | Yes |
| 10 Resource leak | E-010 | Yes |
| 11 Tenant/Cross-project leak | E-011 | Yes |
| 12 Interrupt | E-012 | Yes |

**Total edges:** <N> (E-001 … E-0NN)
```

---

## Verify Contract Notes

- `ockit verify` checks SPEC for string `Edge Case` — present in section title.
- ACM rows must use `E-<number>` prefix (distinguished from RTM `R-<number>` rows).
- If dimension has no applicable edge: write `N/A — <reason>` in Test Scenario, still count as covered.
- Minimum 12 edges (1 per dimension). Real-world: 20-40 edges typical.
