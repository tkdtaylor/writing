#!/usr/bin/env python3
"""package_skill.py - Clean skill payload verifier, packager, and installer.

Uses only the Python 3.10+ standard library (plus sibling validate_skill.py).
Collects the self-contained skill payload (SKILL.md, LICENSE, commands/write-*.md,
references/*.md, and scripts/{strip_markdown,prose_lint,validate_skill}.py),
stages and validates it in an isolated temporary directory, builds deterministic
writing-skill.tar.gz and writing.skill archives, or installs cleanly into a
target harness skill directory without maintainer scaffolding.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tarfile
import tempfile
from typing import Any
import zipfile

try:
    from scripts import validate_skill as _validate_skill
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    import validate_skill as _validate_skill  # type: ignore[no-redef]

ARCHIVE_ROOT_NAME = "writing"
TAR_GZ_FILENAME = "writing-skill.tar.gz"
SKILL_ZIP_FILENAME = "writing.skill"

# Fixed UTC timestamp (2026-01-01 00:00:00Z) for reproducible tar/zip archives.
_DETERMINISTIC_MTIME = 1767225600
_DETERMINISTIC_ZIP_DT = (2026, 1, 1, 0, 0, 0)

REQUIRED_ROOT_FILES = (
    "SKILL.md",
    "LICENSE",
)

REQUIRED_RUNTIME_SCRIPT_FILES = (
    "scripts/strip_markdown.py",
    "scripts/prose_lint.py",
    "scripts/validate_skill.py",
)

FORBIDDEN_TOP_LEVEL_ENTRIES = (
    ".agents",
    ".claude",
    ".git",
    ".gitignore",
    ".gitattributes",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GEMINI.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "artifacts",
    "dist",
    "docs",
    "evals",
    "samples",
    "tests",
    "training",
)

FORBIDDEN_PAYLOAD_FILES = (
    "scripts/check-mermaid.py",
    "scripts/sync-agy-skills.py",
    "scripts/package_skill.py",
)


def _is_executable_payload_file(rel_posix: str, src: Path) -> bool:
    """Return True when a payload file should receive 0o755 mode."""
    if rel_posix.startswith("scripts/") and rel_posix.endswith(".py"):
        return True
    return bool(src.stat().st_mode & stat.S_IXUSR)


def collect_payload_manifest(root: Path) -> tuple[list[str], list[str]]:
    """Collect canonical runtime payload relative POSIX paths from root.

    Returns (sorted_rel_paths, missing_or_invalid_errors).
    """
    errors: list[str] = []
    rel_paths: list[str] = []

    for rel in REQUIRED_ROOT_FILES:
        candidate = root / rel
        if not candidate.is_file() or candidate.is_symlink():
            errors.append(f"missing required payload file: {rel}")
        else:
            rel_paths.append(rel)

    commands_dir = root / "commands"
    if not commands_dir.is_dir():
        errors.append("missing required payload directory: commands/")
    else:
        cmd_files = sorted(
            p
            for p in commands_dir.glob("write-*.md")
            if p.is_file() and not p.is_symlink()
        )
        if not cmd_files:
            errors.append("missing required payload files: commands/write-*.md")
        for p in cmd_files:
            rel_paths.append(f"commands/{p.name}")

    refs_dir = root / "references"
    if not refs_dir.is_dir():
        errors.append("missing required payload directory: references/")
    else:
        ref_files = sorted(
            p for p in refs_dir.glob("*.md") if p.is_file() and not p.is_symlink()
        )
        if not ref_files:
            errors.append("missing required payload files: references/*.md")
        for p in ref_files:
            rel_paths.append(f"references/{p.name}")

    for rel in REQUIRED_RUNTIME_SCRIPT_FILES:
        candidate = root / rel
        if not candidate.is_file() or candidate.is_symlink():
            errors.append(f"missing required runtime script: {rel}")
        else:
            rel_paths.append(rel)

    return sorted(set(rel_paths)), errors


def _stage_payload(root: Path, payload_rel_paths: list[str], staged_dir: Path) -> None:
    """Copy payload_rel_paths from root into staged_dir cleanly."""
    staged_dir.mkdir(parents=True, exist_ok=True)
    for rel in payload_rel_paths:
        src = root / rel
        dst = staged_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        mode = 0o755 if _is_executable_payload_file(rel, src) else 0o644
        os.chmod(dst, mode)


def _check_staged_purity(
    staged_dir: Path, expected_rel_paths: list[str]
) -> tuple[int, bool, list[str]]:
    """Verify staged_dir holds exactly 1 SKILL.md and zero maintainer artifacts."""
    errors: list[str] = []
    skill_md_paths = sorted(
        p.relative_to(staged_dir).as_posix()
        for p in staged_dir.rglob("SKILL.md")
        if p.is_file()
    )
    if skill_md_paths != ["SKILL.md"]:
        errors.append(
            f"expected exactly 1 SKILL.md at staged root, found {skill_md_paths}"
        )

    excluded_absent = True
    for entry in FORBIDDEN_TOP_LEVEL_ENTRIES:
        if (staged_dir / entry).exists():
            excluded_absent = False
            errors.append(f"forbidden maintainer path present in staged tree: {entry}")

    for rel in FORBIDDEN_PAYLOAD_FILES:
        if (staged_dir / rel).exists():
            excluded_absent = False
            errors.append(f"forbidden maintainer script present in staged tree: {rel}")

    for p in sorted(staged_dir.rglob("*")):
        rel = p.relative_to(staged_dir).as_posix()
        if p.is_file() and rel.endswith(".sh"):
            excluded_absent = False
            errors.append(f"forbidden shell script present in staged tree: {rel}")

    staged_files = sorted(
        p.relative_to(staged_dir).as_posix()
        for p in staged_dir.rglob("*")
        if p.is_file()
    )
    if staged_files != sorted(expected_rel_paths):
        extra = sorted(set(staged_files) - set(expected_rel_paths))
        missing = sorted(set(expected_rel_paths) - set(staged_files))
        if extra:
            errors.append(f"unexpected files in staged tree: {', '.join(extra)}")
        if missing:
            errors.append(f"missing files in staged tree: {', '.join(missing)}")

    return len(skill_md_paths), excluded_absent, errors


def verify_payload(root: Path) -> dict[str, Any]:
    """Stage the clean skill payload in TemporaryDirectory and validate it."""
    payload_rel_paths, manifest_errors = collect_payload_manifest(root)
    errors = list(manifest_errors)

    with tempfile.TemporaryDirectory() as tmp:
        staged_dir = Path(tmp) / ARCHIVE_ROOT_NAME
        _stage_payload(root, payload_rel_paths, staged_dir)
        skill_md_count, excluded_absent, purity_errors = _check_staged_purity(
            staged_dir, payload_rel_paths
        )
        errors.extend(purity_errors)

        val_result = _validate_skill.validate_repo(staged_dir)
        if not val_result["passed"]:
            for err in val_result["errors"]:
                errors.append(f"validate_skill: {err}")

    return {
        "passed": len(errors) == 0,
        "root": str(root),
        "payload_files": payload_rel_paths,
        "skill_md_count": skill_md_count,
        "excluded_dirs_absent": excluded_absent,
        "validation": val_result,
        "archives": {},
        "installed_to": None,
        "errors": errors,
    }


def _collect_archive_dirs(payload_rel_paths: list[str]) -> list[str]:
    """Return sorted relative directory names needed inside tar archive."""
    dirs: set[str] = {ARCHIVE_ROOT_NAME}
    for rel in payload_rel_paths:
        parent = Path(rel).parent
        while parent != Path("."):
            dirs.add(f"{ARCHIVE_ROOT_NAME}/{parent.as_posix()}")
            parent = parent.parent
    return sorted(dirs)


def build_archives(
    root: Path, payload_rel_paths: list[str], output_dir: Path
) -> dict[str, str]:
    """Build deterministic writing-skill.tar.gz and writing.skill archives in output_dir."""
    if output_dir.exists() and not output_dir.is_dir():
        raise NotADirectoryError(f"output path is not a directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    tar_gz_path = output_dir / TAR_GZ_FILENAME
    skill_zip_path = output_dir / SKILL_ZIP_FILENAME

    # Write deterministic tar.gz (empty gzip filename, gzip mtime=0, fixed TarInfo metadata).
    with open(tar_gz_path, "wb") as raw_out:
        with gzip.GzipFile(
            filename="", fileobj=raw_out, mode="wb", mtime=0
        ) as gz_out:
            with tarfile.open(fileobj=gz_out, mode="w") as tf:
                for dir_name in _collect_archive_dirs(payload_rel_paths):
                    dinfo = tarfile.TarInfo(name=dir_name)
                    dinfo.type = tarfile.DIRTYPE
                    dinfo.mode = 0o755
                    dinfo.mtime = _DETERMINISTIC_MTIME
                    dinfo.uid = 0
                    dinfo.gid = 0
                    dinfo.uname = ""
                    dinfo.gname = ""
                    tf.addfile(dinfo)

                for rel in sorted(payload_rel_paths):
                    src = root / rel
                    data = src.read_bytes()
                    tinfo = tarfile.TarInfo(name=f"{ARCHIVE_ROOT_NAME}/{rel}")
                    tinfo.type = tarfile.REGTYPE
                    tinfo.size = len(data)
                    tinfo.mode = (
                        0o755 if _is_executable_payload_file(rel, src) else 0o644
                    )
                    tinfo.mtime = _DETERMINISTIC_MTIME
                    tinfo.uid = 0
                    tinfo.gid = 0
                    tinfo.uname = ""
                    tinfo.gname = ""
                    tf.addfile(tinfo, io.BytesIO(data))

    # Write deterministic .skill zip archive with POSIX file permissions preserved.
    with zipfile.ZipFile(
        skill_zip_path, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for rel in sorted(payload_rel_paths):
            src = root / rel
            data = src.read_bytes()
            mode = 0o755 if _is_executable_payload_file(rel, src) else 0o644
            zinfo = zipfile.ZipInfo(
                filename=f"{ARCHIVE_ROOT_NAME}/{rel}",
                date_time=_DETERMINISTIC_ZIP_DT,
            )
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.create_system = 3  # Unix permissions
            zinfo.external_attr = (stat.S_IFREG | mode) << 16
            zf.writestr(zinfo, data)

    return {
        "tar_gz": str(tar_gz_path),
        "skill_zip": str(skill_zip_path),
    }


def install_payload(
    root: Path,
    payload_rel_paths: list[str],
    target_dir: Path,
    clean: bool = False,
) -> Path:
    """Install only the clean runtime payload into target_dir."""
    if target_dir.exists() and not target_dir.is_dir():
        raise NotADirectoryError(f"install target is not a directory: {target_dir}")
    if target_dir.resolve() == root.resolve():
        raise OSError("install target must not be the source repository root")

    target_dir.mkdir(parents=True, exist_ok=True)
    expected_set = set(payload_rel_paths)

    if clean:
        for entry in list(target_dir.iterdir()):
            if entry.is_symlink():
                entry.unlink()
            elif entry.is_dir() and entry.name not in {"commands", "references", "scripts"}:
                shutil.rmtree(entry)

        for current_root, dirnames, filenames in os.walk(target_dir, topdown=False):
            cur_path = Path(current_root)
            for fname in filenames:
                fpath = cur_path / fname
                rel = fpath.relative_to(target_dir).as_posix()
                if rel not in expected_set:
                    fpath.unlink()
            for dname in dirnames:
                dpath = cur_path / dname
                if dpath.is_symlink():
                    dpath.unlink()
                elif dpath.is_dir() and not any(dpath.iterdir()):
                    dpath.rmdir()

    for rel in payload_rel_paths:
        src = root / rel
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        mode = 0o755 if _is_executable_payload_file(rel, src) else 0o644
        os.chmod(dst, mode)

    return target_dir


def _format_human_report(result: dict[str, Any]) -> str:
    """Format a concise human-readable packaging and verification report."""
    status = "PASS" if result["passed"] else "FAIL"
    lines = [
        f"Clean skill package check: {status} (root: {result['root']})",
        f"  Payload files: {len(result['payload_files'])} "
        f"(SKILL.md count={result['skill_md_count']}, "
        f"excluded_dirs_absent={result['excluded_dirs_absent']})",
    ]
    val = result.get("validation")
    if isinstance(val, dict):
        wc = val.get("word_counts", {})
        refs = wc.get("references", {})
        lines.append(
            f"  Skill validation: {'PASS' if val.get('passed') else 'FAIL'} "
            f"(SKILL.md={wc.get('SKILL.md', 0)}, references={len(refs)}, "
            f"combined={wc.get('combined_runtime', 0)})"
        )
    archives = result.get("archives") or {}
    if archives:
        lines.append(f"  Archives: {archives['tar_gz']}, {archives['skill_zip']}")
    if result.get("installed_to"):
        lines.append(f"  Installed to: {result['installed_to']}")
    if result.get("errors"):
        lines.append(f"Errors ({len(result['errors'])}):")
        for err in result["errors"]:
            lines.append(f"  - {err}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        prog="package_skill.py",
        description=(
            "Verify clean skill payload purity, build deterministic release "
            "archives (.tar.gz and .skill), or install cleanly to a target folder."
        ),
    )
    parser.add_argument(
        "--root",
        default=str(default_root),
        help="Repository root directory to package (defaults to repo root).",
    )
    parser.add_argument(
        "--output-dir",
        help="Write deterministic writing-skill.tar.gz and writing.skill into DIR.",
    )
    parser.add_argument(
        "--install-to",
        help="Install only the clean runtime skill payload into DIR.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="When used with --install-to, remove non-payload files inside DIR first.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Stage payload in a temporary directory and verify purity and validate_skill.py.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit packaging report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    root = Path(args.root)
    try:
        is_dir = root.is_dir()
    except OSError as exc:
        print(
            f"error: cannot access root directory {args.root}: {exc}",
            file=sys.stderr,
        )
        return 2
    if not is_dir:
        print(f"error: root directory not found: {args.root}", file=sys.stderr)
        return 2

    try:
        result = verify_payload(root)
    except OSError as exc:
        print(
            f"error: cannot read skill payload under {args.root}: {exc}",
            file=sys.stderr,
        )
        return 2

    if not result["passed"]:
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            print(_format_human_report(result))
        return 1

    if args.output_dir:
        try:
            result["archives"] = build_archives(
                root, result["payload_files"], Path(args.output_dir)
            )
        except OSError as exc:
            print(
                f"error: cannot write archives in {args.output_dir}: {exc}",
                file=sys.stderr,
            )
            return 2

    if args.install_to:
        try:
            installed_path = install_payload(
                root,
                result["payload_files"],
                Path(args.install_to),
                clean=args.clean,
            )
            result["installed_to"] = str(installed_path)
        except OSError as exc:
            print(
                f"error: cannot install skill payload to {args.install_to}: {exc}",
                file=sys.stderr,
            )
            return 2

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
