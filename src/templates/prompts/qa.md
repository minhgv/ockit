---
description: "Run E2E QA tests using qa-test-gen & qa-reproducer skills — start local server, send cURL/Playwright tests, reproduce bugs with MRE pipeline, collect evidence, and audit RTM."
---

# /qa

Run E2E QA testing on a local server using `qa-test-gen` and `qa-reproducer` skills suite.

## Steps

### Step 1: Dogfooding QA & Bug Reproduction (qa-reproducer & qa-test-gen)
Invoke the **`qa`** subagent (`.agents/agents/qa.md`):
- Load the `qa-test-gen` and `qa-reproducer` skills.
- Start local dev server (if not running). Verify health-check.
- Run test cases according to Section 1.4 (User Stories & Gherkin BDD Matrix) and Section 6 (ACM) in `plans/SPEC_*.md`:
  - Happy Path Scenarios: Valid payload & correct user flow → HTTP 200/201
  - Fail Path Scenarios: Missing/invalid fields → HTTP 400/422 with exact specified error message
  - Fail Path Scenarios: Expired/invalid auth tokens → HTTP 401/403 with exact error message
  - 12-Dimensional Edge Cases: Boundary, Unicode, Concurrency, Network failure, Timeout
- For any failures, invoke `qa-reproducer` to build Minimal Reproduction Examples (MRE) and format JSON Bug Reproduction Schema.
- Collect cURL output, response headers, server logs into `tests/qa-evidence/`.
- Report pass/fail per User Story BDD scenario and edge case.

### Step 2: Traceability & RTM Update
```bash
./bin/validate-traceability.sh
```
