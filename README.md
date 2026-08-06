# ockit — OpenCode Kit (v1.0)

> **OpenCode-Native Autonomous Agent Engineering Scaffold & Plugin Suite** — Designed exclusively for **OpenCode CLI (`opencode`)**. Provides multi-provider flexibility, native OpenCode plugins, 14 slash commands, Business Analysis (BA) RTM traceability, strict TDD execution, and isolated Git worktree management.

---

## Key Features

1. **Native OpenCode Plugins (`.opencode/plugins/`)**:
   - `ockit-quality-gate.js`: Path boundary guard & secret scanning pre-tool hook.
   - `ockit-ba-traceability.js`: Enforces Requirement Traceability Matrix (RTM) & 12D Edge Case Matrix.
   - `ockit-tdd-runner.js`: Multi-language TDD test execution (Python, TS, Go, Rust, PHP).
   - `ockit-linter-fixer.js`: Autonomous linter fixer & shebang permission fixer.

2. **OpenCode Subagents (`.opencode/agents/*.md`)**:
   - `planner`: Lead System Architect & BA Specialist
   - `coder`: Senior Developer (TDD RED-GREEN-REFACTOR)
   - `reviewer`: Principal Code & Security Auditor
   - `qa`: E2E QA Automation Engineer

3. **14 Native OpenCode Commands (`.opencode/command/`)**:
   `/brainstorm`, `/plan`, `/grill`, `/pipeline`, `/safe-pipeline`, `/gate`, `/review`, `/qa`, `/solve`, `/doctor`, `/init`, `/learn`, `/schedule`, `/migrate`.

4. **Dedicated `ockit` CLI Tool**:
   - `ockit init [target]`: Scaffold `.opencode/` into any target project directory.
   - `ockit doctor`: Probe environment, toolchains, and plugin health.
   - `ockit verify`: Audit RTM traceability and command compliance.
   - `ockit sync`: Synchronize active assets with `src/templates/`.

---

## Quick Start

```bash
# 1. Install ockit in editable mode
pip install -e .

# 2. Run system health diagnostics
ockit doctor

# 3. Initialize ockit scaffold into a target repository
ockit init --target ./my-app --lang python

# 4. Verify project requirement traceability
ockit verify
```

---

## License

[MIT](LICENSE) © 2026 MinhGV
