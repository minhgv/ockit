# AGENTS.md — ockit Scaffolded Project Rules

> This project was scaffolded by **ockit** (`ockit init`). It ships rules, agents, commands, plugins, and skills that keep AI agents working safely and predictably inside OpenCode.

## 1. Commands Available After Init

Run `ockit --help` for the full CLI. Key commands:

| Command | Purpose |
|---------|---------|
| `ockit init` | Re-run scaffolding (idempotent; `--force` to overwrite with backup, `--dry-run` to preview) |
| `ockit doctor` | Health check for git, OpenCode, config, agents, plugins, skills, commands |
| `ockit verify` | Requirement traceability + workflow audit |
| `ockit sync` | Synchronize active `.opencode/` assets with packaged templates |

## 2. Planning First Rule

- Any feature touching >3 files or changing architecture MUST create `plans/SPEC_<feature>.md` first.
- SPEC must include: use-cases, data flow, files to modify/create, API schema, edge-cases, backward compatibility.
- **DO NOT create or modify code files** during the Plan phase.

## 3. Test-Driven Development (TDD)

- Every new logic must ship with Unit/Integration Test.
- Enforce RED → GREEN → REFACTOR cycle. Confirm the test FAILS before writing the implementation.

## 4. Strict Quality Gates

- Linter & Typecheck: 0 errors, 0 warnings.
- **NEVER hardcode** secrets, API keys, or passwords into the codebase; use environment variables or a secrets manager.
- Security review (OWASP-aware) mandatory before merge for sensitive features.

## 5. Git Convention

- Group commits into complete feature units; follow Conventional Commits.
- **DO NOT commit** single files one by one; commit after coherent units of work.

## 6. Agentic Workflow

```
[Plan] → [TDD] → [Quality Gate] → [E2E QA] → [Review & Commit]
```

## 7. Safety & Recovery

- Before a subagent modifies code, create a git checkpoint (`git stash` or temp commit).
- After modifying code, run the test runner. If tests FAIL → auto-rollback to the clean checkpoint.
- Path safety is enforced on `ockit init --target`: traversal and symlink-escape targets are rejected.
- Max 3 retries per failing test → if exceeded, STOP and escalate.

## 8. Multi-Language Support

- Detect the project language via its root indicator file (`pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, `package.json`).
- Run the toolchain for that language (linter, formatter, typechecker, test runner).
