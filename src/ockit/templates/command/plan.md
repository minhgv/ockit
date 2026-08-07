---
description: "Quick plan-only — create a SPEC with BA expert skill, RTM, and 12-Dimensional Edge Case Matrix without running code."
---

# /plan

Create a SPEC for a new feature using the `ba-expert` skill, RTM, and 12-Dimensional Edge Case Matrix.

## Steps

### Step 1: Survey & BA Plan
Invoke the **`planner`** subagent (`.opencode/agent/planner.md`):
- Survey the codebase related to `$ARGUMENTS`.
- Load the `ba-expert` skill — follow §0 Mandatory Pre-Read Gate: Read the reference templates under `.opencode/skill/ba-expert/references/` BEFORE writing any artefact.
- Execute the Domain Discovery workflow (`references/domain-discovery-workflow.md`).
- Construct the Requirements Traceability Matrix (RTM), 12-Dimensional Edge Case Matrix, NFRs, and DFD using the reference templates as structural guides.
- Create a SPEC at `plans/SPEC_<feature>.md` following `plans/SPEC_TEMPLATE.md` (blank form) annotated by `references/spec-master-template.md` (guide).

### Step 2: Traceability Audit & User Review
```bash
!ockit verify
```
Read the generated SPEC and verify RTM completeness and 12-Dimensional edge cases before proceeding to implementation.
