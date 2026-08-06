---
name: qa-test-gen
description: Automated Unit & Integration Test Generator — generating unit, integration, and E2E test suites (PyTest, Vitest, Jest, Playwright, Go Test) covering edge cases and strict mocking with mandatory JSON Test Plan Output Contract.
---

# qa-test-gen — Automated Unit & Integration Test Generator

The `qa-test-gen` skill transforms subagents into automated Test Engineers across multi-language projects. It automatically generates unit, integration, and contract test suites covering happy paths and edge cases, strictly isolating external dependencies.

## 1. Mandatory JSON Test Plan Output Contract

Subagents generating test suites MUST output execution specs adhering to this JSON contract:

```json
{
  "test_plan": {
    "target_module": "src/user_processor.py",
    "test_runner": "pytest",
    "total_scenarios": 4,
    "coverage_goals": { "happy_path": 1, "edge_cases": 3 }
  },
  "generated_test_code": "import pytest\nfrom src.user_processor import UserProcessor\n..."
}
```

---

## 2. Core Test Generation Rules

1. **Comprehensive Boundary Coverage:** Every test file must contain at least 1 happy path scenario and ≥3 edge case scenarios (null/undefined values, network timeouts, invalid schema payload, resource limits).
2. **Gherkin BDD Scenario Mapping:** Read the Gherkin Given-When-Then matrix from `plans/SPEC_*.md` Section 1.4 and convert every Happy Path and Fail Path scenario directly into runnable test assertions.
3. **Strict I/O Mocking:** All external dependencies (Database queries, HTTP calls, Filesystem writes, LLM endpoints) MUST be strictly mocked (e.g. `unittest.mock.patch` in PyTest, `vi.fn()` in Vitest, `jest.spyOn()` in Jest).
4. **Strict Test Isolation:** Test cases must be completely stateless and independent. No shared state or reliance on execution order between test runs.
5. **Multi-Framework Auto-Detection:** Automatically detect the project's native test runner (`pytest`, `vitest`, `jest`, `playwright`, `go test`) and generate idiomatic assertions.

---

## 3. 3-Step Test Generation Process

1. **Target Module Inspection:** Read the target source module, extract parameter types, return schemas, and side-effects.
2. **Test Scenario Matrix Construction:** Enumerate Happy Path + Edge Cases (Invalid Input, Network Timeout, Permission Denied, Malformed Payload).
3. **Test Code Emission & Execution:** Emit test files into `tests/` or `__tests__/` directory and execute the test runner to verify green pass status.
