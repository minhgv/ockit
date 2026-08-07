---
description: "Execute the complete 5-step agentic engineering workflow for a feature, fully integrated with Business Analysis (BA) and Quality Assurance (QA) skills suite."
---

# /pipeline

Execute the complete 5-step agentic engineering workflow for a feature, fully integrated with Business Analysis (BA) and Quality Assurance (QA) skills suite.

## Steps

### Step 1: Plan (BA & Specification)
**Guard — no SPEC clobbering:** if `plans/SPEC_$(FEATURE).md` already exists (approved draft), DO NOT regenerate or overwrite it. Read it, verify it is complete (RTM + 12-Dimensional Edge Case Matrix + NFRs + DFD), and proceed. Only when the SPEC is missing should the **`planner`** subagent (`.opencode/agent/planner.md`) create a new one:
- Survey the relevant module and create a SPEC at `plans/SPEC_$(FEATURE).md` following `plans/SPEC_TEMPLATE.md` (blank form) annotated by the `ba-expert` skill's `references/spec-master-template.md` (guide).
- Load the `ba-expert` skill — follow §0 Mandatory Pre-Read Gate: Read reference templates under `.opencode/skill/ba-expert/references/` BEFORE writing any artefact.
- Construct the Requirements Traceability Matrix (RTM), 12-Dimensional Edge Case Matrix, Non-Functional Requirements (NFRs), and Data Flow Diagram (DFD) using the reference templates as structural guides.
- Run `!ockit verify` to verify plan compliance.

### Step 2: Shift-Left Destructive TDD Implementation
Invoke the **`coder`** subagent (`.opencode/agent/coder.md`):
- Read `plans/SPEC_$(FEATURE).md`.
- Load the `qa-test-gen` skill to auto-generate unit, integration, and **Adversarial Destructive Testcases** (null bytes, path traversal, concurrency race conditions) covering the 12-Dimensional Edge Case Matrix and mapped RTM requirements.
- Execute TDD: RED (write tests, verify FAIL) → GREEN (write minimal logic, verify PASS) → REFACTOR. Only modify files listed in the File Mutation Manifest.

### Step 3: Quality Gate Audit
Invoke the **`reviewer`** subagent (`.opencode/agent/reviewer.md`):
- Run `!ockit scan-deps` to scan supply chain dependencies.
- Load the `qa-auditor` skill to execute Quality Gate Audit (L1-L5), produce JSON Audit Contract, evaluate Runtime Risk Matrix, and check OWASP-AI 5-item checklist.
- Run `!ockit verify`. Fix all issues found. Report: 0 errors, 0 warnings, 0 secrets.

### Step 4: E2E QA & Runtime Chaos Fuzzing
Invoke the **`qa`** subagent (`.opencode/agent/qa.md`):
- Start local server.
- Load the `qa-reproducer` and `qa-test-gen` skills to execute E2E test suite according to the Test Plan in SPEC.
- Execute Adversarial Chaos Suite (`make test-destructive`). Test 12-Dimensional edge cases and create Minimal Reproduction Examples (MRE) for any failures. Collect evidence into `tests/qa-evidence/`.

### Step 5: Review & Commit (3-State Verification)
Invoke the **`reviewer`** subagent (`.opencode/agent/reviewer.md`):
- Review git diff.
- Load the `qa-auditor` and `ba-expert` skills for pre-commit audit and 3-State Verification (CONFIRMED / PLAUSIBLE / REFUTED).
- Verify RTM status transitions. Run `!ockit verify`.
- Group commits using Conventional Commits.
