# Reference: NFR (Non-Functional Requirements) Template

---

## File Header

```markdown
# NFR: <feature_name>

> **Status:** Draft
> **Author:** Planner Agent (ba-expert)
> **Date:** YYYY-MM-DD
> **Parent SPEC:** `plans/SPEC_<feature>.md`
```

---

## NFR Table Schema (5 columns)

```markdown
## Non-Functional Requirements

| NFR ID | Category | Target Metric / Floor Threshold | Verification Method | Related Req |
|--------|----------|--------------------------------|---------------------|-------------|
| NFR-001 | Latency (p95) | <command/endpoint> < <N> s <conditions> | `time <command>` in QA evidence | R-001 |
| NFR-002 | Throughput | >= <N> ops/s sustained | load test script | R-003 |
| NFR-003 | Error Rate | < <N>% per session | system log audit | R-005 |
| NFR-004 | MTTR | < <N> s via auto-rollback | rollback hook test | R-007 |
| NFR-005 | Coverage Floor | >= 85% lines, >= 70% branches | `pytest --cov` / `jest --coverage` | R-009 |
| NFR-006 | Error Clarity | Every non-zero exit includes 3-part error: What / Context / Fix | unit assert on message shape | Constitution Art.3 |
| NFR-007 | Idempotency | <N>x repeated <operation> → identical state | `diff -qr` | R-007 |
| NFR-008 | Portability | Zero hardcoded paths/secrets in shipped artifacts | CI grep gate | R-017 |
| NFR-009 | Security | <specific security property> | <destructive/pen test> | R-006 |
```

### Column Definitions

| Column | Rules |
|---|---|
| NFR ID | `NFR-<number>` (zero-padded 3 digits). |
| Category | Latency / Throughput / Error Rate / MTTR / Coverage / Security / Portability / Reliability / Observability / Compatibility / Maintainability. |
| Target Metric / Floor Threshold | Measurable number + unit + condition. No vague terms ("fast", "scalable"). |
| Verification Method | How to prove it: timed command, test, audit, CI gate. |
| Related Req | Trace to RTM `R-<NNN>` or ACM `E-<NNN>`. |

---

## Performance Budgets (summary table)

```markdown
## Performance Budgets

| Command / Endpoint | p95 ceiling | Notes |
|--------------------|------------:|-------|
| <command> | <N> s | <conditions> |
```

---

## Quality Floors

```markdown
## Quality Floors

| Metric | Floor |
|--------|------:|
| Line coverage (core modules) | >= 85% |
| Branch coverage (core modules) | >= 70% |
| Portable path violations | 0 |
| Hardcoded secrets | 0 |
```

---

## Explicit Non-Goals (NFR)

```markdown
## Explicit Non-Goals (NFR)

- <performance guarantee explicitly out of scope and why>
```

---

## Verify Contract Notes

- `ockit verify --suite ba-qa` checks that SPEC_TEMPLATE contains the markers `NFR`.
- NFR table is in companion file `plans/NFR_<feature>.md` for 5-file pattern, or inline in SPEC §4 for 1-file pattern.
- Every NFR MUST trace to an RTM requirement or ACM edge — no orphan NFRs.
