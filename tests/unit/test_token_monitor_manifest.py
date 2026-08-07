"""
test_token_monitor_manifest.py — token-monitor TUI plugin port manifest tests
(R-001..R-018, ACM E-012 / E-015 / E-020 / E-021 / E-022)

Static filesystem + content assertions proving the approved
``plans/SPEC_token_monitor_plugin.md`` port landed:

- R-001/R-005: core plugin source + ported vitest suites present in
  ``.opencode/plugin/token-monitor/``.
- R-002: ``.opencode/tui.json`` registers ``./plugin/token-monitor`` (E-020).
- R-003: runtime deps pinned to proven source versions (E-015/E-021).
- R-004/R-018: dev deps + ``test``/``type-check`` scripts (npm --prefix .opencode test).
- R-006/R-007: vitest + tsconfig type-check infra.
- R-008: TEMPORARY debug logging (``/tmp/token-monitor-debug.log``) stripped (E-022).
- R-009..R-011: template mirror under ``src/ockit/templates/`` byte-identical.
- R-017: no personal paths / secrets / machine pins in shipped files.
- E-012: ported vitest suite retains burst/accumulation coverage.

These are static manifest checks (fast, hermetic). The ported vitest suite is
executed separately via ``npm --prefix .opencode test`` (``make test-destructive``).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_PLUGIN_DIR = REPO_ROOT / ".opencode" / "plugin" / "token-monitor"
TEMPLATE_PLUGIN_DIR = (
    REPO_ROOT / "src" / "ockit" / "templates" / "plugin" / "token-monitor"
)
ACTIVE_PKG = REPO_ROOT / ".opencode" / "package.json"
TEMPLATE_PKG = REPO_ROOT / "src" / "ockit" / "templates" / "package.json"
ACTIVE_TUI = REPO_ROOT / ".opencode" / "tui.json"
TEMPLATE_TUI = REPO_ROOT / "src" / "ockit" / "templates" / "tui.json"

# Core source modules copied verbatim (R-001) + ported test suites (R-005).
CORE_FILES = (
    "config.ts",
    "index.ts",
    "lifecycle.ts",
    "solid-runtime.ts",
    "store-runtime.ts",
    "token-state.ts",
    "token-panel.tsx",
)
PORTED_TESTS = ("index.test.ts", "index.integration.test.ts")
PLUGIN_FILES = CORE_FILES + PORTED_TESTS

# R-003 approved pins (SPEC decision D1, source-proven on @opencode-ai/plugin 1.18.12).
RUNTIME_DEPS = {
    "@opencode-ai/plugin": "^1.18.12",
    "solid-js": "1.9.12",
    "@opentui/core": "0.4.5",
    "@opentui/solid": "0.4.5",
}
DEV_DEPS = ("vitest", "typescript", "@types/node", "bun-types")

# R-017 portability fingerprints — personal home paths, debug log paths and
# secret-shaped literals that must never ship.
_FORBIDDEN_PATTERNS = [
    re.compile(r"/Users/[^/]+", re.IGNORECASE),
    re.compile(r"/tmp/"),
    re.compile(r"TOKEN_MONITOR_DEBUG"),
    re.compile(r"token-monitor-debug\.log"),
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),
    re.compile(r"api[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestR001CoreFiles:
    def test_r001_core_files_present(self):
        """R-001: 7 core modules copied into .opencode/plugin/token-monitor/."""
        missing = [f for f in CORE_FILES if not (ACTIVE_PLUGIN_DIR / f).is_file()]
        assert not missing, (
            "What=core token-monitor modules missing; "
            f"Context=active plugin dir '{ACTIVE_PLUGIN_DIR}' lacks {missing}; "
            "Fix=copy the 7 source modules from the approved source repo."
        )

    def test_r005_ported_suite_present(self):
        """R-005: ported vitest suites present (index.test.ts + integration)."""
        missing = [f for f in PORTED_TESTS if not (ACTIVE_PLUGIN_DIR / f).is_file()]
        assert not missing, (
            "What=ported vitest suites missing; "
            f"Context=active plugin dir '{ACTIVE_PLUGIN_DIR}' lacks {missing}; "
            "Fix=port index.test.ts + index.integration.test.ts verbatim."
        )


class TestR002TuiJson:
    def test_r002_tui_json_entry(self):
        """R-002 / E-020: tui.json registers ./plugin/token-monitor."""
        assert ACTIVE_TUI.is_file(), (
            "What=active tui.json missing; "
            f"Context=expected '{ACTIVE_TUI}'; "
            "Fix=create .opencode/tui.json with a plugin array."
        )
        data = _read_json(ACTIVE_TUI)
        plugins = data.get("plugin")
        assert isinstance(plugins, list) and "./plugin/token-monitor" in plugins, (
            "What=tui.json does not register the token-monitor plugin; "
            f"Context=tui.json plugin array = {plugins!r}; "
            'Fix=add "./plugin/token-monitor" to the plugin array.'
        )


class TestR003Deps:
    def test_r003_dependencies_pinned(self):
        """R-003 / E-015 / E-021: runtime deps pinned to proven source versions."""
        assert ACTIVE_PKG.is_file(), (
            "What=.opencode/package.json missing; "
            f"Context=expected '{ACTIVE_PKG}'; "
            "Fix=create .opencode/package.json with the approved dependency set."
        )
        data = _read_json(ACTIVE_PKG)
        deps = data.get("dependencies", {})
        for name, pin in RUNTIME_DEPS.items():
            assert deps.get(name) == pin, (
                "What=runtime dep not pinned to approved version; "
                f"Context=expected {name}={pin}, got {deps.get(name)!r}; "
                "Fix=bump the dependency per SPEC decision D1 (source-proven pins)."
            )


class TestR004Infra:
    def test_r004_devdeps_and_scripts(self):
        """R-004: dev deps + test/type-check scripts present."""
        data = _read_json(ACTIVE_PKG)
        dev = data.get("devDependencies", {})
        missing = [d for d in DEV_DEPS if not dev.get(d)]
        assert not missing, (
            "What=dev deps missing; "
            f"Context=package.json devDependencies lacks {missing}; "
            "Fix=add vitest/typescript/@types/node/bun-types to devDependencies."
        )
        scripts = data.get("scripts", {})
        assert scripts.get("test"), (
            "What=test script missing; "
            "Context=package.json scripts has no 'test'; "
            "Fix=add 'test': 'vitest run' (R-018: npm --prefix .opencode test)."
        )
        assert scripts.get("type-check"), (
            "What=type-check script missing; "
            "Context=package.json scripts has no 'type-check'; "
            "Fix=add 'type-check': 'tsc --noEmit -p plugin/tsconfig.typecheck.json'."
        )

    def test_r018_test_command(self):
        """R-018: test command runnable via npm --prefix .opencode test."""
        data = _read_json(ACTIVE_PKG)
        assert "test" in data.get("scripts", {}), (
            "What=test command not documented; "
            "Context=package.json scripts.test absent; "
            "Fix=define scripts.test so 'npm --prefix .opencode test' works."
        )


class TestR006Vitest:
    def test_r006_vitest_config(self):
        """R-006: vitest.config.ts scoped to plugin/**/*.test.ts."""
        cfg = REPO_ROOT / ".opencode" / "vitest.config.ts"
        assert cfg.is_file(), (
            "What=vitest config missing; "
            f"Context=expected '{cfg}'; "
            "Fix=add .opencode/vitest.config.ts."
        )
        text = cfg.read_text(encoding="utf-8")
        assert 'include: ["plugin/**/*.test.ts"]' in text, (
            "What=vitest include scope wrong; "
            f"Context=config must include 'plugin/**/*.test.ts'; got:\n{text}; "
            "Fix=scope the vitest run to plugin test files."
        )
        # R-012/E-032 scaffold contract: the harness must ship in templates so
        # scaffolded targets can run `npm test` / `npm run type-check`.
        tpl = REPO_ROOT / "src" / "ockit" / "templates" / "vitest.config.ts"
        assert tpl.is_file() and tpl.read_bytes() == cfg.read_bytes(), (
            "What=template vitest.config.ts missing or drifted; "
            f"Context=template must byte-match active '{cfg}'; "
            "Fix=mirror .opencode/vitest.config.ts into src/ockit/templates/."
        )


class TestR007Tsconfig:
    def test_r007_tsconfig(self):
        """R-007: type-check infra (noEmit + bundler base + typecheck override)."""
        base = REPO_ROOT / ".opencode" / "tsconfig.json"
        override = REPO_ROOT / ".opencode" / "plugin" / "tsconfig.typecheck.json"
        assert base.is_file(), (
            "What=base tsconfig missing; "
            f"Context=expected '{base}'; "
            "Fix=add .opencode/tsconfig.json (noEmit, moduleResolution bundler)."
        )
        base_data = _read_json(base)
        opts = base_data.get("compilerOptions", {})
        assert opts.get("noEmit") is True, (
            "What=tsconfig noEmit unset; "
            "Context=type-check must not emit; "
            "Fix=set compilerOptions.noEmit=true."
        )
        assert opts.get("moduleResolution") == "bundler", (
            "What=tsconfig moduleResolution wrong; "
            f"Context=expected 'bundler', got {opts.get('moduleResolution')!r}; "
            "Fix=set compilerOptions.moduleResolution=bundler."
        )
        assert override.is_file(), (
            "What=typecheck override missing; "
            f"Context=expected '{override}'; "
            "Fix=add plugin/tsconfig.typecheck.json extending the base."
        )
        over_text = override.read_text(encoding="utf-8")
        assert '"extends": "../tsconfig.json"' in over_text, (
            "What=typecheck override does not extend base; "
            f"Context={override} content:\n{over_text}; "
            "Fix=extend ../tsconfig.json."
        )
        assert "token-monitor/**/*.ts" in over_text, (
            "What=typecheck override omits token-monitor; "
            f"Context={override} content:\n{over_text}; "
            "Fix=include token-monitor/**/*.ts and token-monitor/**/*.tsx."
        )
        # R-012/E-032 scaffold contract: tsconfig harness must ship in templates
        # so scaffolded targets can run `npm run type-check` (the template
        # package.json script references plugin/tsconfig.typecheck.json).
        tpl_base = REPO_ROOT / "src" / "ockit" / "templates" / "tsconfig.json"
        tpl_override = (
            REPO_ROOT
            / "src"
            / "ockit"
            / "templates"
            / "plugin"
            / "tsconfig.typecheck.json"
        )
        assert tpl_base.is_file() and tpl_base.read_bytes() == base.read_bytes(), (
            "What=template tsconfig.json missing or drifted; "
            f"Context=template must byte-match active '{base}'; "
            "Fix=mirror .opencode/tsconfig.json into src/ockit/templates/."
        )
        assert (
            tpl_override.is_file()
            and tpl_override.read_bytes() == override.read_bytes()
        ), (
            "What=template plugin/tsconfig.typecheck.json missing or drifted; "
            f"Context=template must byte-match active '{override}'; "
            "Fix=mirror .opencode/plugin/tsconfig.typecheck.json into "
            "src/ockit/templates/plugin/."
        )


class TestR008NoDebugLog:
    def test_r008_no_debug_log(self):
        """R-008 / E-022: TEMPORARY debug logging stripped from index.ts."""
        idx = ACTIVE_PLUGIN_DIR / "index.ts"
        text = idx.read_text(encoding="utf-8")
        forbidden = ["appendFileSync", "TOKEN_MONITOR_DEBUG", "token-monitor-debug.log"]
        hits = [tok for tok in forbidden if tok in text]
        assert not hits, (
            "What=TEMPORARY debug logging not stripped; "
            f"Context=index.ts still contains {hits}; "
            "Fix=remove the debug block (source comment says 'Remove before finalizing')."
        )
        assert "/tmp/" not in text, (
            "What=hardcoded /tmp path remains in index.ts; "
            "Context=portable plugin must not write /tmp; "
            "Fix=strip the debug log block per R-008."
        )


class TestR009TemplatesMirror:
    def test_r009_templates_mirror(self):
        """R-009: all 9 plugin files mirrored byte-identical into templates."""
        missing = [f for f in PLUGIN_FILES if not (TEMPLATE_PLUGIN_DIR / f).is_file()]
        assert not missing, (
            "What=template mirror missing files; "
            f"Context={TEMPLATE_PLUGIN_DIR} lacks {missing}; "
            "Fix=mirror the active plugin into src/ockit/templates/plugin/token-monitor/."
        )
        mismatched = []
        for f in PLUGIN_FILES:
            a = (ACTIVE_PLUGIN_DIR / f).read_bytes()
            t = (TEMPLATE_PLUGIN_DIR / f).read_bytes()
            if a != t:
                mismatched.append(f)
        assert not mismatched, (
            "What=template mirror drifted from active plugin; "
            f"Context=content mismatch on {mismatched}; "
            "Fix=re-copy active files into templates (ockit sync contract, R-012)."
        )


class TestR010TemplatesTuiJson:
    def test_r010_templates_tui_json(self):
        """R-010: template tui.json mirrors active byte-identical."""
        assert TEMPLATE_TUI.is_file(), (
            "What=template tui.json missing; "
            f"Context=expected '{TEMPLATE_TUI}'; "
            "Fix=mirror .opencode/tui.json into src/ockit/templates/tui.json."
        )
        assert ACTIVE_TUI.read_bytes() == TEMPLATE_TUI.read_bytes(), (
            "What=template tui.json drifted from active; "
            "Context=bytes differ; "
            "Fix=mirror active tui.json into templates."
        )


class TestR011TemplatesPackageJson:
    def test_r011_templates_package_json(self):
        """R-011: template package.json declares the plugin runtime deps."""
        assert TEMPLATE_PKG.is_file(), (
            "What=template package.json missing; "
            f"Context=expected '{TEMPLATE_PKG}'; "
            "Fix=add src/ockit/templates/package.json so scaffolded targets can "
            "npm install the token-monitor runtime deps."
        )
        data = _read_json(TEMPLATE_PKG)
        deps = data.get("dependencies", {})
        for name, pin in RUNTIME_DEPS.items():
            assert deps.get(name) == pin, (
                "What=template package.json missing runtime dep; "
                f"Context=expected {name}={pin}, got {deps.get(name)!r}; "
                "Fix=declare all token-monitor runtime deps in the template."
            )


class TestR017NoLeaks:
    def test_r017_no_leaks(self):
        """R-017: no personal paths / secrets / machine pins in shipped files."""
        scan_targets = [ACTIVE_PLUGIN_DIR, TEMPLATE_PLUGIN_DIR]
        files = []
        for d in scan_targets:
            if d.is_dir():
                files.extend(d.glob("*.ts"))
                files.extend(d.glob("*.tsx"))
        for extra in (ACTIVE_TUI, TEMPLATE_TUI, ACTIVE_PKG, TEMPLATE_PKG):
            if extra.is_file():
                files.append(extra)

        assert files, (
            "What=no files scanned for leaks; "
            "Context=plugin/template tree empty; "
            "Fix=ensure plugin + templates exist before scanning."
        )

        leaked = {}
        for path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in _FORBIDDEN_PATTERNS:
                m = pattern.search(text)
                if m:
                    leaked.setdefault(str(path), []).append(m.group(0))
        assert not leaked, (
            "What=portability violation in shipped files; "
            f"Context=forbidden patterns {leaked}; "
            "Fix=strip personal paths, /tmp debug logging and secret-shaped "
            "literals per ockit AGENTS.md (portable opencode.json, no leaked config)."
        )


class TestEdge12BurstCoverage:
    def test_e012_burst_accumulation_covered(self):
        """ACM E-012: ported suite retains rapid-fire accumulation coverage."""
        test_file = ACTIVE_PLUGIN_DIR / "index.test.ts"
        text = test_file.read_text(encoding="utf-8")
        assert "accumulates same model across multiple messages" in text, (
            "What=ported suite lost burst accumulation case; "
            f"Context={test_file} lacks the burst accumulation test; "
            "Fix=keep the ported index.test.ts verbatim."
        )
        assert "subscribes to tick signal" in text, (
            "What=ported suite lost render reactivity case; "
            f"Context={test_file} lacks the tick reactivity test; "
            "Fix=keep the ported index.test.ts verbatim."
        )
