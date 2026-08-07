"""
scan_deps.py — Supply chain pattern scanner for `ockit scan-deps`

Ports agy-kit's ``bin/scan-dependencies.sh`` into Python (R-012). Per SPEC
Non-Goals, this is a PATTERN scan only: no network access, no CVE/OSV database.
Slopsquat-looking names and insecure ``http://`` URLs are errors (exit 1);
unpinned versions are warnings (exit 0).

Source reference: https://github.com/giapminh79/agy-kit/tree/main/bin/scan-dependencies.sh
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# OWASP-AI-01 hallucinated / slopsquatting dependency name signatures.
SLOPSQUAT_PATTERNS = (
    "fastapi-utils-v2",
    "react-helper-lib",
    "python-crypto",
    "requests-async-v2",
    "langchain-core-plus",
    "flask-utils-v2",
)

# Dependency manifest/lock files scanned anywhere under the project root.
DEPENDENCY_FILENAMES = {
    "requirements.txt",
    "pyproject.toml",
    "Pipfile.lock",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "composer.json",
    "composer.lock",
}

# Directories skipped during the recursive walk (noise / vendored deps).
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".opencode",
}

# Insecure registry URLs over plain HTTP (MITM risk). Local registries are safe.
_INSECURE_HTTP_RE = re.compile(r"http://(?!localhost|127\.0\.0\.1|\[::1\])(\S+)")

# Python package name: strip extras/constraints/comments.
_REQ_RE = re.compile(r"^([A-Za-z0-9_.\-\[\]]+)")


@dataclass
class ScanDepsReport:
    """Structured scan result (ScanDepsReport schema, section 3)."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scanned_files: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return 1 if self.errors else 0


def _is_local_http(url: str) -> bool:
    lowered = url.lower()
    return (
        lowered.startswith("http://localhost")
        or lowered.startswith("http://127.0.0.1")
        or lowered.startswith("http://[::1]")
    )


def _check_content(rel_path: str, content: str, report: ScanDepsReport) -> None:
    """Runs pattern checks for a single dependency file (R-012)."""
    # Slopsquat signature (case-insensitive) — hard error.
    lowered = content.lower()
    for sig in SLOPSQUAT_PATTERNS:
        if sig in lowered:
            report.errors.append(
                f"OWASP-AI-01 slopsquat signature '{sig}' detected in {rel_path}"
            )

    # Insecure http:// transport — hard error (non-local registries only).
    for match in _INSECURE_HTTP_RE.finditer(content):
        url = match.group(0)
        if not _is_local_http(url):
            report.errors.append(
                f"insecure http:// URL detected in {rel_path}: {url} (use https://)"
            )

    # Unpinned version checks (warnings only).
    if rel_path == "requirements.txt":
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            if (
                "=" in stripped
                or "<" in stripped
                or ">" in stripped
                or "!" in stripped
                or "~" in stripped
            ):
                if "==*" in stripped or ">=0.0.0" in stripped:
                    report.warnings.append(
                        f"unpinned Python dependency version spec in {rel_path}: {stripped}"
                    )
                continue
            match = _REQ_RE.match(stripped)
            if match:
                report.warnings.append(
                    f"unpinned Python dependency in {rel_path}: {match.group(1)}"
                )
    elif rel_path == "package.json":
        for m in re.finditer(r'"([^"]+)":\s*"([^"]+)"', content):
            name, version = m.group(1), m.group(2)
            if name in (
                "name",
                "version",
                "description",
                "author",
                "license",
                "main",
                "type",
            ):
                continue
            if (
                version.startswith("^")
                or version.startswith("~")
                or version.startswith(">=")
                or version == "*"
                or version == "latest"
            ):
                report.warnings.append(
                    f"unpinned Node dependency in {rel_path}: {name}@{version} (pin an exact version)"
                )


def run_scan_deps(project_root: str | None = None) -> ScanDepsReport:
    """
    Walks ``project_root`` (default cwd) for dependency files and flags
    slopsquat-looking names, insecure ``http://`` URLs and unpinned versions.

    Errors → exit 1; warnings alone → exit 0 (R-012 exit contract).
    """
    root = os.path.abspath(project_root or os.getcwd())
    report = ScanDepsReport()

    if not os.path.isdir(root):
        raise ValueError(
            f"What=invalid project root; Context='{root}' is not a directory; "
            "Fix=point scan-deps at an existing project directory"
        )

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name not in DEPENDENCY_FILENAMES:
                continue
            full = os.path.join(dirpath, name)
            rel_path = os.path.relpath(full, root)
            report.scanned_files.append(rel_path)
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            _check_content(rel_path, content, report)

    return report
