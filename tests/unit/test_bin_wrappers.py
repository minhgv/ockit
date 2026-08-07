"""
test_bin_wrappers.py — Thin bin wrapper tests (R-011, R-026, R-027)

Validates the post-nativization bin surface: exactly three thin bash wrappers,
each ≤30 lines and executable, each forwarding to the ockit CLI with the
agy-kit fallback (``ockit`` on PATH, else ``.venv/bin/ockit``, else exit 1).

ACM edge mapping (R-025):
- E-011  -> test_bin_surface_exactly_three + wrappers forward to ockit (allowed
           wrapper set in verify.py ALLOWED_BIN_WRAPPERS)
- R-011  -> test_wrapper_*_forwards_to_ockit_* (compat scripts still invokable)
- R-026  -> test_bin_surface_exactly_three (≤3 wrappers) + line-count tests
- R-027  -> test_wrapper_headers_cite_agy_kit (provenance)
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN_DIR = os.path.join(REPO_ROOT, "bin")

EXPECTED_WRAPPERS = sorted(
    [
        "validate-traceability.sh",
        "validate-phase10-ba-qa.sh",
        "scan-dependencies.sh",
    ]
)

# command the wrapper must prepend (argv[0] of the ockit call)
WRAPPER_CMD = {
    "validate-traceability.sh": ["verify"],
    "validate-phase10-ba-qa.sh": ["verify", "--suite", "ba-qa"],
    "scan-dependencies.sh": ["scan-deps"],
}


def _wrapper_path(name: str) -> str:
    return os.path.join(BIN_DIR, name)


def _write_shim(dirpath: str, exit_code: int = 0) -> str:
    """Creates an `ockit` shim that records "$@" to OCKIT_ARGS_FILE."""
    shim = os.path.join(dirpath, "ockit")
    with open(shim, "w", encoding="utf-8") as fh:
        fh.write(
            "#!/usr/bin/env bash\n"
            'printf \'%s\\n\' "$@" > "${OCKIT_ARGS_FILE}"\n'
            f"exit {exit_code}\n"
        )
    os.chmod(shim, 0o755)
    return shim


# ---------------------------------------------------------------------------
# R-026 — surface & shape
# ---------------------------------------------------------------------------


def test_bin_surface_exactly_three_wrappers():
    files = sorted(f for f in os.listdir(BIN_DIR) if f.endswith(".sh"))
    assert files == EXPECTED_WRAPPERS


@pytest.mark.parametrize("name", EXPECTED_WRAPPERS)
def test_wrapper_exists_executable(name):
    path = _wrapper_path(name)
    assert os.path.isfile(path)
    mode = os.stat(path).st_mode
    assert mode & stat.S_IXUSR, f"{name} must be executable (chmod +x)"


@pytest.mark.parametrize("name", EXPECTED_WRAPPERS)
def test_wrapper_shebang(name):
    with open(_wrapper_path(name), encoding="utf-8") as fh:
        assert fh.readline().strip() == "#!/usr/bin/env bash"


@pytest.mark.parametrize("name", EXPECTED_WRAPPERS)
def test_wrapper_max_30_lines(name):
    with open(_wrapper_path(name), encoding="utf-8") as fh:
        lines = fh.readlines()
    assert len(lines) <= 30, f"{name} exceeds 30 lines (NFR bin surface)"


@pytest.mark.parametrize("name", EXPECTED_WRAPPERS)
def test_wrapper_headers_cite_agy_kit(name):
    with open(_wrapper_path(name), encoding="utf-8") as fh:
        content = fh.read()
    assert "agy-kit" in content, f"{name} missing agy-kit provenance header (R-027)"
    assert "github.com/giapminh79/agy-kit" in content


# ---------------------------------------------------------------------------
# R-011 — wrappers exec ockit and forward argv / exit codes
# ---------------------------------------------------------------------------


def _run_wrapper(name, cwd, env, *args):
    return subprocess.run(
        ["bash", _wrapper_path(name), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _env_with_shim(tmp_path):
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    _write_shim(str(shim_dir))
    args_file = tmp_path / "args.txt"
    env = dict(os.environ)
    env["PATH"] = str(shim_dir) + os.pathsep + env["PATH"]
    env["OCKIT_ARGS_FILE"] = str(args_file)
    return env, str(args_file)


def test_wrapper_traceability_forwards_verify(tmp_path):
    env, args_file = _env_with_shim(tmp_path)
    res = _run_wrapper("validate-traceability.sh", str(tmp_path), env)
    assert res.returncode == 0
    recorded = open(args_file, encoding="utf-8").read().splitlines()
    assert recorded[0] == "verify"


def test_wrapper_traceability_passthrough_args(tmp_path):
    env, args_file = _env_with_shim(tmp_path)
    res = _run_wrapper(
        "validate-traceability.sh", str(tmp_path), env, "--suite", "traceability"
    )
    assert res.returncode == 0
    recorded = open(args_file, encoding="utf-8").read().splitlines()
    assert recorded == ["verify", "--suite", "traceability"]


def test_wrapper_ba_qa_forwards_suite(tmp_path):
    env, args_file = _env_with_shim(tmp_path)
    res = _run_wrapper("validate-phase10-ba-qa.sh", str(tmp_path), env)
    assert res.returncode == 0
    recorded = open(args_file, encoding="utf-8").read().splitlines()
    assert recorded == ["verify", "--suite", "ba-qa"]


def test_wrapper_scan_deps_forwards(tmp_path):
    env, args_file = _env_with_shim(tmp_path)
    res = _run_wrapper("scan-dependencies.sh", str(tmp_path), env)
    assert res.returncode == 0
    recorded = open(args_file, encoding="utf-8").read().splitlines()
    assert recorded == ["scan-deps"]


def test_wrapper_forwards_exit_code(tmp_path):
    # Shim exits 3 → wrapper must propagate (exec passthrough, R-011).
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    _write_shim(str(shim_dir), exit_code=3)
    env = dict(os.environ)
    env["PATH"] = str(shim_dir) + os.pathsep + env["PATH"]
    res = _run_wrapper("validate-traceability.sh", str(tmp_path), env)
    assert res.returncode == 3


def test_wrapper_falls_back_to_venv_bin(tmp_path):
    # No `ockit` on PATH; `.venv/bin/ockit` relative to cwd must be used.
    venv_bin = tmp_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    args_file = tmp_path / "args.txt"
    _write_shim(str(venv_bin))
    env = dict(os.environ)
    env["PATH"] = "/usr/bin:/bin"  # hide any real ockit
    env["OCKIT_ARGS_FILE"] = str(args_file)
    res = _run_wrapper("validate-traceability.sh", str(tmp_path), env)
    assert res.returncode == 0
    recorded = open(args_file, encoding="utf-8").read().splitlines()
    assert recorded[0] == "verify"


@pytest.mark.parametrize("name", EXPECTED_WRAPPERS)
def test_wrapper_errors_when_ockit_unavailable(tmp_path, name):
    env = dict(os.environ)
    env["PATH"] = "/usr/bin:/bin"
    res = _run_wrapper(name, str(tmp_path), env)
    assert res.returncode == 1
    assert "ockit" in res.stderr
    assert "pip install" in res.stderr
