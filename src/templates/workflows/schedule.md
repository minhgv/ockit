---
description: "Schedule background audit tasks & recurring timers — configure timer notifications or cron checks for security scanning, health diagnostics, and dependency audits."
---

# /schedule

Configure recurring background audit tasks or one-shot timers for project health monitoring.

## Steps

### Step 1: Audit Schedule Specification
Invoke the **`qa`** subagent (`.agents/agents/qa.md`):
- Define scheduled task target for `$ARGUMENTS` (e.g., dependency security scan, health check, quality gate audit).
- Set interval or timer duration (e.g., one-shot timer or recurring cron check).

### Step 2: Automated Execution & Alerting
```bash
./bin/scan-dependencies.sh
```
- Capture background audit logs.
- If vulnerability or regression is detected, emit notification for remediation.
