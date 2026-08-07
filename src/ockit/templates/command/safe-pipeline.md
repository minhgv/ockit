---
description: "Rollback-aware pipeline with BA & QA skills suite — runs 5 stages with auto-rollback on test failure at each stage, verifying RTM and 12-Dimensional Edge Cases."
agent: coder
subtask: true
---

# /safe-pipeline

Full 5-step pipeline with BA & QA skills, isolated Git worktree execution, and auto-rollback safety net. Runs as a native OpenCode subtask (`subtask: true`) so the parent session stays isolated from pipeline side effects.

## Steps

### Step 0: Create Git Checkpoint
```bash
git stash push -m "pre-pipeline-$(date +%s)" || git commit -am "checkpoint: pre-pipeline" --allow-empty
```

### Step 1: Plan (BA Expert & RTM)
Invoke the **`planner`** subagent (`.opencode/agent/planner.md`):
- Survey and create SPEC for `$ARGUMENTS` at `plans/SPEC_$(echo $ARGUMENTS | tr ' ' '-').md`.
- Load the `ba-expert` skill to construct RTM, 12-Dimensional Edge Case Matrix, NFRs, and DFD.
- Run `!ockit verify`.

### Step 2: TDD (QA Test Gen with rollback on failure)
Invoke the **`coder`** subagent (`.opencode/agent/coder.md`):
- Read the generated SPEC. Invoke the `qa-test-gen` skill.
- Execute TDD: RED → GREEN → REFACTOR covering RTM and 12-Dimensional Edge Cases.
- On failure at any step, restore the Step 0 checkpoint before retrying.

### Step 3: Quality Gate Audit (QA Auditor & Dependency Scan)
```bash
!ockit scan-deps
```
Invoke the **`reviewer`** subagent (`.opencode/agent/reviewer.md`):
- Load the `qa-auditor` skill. Lint + typecheck + secret scan + OWASP-AI checklist.
- Run `!ockit verify`. Fix all issues.

### Step 4: E2E QA (QA Reproducer with rollback on failure)
Invoke the **`qa`** subagent (`.opencode/agent/qa.md`):
- Start local server. Load `qa-reproducer` skill for MRE pipeline.
- Run E2E test covering 12-Dimensional edge cases. Collect evidence into `tests/qa-evidence/`.

### Step 5: Review & Commit (3-State Verification)
Invoke the **`reviewer`** subagent (`.opencode/agent/reviewer.md`):
- Load the `qa-auditor` and `ba-expert` skills. Pre-commit diff audit + 3-State Verification + RTM audit + Conventional Commits.
