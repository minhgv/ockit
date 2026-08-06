---
description: "Run quality gate only — dependency scanning, qa-auditor skill, OWASP-AI checklist, RTM verification, 12-Dimensional Edge Case audit, and traceability check on current changes."
---

# /gate

Run the Quality Gate audit on current changes with dependency scanning, `qa-auditor` skill, RTM verification, 12-Dimensional Edge Case Matrix audit, and traceability verification.

## Steps

### Step 1: Supply Chain & Dependency Security Scan
```bash
./bin/scan-dependencies.sh
```

### Step 2: Quality & Security Audit (qa-auditor, RTM & 12D Matrix)
Invoke the **`reviewer`** subagent (`.agents/agents/reviewer.md`):
- Load the `qa-auditor` skill to execute Quality Gate Audit (L1-L5).
- LINT & TYPECHECK: Run linter and type checker. Fix all warnings/errors.
- SECRET SCAN: Run secret scanning on staged diff. If secrets found → remove + patch.
- OWASP-AI CHECKLIST & TRACEABILITY:
  - OWASP-AI-01: Verify imports against lockfiles
  - OWASP-AI-02: Check authorization on endpoints
  - OWASP-AI-03: Parameterized SQL, no `shell=True`
  - OWASP-AI-04: No hardcoded credentials
  - OWASP-AI-05: Least-privilege tool execution
- AUDIT CONTRACT & RISK MATRIX: Generate JSON Audit Contract, evaluate Runtime Risk Matrix, verify RTM status, and audit 12-Dimensional Edge Case Matrix coverage.
- Report pass/fail for each item.

### Step 3: Requirement Traceability Audit
```bash
./bin/validate-traceability.sh
```
