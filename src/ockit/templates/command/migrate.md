---
description: "Migrate legacy v0.7.x configuration to OCKIT 2.0 — convert JSON subagent specs into native Markdown subagents and canonicalize workspace configuration."
---

# /migrate

Migrate legacy v0.7.x JSON agent configurations into native Antigravity 2.0 Markdown format (`.opencode/agent/*.md`).

## Steps

### Step 1: Legacy Spec Audit & Conversion
Invoke the **`planner`** subagent (`.opencode/agent/planner.md`):
- Audit existing `.antigravity/agents/*.json` or legacy agent files.
- Convert JSON agent instructions, models, and tool definitions into native Markdown agent files with YAML frontmatter at `.opencode/agent/<name>.md`.
- Preserve existing prompt rules and safety policies without overwriting customized user instructions.

### Step 2: Canonical Directory Synchronization
```bash
!ockit verify --suite agents
!ockit verify --suite commands
```
- Remove legacy JSON definitions.
- Verify all workflows and skills align with OCKIT 2.0 native standards.
