# ockit — OpenCode Kit (v1.0)

> **OpenCode-Native Autonomous Agent Engineering Scaffold & Plugin Suite** — Designed exclusively for **OpenCode CLI (`opencode`)**. Provides multi-provider flexibility, native OpenCode plugins, 14 slash commands, Business Analysis (BA) RTM traceability, strict TDD execution, and isolated Git worktree management.

---

## Key Features

1. **Native OpenCode Plugins (`.opencode/plugin/`)**:
   - `ockit-quality-gate.js`: Path boundary guard & secret scanning pre-tool hook.
   - `ockit-ba-traceability.js`: Enforces Requirement Traceability Matrix (RTM) & 12D Edge Case Matrix.
   - `ockit-tdd-runner.js`: Multi-language TDD test execution (Python, TS, Go, Rust, PHP).
   - `ockit-linter-fixer.js`: Autonomous linter fixer & shebang permission fixer.

2. **OpenCode Subagents (`.opencode/agent/`, 5 custom agents)**:
   - `orchestrator` (**primary**): coordinates planning / coding / review / QA runs.
   - `planner`: Lead System Architect & BA Specialist (**subagent**)
   - `coder`: Senior Developer, TDD RED-GREEN-REFACTOR (**subagent**)
   - `reviewer`: Principal Code & Security Auditor (**subagent**)
   - `qa`: E2E QA Automation Engineer (**subagent**)

3. **14 Native OpenCode Commands (`.opencode/command/`)**:
   `/brainstorm`, `/plan`, `/grill`, `/pipeline`, `/safe-pipeline`, `/gate`, `/review`, `/qa`, `/solve`, `/doctor`, `/ockit-init`, `/learn`, `/schedule`, `/migrate`.
   Commands are nativized: they call the `ockit` CLI via `!ockit …` verbs and use native `subtask`/`agent` frontmatter instead of shell scripts.

4. **Dedicated `ockit` CLI Tool**:

   | Command | Description |
   |---------|-------------|
   | `ockit init --target <dir> [--lang <lang>] [--force] [--dry-run]` | Scaffold `.opencode/` + root `AGENTS.md` from packaged templates |
   | `ockit doctor` | Probe environment, toolchains, and plugin health |
   | `ockit verify [--suite all\|traceability\|ba-qa\|agents\|commands]` | Audit RTM traceability and workflow compliance |
   | `ockit sync [--check\|--sync]` | Drift check / sync active `.opencode/` vs templates (default: `--check`) |
   | `ockit scan-deps` | Scan dependency files for slopsquatting / insecure URLs |

5. **Thin `bin/` wrappers** (legacy CI muscle memory — logic lives in the CLI):
   - `bin/validate-traceability.sh` → `ockit verify`
   - `bin/validate-phase10-ba-qa.sh` → `ockit verify --suite ba-qa`
   - `bin/scan-dependencies.sh` → `ockit scan-deps`

   Templates ship inside the package at `src/ockit/templates/` (`agent/`, `command/`, `plugin/`, `skill/`, `opencode.json`, `AGENTS.md`) and are installed by `ockit init`; `ockit sync` keeps active assets in sync with them.

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
