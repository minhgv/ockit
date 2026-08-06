---
description: "Initialize ockit scaffolding — scaffold OCKIT-native subagent specs, rules, skills, workflows, and language toolchains into a target repository."
---

# /init

Scaffold `ockit` into a target project using `bin/init-ockit.sh`.

## Steps

### Step 1: Execute Safe Scaffolding Installer
```bash
./bin/init-ockit.sh --target . --lang python
```

### Step 2: Verification & Agent Alignment
Invoke the **`planner`** subagent (`.agents/agents/planner.md`):
- Verify `.agents/` directory structure and `install-manifest.json`.
- Confirm `AGENTS.md` and native Markdown subagent specifications align with the project's primary tech stack.
