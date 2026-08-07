# AGENTS.md — ockit Repository Rules

> **ockit** — OpenCode-Native Autonomous Agent Engineering Scaffold & Plugin Suite. Provides `ockit init` to scaffold `.opencode/` assets and root `AGENTS.md` into target projects, plus audit tooling (`doctor`, `verify`, `sync`, `scan-deps`).

## 1. Commands

| Command | Purpose |
|---------|---------|
| `ockit init --target <dir> [--force] [--dry-run]` | Scaffold `.opencode/` + root `AGENTS.md` from packaged templates (path-safe: traversal/symlink-escape rejected) |
| `ockit doctor` | Environment health probe |
| `ockit verify` | Requirement traceability / workflow audit |
| `ockit sync` | Drift check/sync between active `.opencode/` and packaged templates |
| `ockit scan-deps` | Dependency pattern scan |
| `python -m pytest tests/ -q` | Run the full test suite |

## 2. Key Constraints

- **Packaged templates live in `src/ockit/templates/`.** Never write scaffold content anywhere else — `src/templates/` was deleted to avoid a dual source of truth. Template changes ship in the wheel via `[tool.setuptools.package-data] ockit`.
- **TDD strictly**: write failing tests first (RED), then implement (GREEN), then refactor. Existing tests must keep passing.
- **Path safety**: every `--target` goes through `validators.resolve_safe_target()`; no `shell=True`; no new runtime dependencies beyond `jsonschema`.
- **3-Dimensional errors**: What / Context / Fix on every thrown or returned error.
- **No secret leakage**: templates must never contain personal home paths, apiKeys, or machine-specific MCP/plugin pins (portable `opencode.json`).
- **Backward compatibility**: preserve existing CLI subcommand names and public module APIs.
- Follow conventional commits; group commits into coherent feature units.
