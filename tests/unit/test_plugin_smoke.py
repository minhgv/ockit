"""
test_plugin_smoke.py — Plugin smoke tests (R-001, R-002 / ISSUE-01 + ISSUE-08)

Asserts every packaged ockit plugin:
- exports an async factory function returning the documented hook shape;
- never throws when the OpenCode runtime injects an absent / undefined
  ``client`` (BA-traceability after-hook must be best-effort per Art.7.3).

Three of the four plugins (ba-traceability, quality-gate, linter-fixer) import
only ``node:*`` builtins. The fourth (tdd-runner) imports ``@opencode-ai/plugin``
which is resolvable via ``.opencode/node_modules`` in this repo, so it too is
exercised via a dynamic ESM import through a ``node`` subprocess (top-level
``await`` requires ESM mode).

R-005: the token-monitor TUI plugin (``plugin/token-monitor/*.ts(x)``) is
EXCLUDED from this node ESM probe. It is a TypeScript TUI plugin registered via
``tui.json`` (not ``opencode.json``) and its contract (default export
``{ id, tui }``, ``sidebar_content`` slot, ``message.updated`` +
``session.next.step.*`` subscriptions) is exercised by the ported vitest suite
under ``.opencode`` (``npm --prefix .opencode test``) — see
``plans/SPEC_token_monitor_plugin.md`` R-005/R-015.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / ".opencode" / "plugin"

# Node ESM probe. argv[1] = plugin file path, argv[2] = mode.
# Parses stdout's LAST line as JSON (node may emit MODULE_TYPELESS warnings
# to stderr; only stdout holds our console.log payload).
_PROBE = r"""
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import fs from "node:fs";

const file = process.argv[1];
const mode = process.argv[2] || "shape";
const result = {};
try {
  const m = await import(pathToFileURL(resolve(file)).href);
  const exportKeys = Object.keys(m);
  result.exportKeys = exportKeys;
  const factoryName = exportKeys.find((k) => typeof m[k] === "function");
  if (!factoryName) throw new Error("no async factory function exported");
  result.factoryName = factoryName;

  if (mode === "shape") {
    let logCalls = 0;
    const stubClient = { app: { log: async () => { logCalls += 1; } } };
    const hooks = await m[factoryName]({ client: stubClient });
    result.hookKeys = Object.keys(hooks);
    result.logCallsAfterFactory = logCalls;
  } else if (mode === "r001_no_client") {
    // Invoke factory with NO client — simulates OpenCode runtime variance.
    const hooks = await m[factoryName]({});
    result.hookKeys = Object.keys(hooks);
    const after = hooks["tool.execute.after"];
    if (typeof after !== "function") {
      result.afterThrew = "NO_AFTER_HOOK";
    } else {
      // NOTE: probe content must NOT contain the literal substrings "RTM"
      // or "Edge Case" — otherwise the plugin's marker check short-circuits
      // and the warn-log path (the one we are stress-testing) never runs.
      const probe = resolve("plans/_smoke_probe_spec.md");
      fs.writeFileSync(probe, "# spec doc with no traceability markers here\n");
      let threw = null;
      try {
        await after({ tool: "write", args: { filePath: probe } });
      } catch (e) {
        threw = String(e);
      } finally {
        try { fs.unlinkSync(probe); } catch {}
      }
      result.afterThrew = threw;
    }
  }
  result.ok = true;
} catch (e) {
  result.ok = false;
  result.error = String(e);
  result.code = e.code || null;
}
console.log(JSON.stringify(result));
"""


def _run_probe(plugin_name: str, mode: str = "shape") -> dict:
    """Run the ESM import probe for one plugin and return parsed JSON result."""
    plugin_path = PLUGINS_DIR / f"ockit-{plugin_name}.js"
    if not plugin_path.exists():
        return {"ok": False, "error": f"plugin file missing: {plugin_path}"}
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", _PROBE, str(plugin_path), mode],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=20,
    )
    stdout_lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not stdout_lines:
        return {
            "ok": False,
            "error": (
                f"node probe emitted no stdout; exit={proc.returncode}; "
                f"stderr={proc.stderr[-500:]}"
            ),
        }
    try:
        return json.loads(stdout_lines[-1])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"non-JSON stdout: {stdout_lines[-1][:200]} ({exc})",
        }


def test_r002_all_plugins_export_valid_hook_shape():
    """R-002: each of the 4 plugins exports an async factory + ≥1 hook key."""
    for name in ("ba-traceability", "quality-gate", "linter-fixer", "tdd-runner"):
        res = _run_probe(name, "shape")
        assert res.get("ok") is True, (
            "What=plugin import/factory failed; "
            f"Context=plugin 'ockit-{name}.js' probe result={res}; "
            "Fix=ensure the plugin exports an async factory returning a hooks object "
            "and that all imports resolve (node:* builtins or .opencode/node_modules)."
        )
        assert res.get("factoryName"), (
            "What=no async factory export; "
            f"Context=plugin 'ockit-{name}.js' exports={res.get('exportKeys')}; "
            "Fix=export an async function as a named export."
        )
        assert res.get("hookKeys"), (
            "What=factory returned empty hooks; "
            f"Context=plugin 'ockit-{name}.js' returned no hook keys; "
            "Fix=return an object with ≥1 documented hook key "
            "(tool.execute.before|tool.execute.after|tool)."
        )


def test_r001_ba_traceability_no_throw_without_client():
    """R-001: BA-traceability after-hook MUST NOT throw when client is absent."""
    res = _run_probe("ba-traceability", "r001_no_client")
    assert res.get("ok") is True, (
        "What=ba-traceability plugin import failed; "
        f"Context=probe result={res}; "
        "Fix=ensure the plugin module loads cleanly under dynamic ESM import."
    )
    assert res.get("afterThrew") is None, (
        "What=tool.execute.after hook threw when client was undefined; "
        f"Context=plugin '.opencode/plugin/ockit-ba-traceability.js' threw: "
        f"{res.get('afterThrew')!r}; "
        "Fix=guard the client.app.log(...) call with `if (client?.app?.log)` + "
        "try/catch swallow (logging is best-effort, Art.7.3)."
    )
