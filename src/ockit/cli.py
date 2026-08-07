"""
cli.py — Main CLI entrypoint for ockit command line tool

Argparse surface (R-028): ``init``, ``doctor``, ``verify`` (--suite),
``sync`` (--check | --sync), ``scan-deps``.
"""

from __future__ import annotations

import argparse
import os
import sys

from ockit.doctor import run_doctor
from ockit.installer import OckitInstaller
from ockit.scan_deps import run_scan_deps
from ockit.sync import run_sync
from ockit.validators import validate_target_arg
from ockit.verify import VERIFY_SUITES, run_verify


def _templates_dir() -> str:
    """Packaged templates resolve from the ockit package itself (R-004)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def _run_init(args) -> int:
    try:
        target = validate_target_arg(args.target)
    except ValueError as exc:
        print(f"❌ Invalid --target: {exc}", file=sys.stderr)
        return 1

    mode = (
        "🔍 DRY-RUN MODE ACTIVE: No files will be created or modified."
        if args.dry_run
        else "🚀"
    )
    print(f"{mode} Initializing ockit scaffold into target: {target}")

    installer = OckitInstaller(templates_dir=_templates_dir())
    try:
        res = installer.install(
            target=target, lang=args.lang, force=args.force, dry_run=args.dry_run
        )
    except ValueError as exc:
        # E-001 / E-032: missing packaged templates or bad state must exit 1
        # with an actionable message, never a raw traceback.
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    if res["status"] == "dry_run":
        print(
            f"Would copy {len(res['copied_files'])} files into {res['opencode_dir']} and root AGENTS.md"
        )
    else:
        print(
            f"✅ Scaffold initialized successfully. Copied {len(res['copied_files'])} files "
            f"into .opencode/ ({len(res['skipped_files'])} skipped, already present)."
        )
    return 0


def _run_doctor(project_root: str) -> int:
    print("==================================================")
    print("   ockit OpenCode-Native System Diagnostics       ")
    print("==================================================")
    res = run_doctor(project_root=project_root)
    print(f"Git Installed: {'✅ Yes' if res['git_installed'] else '❌ No'}")
    print(f"OpenCode CLI: {'✅ Yes' if res['opencode_installed'] else '⚠️ Not in PATH'}")
    print(f"Python Version: {res['python_version']}")
    print(f"AGENTS.md: {'✅ Present' if res['agents_md_present'] else '❌ Missing'}")
    print(
        f"Subagent Specs: {'✅ Valid' if res['agents_valid'] else '❌ Errors detected'}"
    )
    print(
        f"Agent Modes: {'✅ Valid' if res['agent_modes_valid'] else '❌ Errors detected'}"
    )
    print(
        f"Native Plugins: {'✅ Valid' if res['plugins_valid'] else '⚠️ Warnings detected'}"
    )

    if res["errors"]:
        print("\n❌ Errors:")
        for err in res["errors"]:
            print(f"  - {err}")
        return 1
    if res["warnings"]:
        print("\n⚠️ Warnings:")
        for warn in res["warnings"]:
            print(f"  - {warn}")
    print("\n✅ System Diagnostics Passed Successfully!")
    return 0


def _run_verify(args, project_root: str) -> int:
    report = run_verify(suite=args.suite, project_root=project_root)
    print("==================================================")
    print(f"   ockit Verify Audit — suite: {report.suite}")
    print("==================================================")
    for finding in report.findings:
        suffix = f" ({finding.path})" if finding.path else ""
        print(f"  [{finding.level}] {finding.message}{suffix}")
    print("==================================================")
    if report.error_count:
        print(
            f"❌ Verify failed: {report.error_count} error(s), "
            f"{report.warning_count} warning(s)."
        )
    else:
        print(f"✅ Verify passed ({report.warning_count} warning(s)).")
    return report.exit_code


def _run_sync(args, project_root: str) -> int:
    mode = "sync" if args.sync else "check"
    try:
        report = run_sync(active_dir=os.path.join(project_root, ".opencode"), mode=mode)
    except ValueError as exc:
        # E-032: missing packaged templates must exit 1 with an actionable
        # message, never a raw traceback.
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    print("==================================================")
    print(f"   ockit Template Synchronization Audit ({mode})")
    print("==================================================")
    for item in report.drift:
        print(f"  [DRIFT] {item.kind}: {item.relative_path}")
    for synced in report.synced:
        print(f"  ✅ Synced {synced} to active .opencode/")
    if mode == "check":
        if report.drift:
            print(
                f"❌ Template drift detected ({len(report.drift)} item(s)). "
                "Run 'ockit sync --sync' to copy packaged templates into active .opencode/."
            )
        else:
            print("✅ Active .opencode/ is 100% synchronized with packaged templates.")
    else:
        if report.synced:
            print(f"✅ Successfully synchronized {len(report.synced)} file(s).")
        else:
            print("✅ Templates were already synchronized. Zero drift.")
    return report.exit_code


def _run_scan_deps(project_root: str) -> int:
    report = run_scan_deps(project_root=project_root)
    print("==================================================")
    print("   ockit Supply Chain & Slopsquatting Scanner")
    print("==================================================")
    for err in report.errors:
        print(f"  [FAIL] {err}")
    for warn in report.warnings:
        print(f"  [WARN] {warn}")
    if not report.errors and not report.warnings:
        print(
            f"  [OK] Scanned {len(report.scanned_files)} dependency file(s); no issues found."
        )
    else:
        print(f"  Scanned {len(report.scanned_files)} dependency file(s).")
    print("==================================================")
    if report.errors:
        print(f"❌ Supply Chain Scan Failed ({len(report.errors)} error(s) detected).")
    else:
        print(
            f"✅ Supply Chain Scan Passed (Warnings: {len(report.warnings)}, Errors: 0)."
        )
    return report.exit_code


def main():
    parser = argparse.ArgumentParser(
        prog="ockit",
        description="OpenCode Kit (ockit) — OpenCode-Native Autonomous Agent Engineering Scaffold & Plugin Suite",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize ockit scaffold into a target directory"
    )
    init_parser.add_argument(
        "--target", default=".", help="Target directory (default: current dir)"
    )
    init_parser.add_argument(
        "--lang", default="python", help="Target programming language"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files (backs up originals)",
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be copied without writing anything",
    )

    # doctor command
    subparsers.add_parser("doctor", help="Run system health probe and diagnostics")

    # verify command
    verify_parser = subparsers.add_parser(
        "verify", help="Verify project requirement traceability and workflow sync"
    )
    verify_parser.add_argument(
        "--suite",
        choices=VERIFY_SUITES,
        default="all",
        help="Audit suite to run (default: all)",
    )

    # sync command (R-021: --check is the safe default)
    sync_parser = subparsers.add_parser(
        "sync", help="Synchronize active assets with templates"
    )
    sync_group = sync_parser.add_mutually_exclusive_group()
    sync_group.add_argument(
        "--check",
        action="store_true",
        help="Check for drift without writing (default)",
    )
    sync_group.add_argument(
        "--sync",
        action="store_true",
        help="Copy packaged templates into active .opencode/",
    )

    # scan-deps command
    subparsers.add_parser(
        "scan-deps", help="Scan project dependency files for supply chain patterns"
    )

    args = parser.parse_args()

    project_root = os.getcwd()

    if args.command == "init":
        sys.exit(_run_init(args))

    elif args.command == "doctor":
        sys.exit(_run_doctor(project_root))

    elif args.command == "verify":
        sys.exit(_run_verify(args, project_root))

    elif args.command == "sync":
        sys.exit(_run_sync(args, project_root))

    elif args.command == "scan-deps":
        sys.exit(_run_scan_deps(project_root))

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
