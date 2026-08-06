---
name: qa-reproducer
description: Minimal Bug Reproduction & Regression Conversion Pipeline — analyzing log stack traces, synthesizing minimal reproduction scripts (reproductions/repro-xxx.py), isolating root causes, and promoting to permanent regression test suites.
---

# qa-reproducer — Minimal Bug Reproduction & Regression Conversion Pipeline

The `qa-reproducer` skill enables subagents to parse runtime error logs, stack traces, or user bug reports, automatically generate a Minimal Reproduction Example (MRE) script under `reproductions/repro-xxx.py` (or `.ts`), isolate the root cause, and convert it into a permanent regression test suite.

## 1. Mandatory JSON Bug Reproduction Output Contract

When executing bug reproduction, subagents MUST format output using this JSON contract:

```json
{
  "reproduction_summary": {
    "target_error": "TypeError: Cannot read property 'zipCode' of undefined",
    "status": "REPRODUCED",
    "file_path": "reproductions/repro-20260804-001-null-address.py",
    "root_cause": "Missing null check before accessing address.zipCode",
    "reproduction_command": "python3 reproductions/repro-20260804-001-null-address.py",
    "exit_code": 1
  },
  "minimal_reproduction_code": "from src.user import get_user_zip\n..."
}
```

---

## 2. 4-Step Reproduction & Regression Conversion Pipeline

1. **Log & Stack Trace Ingestion:** Extract the failing stack trace, error message, and context parameters from user reports or test logs.
2. **Minimal Reproduction Script Generation (MRE):** Emit a self-contained script at `reproductions/repro-<timestamp>-<id>.py` containing only the minimal logic required to trigger the defect. The script MUST exit with code `1` when the defect is present, and code `0` when fixed.
3. **Local Execution & Verification:** Execute the reproduction script to verify 100% deterministic failure.
4. **Regression Suite Promotion:** Once the fix is applied and the reproduction script exits with code `0`, automatically promote the MRE script into a permanent regression test file under `tests/regression/test_repro_<id>.py` to protect against future regressions in CI/CD.
