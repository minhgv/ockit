---
description: "Rollback-aware pipeline with BA & QA skills suite — runs 5 stages with auto-rollback on test failure at each stage, verifying RTM and 12-Dimensional Edge Cases."
---

# /safe-pipeline

Full 5-step pipeline with BA & QA skills, isolated Git worktree execution, and auto-rollback safety net.

## Steps

### Step 0: Create Git Checkpoint
```bash
git stash push -m "pre-pipeline-$(date +%s)" || git commit -am "checkpoint: pre-pipeline" --allow-empty
```

### Step 1: Plan (BA Expert & RTM)
Invoke the **`planner`** subagent (`.agents/agents/planner.md`):
- Survey and create SPEC for `$ARGUMENTS` at `plans/SPEC_$(echo $ARGUMENTS | tr ' ' '-').md`.
- Load the `ba-expert` skill to construct RTM, 12-Dimensional Edge Case Matrix, NFRs, and DFD.
- Run `./bin/validate-traceability.sh`.

### Step 2: TDD (QA Test Gen with rollback on failure)
```bash
./bin/safe-agent-run.sh coder "$ARGUMENTS" "Read SPEC. Invoke 'qa-test-gen' skill. Execute TDD: RED → GREEN → REFACTOR covering RTM and 12-Dimensional Edge Cases."
```

### Step 3: Quality Gate Audit (QA Auditor & Dependency Scan)
```bash
./bin/scan-dependencies.sh
```
Invoke the **`reviewer`** subagent (`.agents/agents/reviewer.md`):
- Load the `qa-auditor` skill. Lint + typecheck + secret scan + OWASP-AI checklist.
- Run `./bin/validate-traceability.sh`. Fix all issues.

### Step 4: E2E QA (QA Reproducer with rollback on failure)
Invoke the **`qa`** subagent (`.agents/agents/qa.md`):
- Start local server. Load `qa-reproducer` skill for MRE pipeline.
- Run E2E test covering 12-Dimensional edge cases. Collect evidence into `tests/qa-evidence/`.

### Step 5: Review & Commit (3-State Verification)
Invoke the **`reviewer`** subagent (`.agents/agents/reviewer.md`):
- Load the `qa-auditor` and `ba-expert` skills. Pre-commit diff audit + 3-State Verification + RTM audit + Conventional Commits.
