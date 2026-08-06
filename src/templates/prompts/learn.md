---
description: "Extract persistent memory & knowledge items — distill user corrections, architectural patterns, and debugging solutions into MEMORY.md and Knowledge Items."
---

# /learn

Distill insights, user directives, bug fixes, or architecture conventions into persistent memory (`MEMORY.md`).

## Steps

### Step 1: Memory Extraction & Pattern Mining
Invoke the **`reviewer`** subagent (`.agents/agents/reviewer.md`):
- Analyze recent conversation history, code changes, or user feedback for `$ARGUMENTS`.
- Extract key project conventions, recurring gotchas, or setup rules.
- Format the learning entry with context, rationale, and actionable instructions.

### Step 2: Persistent Memory Update
- Append distilled rules into `MEMORY.md`.
- Verify no duplicate entries or conflicting guidance exist in `AGENTS.md` or `MEMORY.md`.
