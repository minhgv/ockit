---
name: qa-auditor
description: Codebase Runtime Failure & Edge Case Auditor — scanning runtime exceptions, unhandled promises, memory leaks, race conditions, boundary nullability, and security vulnerabilities with mandatory JSON Audit Contract.
---

# qa-auditor — Codebase Runtime Failure & Edge Case Auditor

The `qa-auditor` skill equips subagents to act as a cross-platform Quality Assurance Auditor. It scans source code for runtime risk vectors (unhandled rejections, null pointers, race conditions, memory leaks, division by zero, missing validation) and outputs findings adhering strictly to a JSON Audit Contract.

## 1. Mandatory JSON Findings Contract

When executing a QA Audit, subagents MUST produce audit results structured according to this JSON schema:

```json
{
  "audit_summary": {
    "scanned_files": 1,
    "total_findings": 2,
    "risk_level": "High"
  },
  "findings": [
    {
      "id": "QA-01",
      "type": "UNHANDLED_JSON_PARSE",
      "file": "src/api.ts",
      "line": 42,
      "severity": "High",
      "evidence": "JSON.parse(raw) without try/catch block",
      "impact": "Parsing an empty or malformed payload crashes the runtime server.",
      "recommendation": "Wrap JSON.parse in try/catch block and validate input schema with Zod/Pydantic.",
      "confidence": 0.95
    }
  ]
}
```

*Note: Findings lacking concrete `file`, `line`, or `evidence` fields are invalid.*

---

## 2. Runtime Risk Matrix

Subagents systematically audit 5 primary runtime failure zones:

| Risk Zone | Real-World Failure Points | Remediation Standard |
|---|---|---|
| **Exception & Promise** | Unhandled Promise Rejection, missing `try/catch` in async functions, swallowed exceptions (empty catch blocks). | Every async path must handle exceptions cleanly and log contextual error details. |
| **Boundary & Nullability** | `Cannot read property of undefined/null`, empty array index out of bounds, division by zero (`NaN`/`Infinity`), unsafe type casts. | Enforce Optional Chaining (`?.`), Nullish Coalescing (`??`), zero checks before division, and schema validation. |
| **Concurrency & Race** | Asynchronous race conditions mutating shared state, missing locks/mutexes on file I/O or DB records. | Enforce atomic transactions, optimistic locking (`version` key), or serialised queue handlers. |
| **Memory & Resource** | Unclosed streams/handles, memory leaks in global event listeners/timers (`setInterval`), dangling DB connections. | Require explicit cleanup via RAII, `dispose()`, `close()`, or `try-finally` blocks. |
| **Security & Validation** | Dynamic string query SQL injection, path traversal (`../../`), unescaped HTML XSS, hardcoded secrets in logs. | Require parameterized queries, `path.basename` sanitization, strict input schemas, and environment secret injection. |

---

## 3. 4-Step QA Audit Process

1. **Codebase Reconnaissance:** Identify target modified files using `git diff` or explicit path inputs.
2. **Static & Pattern Analysis:** Scan for risky code patterns (`JSON.parse` without `try/catch`, empty catch blocks, `any` casting, unclosed handles).
3. **Edge Case Simulation:** Evaluate system behavior under network timeout, empty payload, `EACCES` file permission failure, and zero division.
4. **JSON Export & Reporting:** Emit the standardized JSON findings contract and present a human-readable summary table.
