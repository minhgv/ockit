---
description: "Rigorous stress testing of plans and specifications — apply 11 scrutiny questions to expose hidden assumptions, risks, and failure modes before writing code."
---

# /grill

Stress-test plans, ADRs, and technical specifications using the `grill-me` skill with 11 scrutiny questions before committing to implementation.

## Steps

### Step 1: 11-Question Scrutiny & Risk Exposure
Invoke the **`reviewer`** subagent (`.agents/agents/reviewer.md`):
- Load the `grill-me` skill to stress-test the proposed plan or SPEC for `$ARGUMENTS`.
- Evaluate all 11 scrutiny questions:
  1. What assumptions are you making that could be wrong?
  2. What's the most likely thing to fail?
  3. What if X is 10x larger / smaller / slower?
  4. What's the cost of being wrong?
  5. What's the simplest way to test this?
  6. What's the hardest part? Why?
  7. What's the rollback plan?
  8. What would make this a mistake?
  9. Who disagrees with this? Why?
  10. What's the non-goal everyone forgets?
  11. What are we not talking about?
- Surface hidden risks and force concrete answers rather than "figure it out later".

### Step 2: Plan Hardening & Verification
Invoke the **`planner`** subagent (`.agents/agents/planner.md`):
- Update the technical specification to address all identified vulnerabilities, record answers to all scrutiny questions, and confirm plan resilience before code implementation.
