---
description: "Systematic 5-technique problem solving when stuck — dispatch Simplification Cascades, Collision-Zone Thinking, Meta-Pattern Recognition, Inversion Exercise, or Scale Game."
---

# /solve

Apply systematic problem-solving techniques using the `problem-solving` skill when encountering complexity spirals, innovation blocks, recurring patterns, assumption constraints, or scale uncertainty.

## Steps

### Step 1: Stuck Symptom Diagnosis & Dispatch
Invoke the **`coder`** subagent (`.agents/agents/coder.md`):
- Load the `problem-solving` skill for `$ARGUMENTS`.
- Diagnose stuck symptom against the quick dispatch matrix:
  - Complexity spiraling -> Simplification Cascades (`references/simplification-cascades.md`)
  - Need breakthrough -> Collision-Zone Thinking (`references/collision-zone-thinking.md`)
  - Recurring patterns -> Meta-Pattern Recognition (`references/meta-pattern-recognition.md`)
  - Forced assumptions -> Inversion Exercise (`references/inversion-exercise.md`)
  - Scale uncertainty -> Scale Game (`references/scale-game.md`)
  - General stuck-ness -> When Stuck (`references/when-stuck.md`)
- Load the corresponding reference file from `references/` and execute the technique systematically.

### Step 2: Breakthrough Implementation & Verification
Invoke the **`coder`** subagent (`.agents/agents/coder.md`):
- Implement the refactored logic or simplified architecture, document problem-solving insights, and execute test suite to verify GREEN status.
