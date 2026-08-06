# TDD Workflow Skill — Red → Green → Refactor

## Trigger
- Any new coding task that requires writing logic.

## Procedure

### RED Phase
1. Read the SPEC file (`plans/SPEC_*.md`) to understand requirements.
2. Write Unit Test + Integration Test simulating all requirements.
3. Run test runner: `npm run test` / `pytest` / `php artisan test`.
4. **Verify:** All new tests must FAIL (no logic yet). If a test PASSES immediately → test is wrong or logic already exists.

### GREEN Phase
1. Write minimal code logic to PASS all tests.
2. Do not implement features outside the SPEC.
3. Re-run tests → **Verify:** 100% PASS.

### REFACTOR Phase
1. Optimize: extract long functions, rename variables for clarity, remove duplicate code (DRY).
2. Re-run tests after each change → **Verify:** ALL TESTS STILL PASS.
3. Report final coverage.

## Pitfalls
- Do not skip the RED phase — if logic is complex, break it into smaller tests.
- If tests are hard to write → SPEC may lack detail → return to Planner.
- Coverage threshold: ≥80% for new code.
