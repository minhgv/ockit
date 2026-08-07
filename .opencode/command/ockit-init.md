---
description: "Initialize ockit scaffold into a target project"
---

# /ockit-init

Scaffold `.opencode/` assets and root `AGENTS.md` into a target project using the native `ockit` CLI.

## Steps

### Step 1: Validate Arguments
- If `$ARGUMENTS` is empty, target the current directory (`.`).
- Accept optional passthrough flags `--force` (overwrite existing files) and `--dry-run` (preview without writing).
- The full argument string is passed through to `ockit init` verbatim.

### Step 2: Execute Scaffold Installer
```bash
!ockit init --target "$ARGUMENTS"
```

### Step 3: Verification & Agent Alignment
Invoke the **`planner`** subagent (`.opencode/agent/planner.md`):
- Verify `.opencode/` directory structure and installed assets.
- Confirm `AGENTS.md` and native Markdown subagent specifications align with the project's primary tech stack.
