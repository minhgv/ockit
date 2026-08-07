---
description: "Run opencode-doctor diagnostics — audit system health, CLI version, authentication, subagent specs, skills, MCP servers, and language toolchains."
---

# /doctor

Run environment, subagent, skill, and toolchain diagnostics using `bin/opencode-doctor.sh`.

## Steps

### Step 1: Health & System Audit
```bash
./bin/opencode-doctor.sh
```

### Step 2: Diagnostic Synthesis & Remediation
Invoke the **`reviewer`** subagent (`.opencode/agent/reviewer.md`):
- Review the output of `bin/opencode-doctor.sh`.
- If any `[FAIL]` or `[WARN]` items are reported (such as missing language linter, unauthenticated CLI, or missing MCP server), provide step-by-step resolution commands.
