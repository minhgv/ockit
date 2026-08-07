"""
test_portable_config.py — Portable opencode.json tests (R-017)

Verifies the packaged template AND the live repo config are free of personal
home paths, apiKeys, hardcoded author model pins, and author-only MCP/plugin
pins, and that the two trees stay byte-identical (no sync drift).
"""

from __future__ import annotations

import json
import os

import pytest

from ockit import __file__ as ockit_init_file

_PKG_DIR = os.path.dirname(os.path.abspath(ockit_init_file))
_TEMPLATE_CFG = os.path.join(_PKG_DIR, "templates", "opencode.json")
_ACTIVE_CFG = os.path.join(
    os.path.dirname(_PKG_DIR), "..", ".opencode", "opencode.json"
)

_HOME_PATH_PATTERNS = ["/Users/", "C:\\Users\\", "/home/"]


def _configs():
    return [_TEMPLATE_CFG, os.path.abspath(_ACTIVE_CFG)]


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.parametrize("cfg", _configs())
def test_config_is_valid_json(cfg):
    data = _load(cfg)
    assert data["$schema"].startswith("https://opencode.ai/")
    assert "lsp" in data
    assert "autoupdate" in data
    assert "share" in data


@pytest.mark.parametrize("cfg", _configs())
def test_no_home_paths(cfg):
    raw = open(cfg, encoding="utf-8").read()
    for pattern in _HOME_PATH_PATTERNS:
        assert pattern not in raw, f"personal home path '{pattern}' leaked in {cfg}"


@pytest.mark.parametrize("cfg", _configs())
def test_no_hardcoded_model_pins(cfg):
    data = _load(cfg)
    # Top-level model selection omitted so the consumer's global config applies.
    assert "model" not in data, "top-level 'model' pin must be omitted (portable)"
    assert "small_model" not in data, "top-level 'small_model' pin must be omitted"
    # Agent-level model pins are ALLOWED only when uniform and sanctioned.
    # The ockit agent suite defaults to the opencode-go gateway model so every
    # agent/subagent runs on the same cheap-fast model out of the box.
    _SANCTIONED_AGENT_MODEL = "opencode-go/deepseek-v4-flash"
    agents = data.get("agent", {})
    assert agents, "agent section must exist in portable config"
    for name, spec in agents.items():
        assert "model" in spec, f"agent '{name}' must carry a model pin"
        assert spec["model"] == _SANCTIONED_AGENT_MODEL, (
            f"agent '{name}' model pin '{spec['model']}' is not the sanctioned "
            f"'{_SANCTIONED_AGENT_MODEL}' (uniform default required)"
        )


@pytest.mark.parametrize("cfg", _configs())
def test_no_secret_literals(cfg):
    raw = open(cfg, encoding="utf-8").read()
    assert "apiKey" not in raw, "literal apiKey material in config"


@pytest.mark.parametrize("cfg", _configs())
def test_no_personal_external_directory(cfg):
    data = _load(cfg)
    ext = data.get("permission", {}).get("external_directory", {})
    for key in ext:
        if key != "*":
            assert not any(p in key for p in _HOME_PATH_PATTERNS), (
                f"personal external_directory entry '{key}' in {cfg}"
            )


@pytest.mark.parametrize("cfg", _configs())
def test_plugin_list_only_local(cfg):
    data = _load(cfg)
    for plugin in data.get("plugin", []):
        assert plugin.startswith("./plugin/"), (
            f"author-only external plugin pin '{plugin}' must not ship"
        )


def test_template_and_active_identical():
    with (
        open(_TEMPLATE_CFG, "rb") as fa,
        open(os.path.abspath(_ACTIVE_CFG), "rb") as fb,
    ):
        assert fa.read() == fb.read(), "opencode.json drifted between trees"
