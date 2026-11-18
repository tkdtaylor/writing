"""Unit and integration tests for Task 014: Clean Skill Packaging and End-User Install Hygiene.

Covers TC-014-01 through TC-014-03 from
docs/tasks/test-specs/014-clean-skill-packaging-and-install-hygiene-test-spec.md.
"""
from __future__ import annotations

import ast
from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import package_skill, prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_CLI = ROOT / "scripts" / "package_skill.py"
EM_DASH = "\u2014"

EXPECTED_RUNTIME_PAYLOAD = {
    "LICENSE",
    "SKILL.md",
    "commands/write-draft.md",
    "commands/write-edit.md",
    "commands/write-lint.md",
    "commands/write-review.md",
    "references/business-and-executive.md",
    "references/draft-and-brief.md",
    "references/edit-and-anti-slop.md",
    "references/longform-and-persuasion.md",
    "references/one-pager-and-six-pager.md",
    "references/review-rubric.md",
    "references/technical-and-docs.md",
    "scripts/prose_lint.py",
    "scripts/strip_markdown.py",
    "scripts/validate_skill.py",
}

FORBIDDEN_ARCHIVE_PREFIXES = (
    ".agents/",
    ".claude/",
    "docs/",
    "tests/",
    "evals/",
    "samples/",
    "artifacts/",
    "dist/",
    "training/",
)

FORBIDDEN_ARCHIVE_EXACT = {
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GEMINI.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "scripts/check-mermaid.py",
    "scripts/check-task-state.sh",
    "scripts/finish-task.sh",
    "scripts/package_skill.py",
    "scripts/start-task.sh",
    "scripts/sync-agy-skills.py",
    "scripts/verify-worktree-isolation.sh",
}

ALL_TELL_LIST_KEYS = (
    "em_dashes",
    "connector_colons",
    "bold_restatement_bullets",
    "emoji_bullets",
    "hard_wrapped_lines",
    "false_scales",
    "ai_tell_words",
    "inflated_style_verbs",
    "tech_buzz_nouns",
    "framing_theater",
    "contrastive_pivots",
    "participial_tail_puffery",
    "copula_avoidance",
    "rhetorical_qa_pivots",
    "performative_fragments",
    "stacked_questions",
    "shorthand_ambiguities",
    "exclamation_marks",
    "false_agency",
    "chatbot_artifacts",
    "meta_and_strawman_tells",
    "mixed_dialects",
)


def _run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestTask014CleanPackaging(unittest.TestCase):
    """Verification suite for REQ-014-01..REQ-014-03 (TC-014-01..TC-014-03)."""

    def test_tc_014_01_gitattributes_and_git_archive_purity(self) -> None:
        """TC-014-01 (REQ-014-01): .gitattributes export-ignore limits git archive to clean skill payload."""
        gitattributes_path = ROOT / ".gitattributes"
        self.assertTrue(gitattributes_path.is_file(), "Missing .gitattributes")
        attrs_text = gitattributes_path.read_text(encoding="utf-8")

        for pattern in (
            ".agents",
            ".claude",
            "docs",
            "tests",
            "evals",
            "samples",
            "artifacts",
            "Makefile",
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "CHANGELOG.md",
            ".gitignore",
            ".gitattributes",
            "scripts/*.sh",
            "scripts/check-mermaid.py",
            "scripts/sync-agy-skills.py",
            "scripts/package_skill.py",
        ):
            self.assertIn(pattern, attrs_text, f".gitattributes missing {pattern}")
            self.assertRegex(
                attrs_text,
                rf"(?m)^/?{re.escape(pattern)}\s+export-ignore\s*$",
                f".gitattributes must mark {pattern} as export-ignore",
            )

        proc = subprocess.run(
            ["git", "archive", "--worktree-attributes", "--format=tar", "HEAD"],
            capture_output=True,
            cwd=str(ROOT),
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"git archive failed: {proc.stderr.decode('utf-8', errors='replace')}",
        )

        with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as tf:
            non_dir_members = sorted(
                m.name.lstrip("./") for m in tf.getmembers() if not m.isdir()
            )
            with tempfile.TemporaryDirectory() as tmp:
                extracted_dir = Path(tmp) / "extracted"
                extracted_dir.mkdir()
                if hasattr(tarfile, "data_filter"):
                    tf.extractall(path=extracted_dir, filter="data")
                else:
                    tf.extractall(path=extracted_dir)

                self.assertEqual(set(non_dir_members), EXPECTED_RUNTIME_PAYLOAD)
                skill_mds = [
                    m for m in non_dir_members if Path(m).name == "SKILL.md"
                ]
                self.assertEqual(skill_mds, ["SKILL.md"])

                for member_name in non_dir_members:
                    self.assertNotIn(member_name, FORBIDDEN_ARCHIVE_EXACT)
                    for prefix in FORBIDDEN_ARCHIVE_PREFIXES:
                        self.assertFalse(
                            member_name.startswith(prefix),
                            f"Archive leaked maintainer path: {member_name}",
                        )
                    self.assertFalse(member_name.endswith(".sh"))

                val_report = validate_skill.validate_repo(extracted_dir)
                self.assertTrue(
                    val_report["passed"],
                    f"Extracted git archive failed validate_skill: {val_report['errors']}",
                )

    def test_tc_014_02_package_skill_cli_archives_install_and_oserror(self) -> None:
        """TC-014-02 (REQ-014-02): scripts/package_skill.py builds deterministic archives, installs cleanly, passes --check, and handles OSError."""
        self.assertTrue(PACKAGE_CLI.is_file(), "Missing scripts/package_skill.py")
        mode = PACKAGE_CLI.stat().st_mode
        self.assertTrue(bool(mode & stat.S_IXUSR), "scripts/package_skill.py must be executable")
        self.assertTrue(os.access(PACKAGE_CLI, os.X_OK), "scripts/package_skill.py must be executable via os.access")

        source = PACKAGE_CLI.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, source, "package_skill.py must not contain literal em dashes")

        # Verify Python 3 stdlib only (plus sibling validate_skill)
        tree = ast.parse(source)
        allowed_non_stdlib = {"scripts", "validate_skill"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_mod = alias.name.split(".")[0]
                    self.assertIn(
                        top_mod,
                        sys.stdlib_module_names | allowed_non_stdlib,
                        f"Non-stdlib import found: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                top_mod = node.module.split(".")[0]
                self.assertIn(
                    top_mod,
                    sys.stdlib_module_names | allowed_non_stdlib,
                    f"Non-stdlib import found: {node.module}",
                )

        # --check --json
        chk_proc = _run_cmd([sys.executable, str(PACKAGE_CLI), "--check", "--json"])
        self.assertEqual(chk_proc.returncode, 0, chk_proc.stdout + chk_proc.stderr)
        chk_payload = json.loads(chk_proc.stdout)
        self.assertTrue(chk_payload["passed"], chk_payload["errors"])
        self.assertEqual(chk_payload["skill_md_count"], 1)
        self.assertTrue(chk_payload["excluded_dirs_absent"])
        self.assertEqual(set(chk_payload["payload_files"]), EXPECTED_RUNTIME_PAYLOAD)
        self.assertEqual(chk_payload["errors"], [])

        # --output-dir produces deterministic writing-skill.tar.gz and writing.skill
        with (
            tempfile.TemporaryDirectory() as tmp1,
            tempfile.TemporaryDirectory() as tmp2,
        ):
            out1 = Path(tmp1) / "dist"
            out2 = Path(tmp2) / "dist"
            p1 = _run_cmd([sys.executable, str(PACKAGE_CLI), "--output-dir", str(out1), "--json"])
            p2 = _run_cmd([sys.executable, str(PACKAGE_CLI), "--output-dir", str(out2), "--json"])
            self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)

            tar1 = out1 / "writing-skill.tar.gz"
            zip1 = out1 / "writing.skill"
            tar2 = out2 / "writing-skill.tar.gz"
            zip2 = out2 / "writing.skill"
            for archive in (tar1, zip1, tar2, zip2):
                self.assertTrue(archive.is_file(), f"Missing archive: {archive}")

            self.assertEqual(_sha256(tar1), _sha256(tar2), "tar.gz output must be deterministic")
            self.assertEqual(_sha256(zip1), _sha256(zip2), ".skill output must be deterministic")

            expected_prefixed = {f"writing/{p}" for p in EXPECTED_RUNTIME_PAYLOAD}
            with tarfile.open(tar1, "r:gz") as tf:
                tar_files = {m.name for m in tf.getmembers() if m.isfile()}
                self.assertEqual(tar_files, expected_prefixed)
                tar_skill_mds = [n for n in tar_files if n.endswith("/SKILL.md")]
                self.assertEqual(tar_skill_mds, ["writing/SKILL.md"])

            with zipfile.ZipFile(zip1, "r") as zf:
                zip_files = {n for n in zf.namelist() if not n.endswith("/")}
                self.assertEqual(zip_files, expected_prefixed)
                zip_extract = Path(tmp1) / "zip-extracted"
                zf.extractall(zip_extract)
                zip_val = validate_skill.validate_repo(zip_extract / "writing")
                self.assertTrue(zip_val["passed"], zip_val["errors"])

        # --install-to installs clean payload passing validate_skill.py --root
        with tempfile.TemporaryDirectory() as tmp_install:
            clean_target = Path(tmp_install) / "clean-writing"
            inst_proc = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--install-to", str(clean_target)]
            )
            self.assertEqual(inst_proc.returncode, 0, inst_proc.stdout + inst_proc.stderr)

            installed_files = {
                p.relative_to(clean_target).as_posix()
                for p in clean_target.rglob("*")
                if p.is_file()
            }
            self.assertEqual(installed_files, EXPECTED_RUNTIME_PAYLOAD)
            for forbidden in (".agents", ".claude", "docs", "tests", "evals", "samples"):
                self.assertFalse((clean_target / forbidden).exists())

            val_installed = _run_cmd(
                [
                    sys.executable,
                    str(clean_target / "scripts" / "validate_skill.py"),
                    "--root",
                    str(clean_target),
                ]
            )
            self.assertEqual(
                val_installed.returncode,
                0,
                val_installed.stdout + val_installed.stderr,
            )

            # Verify --clean removes stale maintainer folders from an existing directory
            stale_target = Path(tmp_install) / "dirty-writing"
            (stale_target / ".agents" / "skills" / "task-executor").mkdir(parents=True)
            (stale_target / ".agents" / "skills" / "task-executor" / "SKILL.md").write_text(
                "stale", encoding="utf-8"
            )
            (stale_target / "README.md").write_text("stale readme", encoding="utf-8")

            clean_proc = _run_cmd(
                [
                    sys.executable,
                    str(PACKAGE_CLI),
                    "--install-to",
                    str(stale_target),
                    "--clean",
                ]
            )
            self.assertEqual(clean_proc.returncode, 0, clean_proc.stdout + clean_proc.stderr)
            stale_files = {
                p.relative_to(stale_target).as_posix()
                for p in stale_target.rglob("*")
                if p.is_file()
            }
            self.assertEqual(stale_files, EXPECTED_RUNTIME_PAYLOAD)
            self.assertFalse((stale_target / ".agents").exists())
            self.assertFalse((stale_target / "README.md").exists())

        # OSError, missing path, and invalid payload error handling
        with tempfile.TemporaryDirectory() as tmp_err:
            tmp_path = Path(tmp_err)
            missing_root = tmp_path / "missing-repo"
            miss_proc = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--root", str(missing_root), "--check"]
            )
            self.assertEqual(miss_proc.returncode, 2)
            self.assertIn("error:", miss_proc.stderr)

            stderr_buf = io.StringIO()
            with (
                patch.object(
                    Path,
                    "is_dir",
                    side_effect=PermissionError(13, "Permission denied"),
                ),
                redirect_stderr(stderr_buf),
            ):
                rc_perm = package_skill.main(["--root", str(tmp_path / "restricted"), "--check"])
            self.assertEqual(rc_perm, 2)
            self.assertIn("error:", stderr_buf.getvalue())

            not_a_dir = tmp_path / "regular-file.txt"
            not_a_dir.write_text("file", encoding="utf-8")
            out_file_proc = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--output-dir", str(not_a_dir)]
            )
            self.assertEqual(out_file_proc.returncode, 2)
            self.assertIn("error:", out_file_proc.stderr)

            inst_file_proc = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--install-to", str(not_a_dir)]
            )
            self.assertEqual(inst_file_proc.returncode, 2)
            self.assertIn("error:", inst_file_proc.stderr)

            self_inst_proc = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--install-to", str(ROOT)]
            )
            self.assertEqual(self_inst_proc.returncode, 2)
            self.assertIn("error:", self_inst_proc.stderr)

            empty_root = tmp_path / "empty-skill"
            empty_root.mkdir()
            empty_chk = _run_cmd(
                [sys.executable, str(PACKAGE_CLI), "--root", str(empty_root), "--check"]
            )
            self.assertEqual(empty_chk.returncode, 1)

    def test_tc_014_03_makefile_specs_docs_and_fitness(self) -> None:
        """TC-014-03 (REQ-014-03): Makefile, specs, docs, and make fitness integrate F-007 and clean install docs."""
        gitignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertRegex(gitignore_text, r"(?m)^dist/\s*$")

        makefile_text = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertRegex(makefile_text, r"(?m)^package:\s*$")
        self.assertRegex(makefile_text, r"(?m)^fitness-clean-package:\s*$")
        self.assertIn("scripts/package_skill.py --output-dir dist", makefile_text)
        self.assertIn("scripts/package_skill.py --check", makefile_text)
        fitness_line = re.search(r"(?m)^fitness:\s*(.+)$", makefile_text)
        self.assertIsNotNone(fitness_line)
        self.assertIn("fitness-clean-package", fitness_line.group(1).split())

        fitness_spec = (ROOT / "docs" / "spec" / "fitness-functions.md").read_text(encoding="utf-8")
        self.assertIn("`F-007`", fitness_spec)
        self.assertIn("make fitness-clean-package", fitness_spec)
        self.assertIn("Active", fitness_spec)

        arch_spec = (ROOT / "docs" / "spec" / "architecture.md").read_text(encoding="utf-8")
        self.assertIn("scripts/package_skill.py", arch_spec)
        self.assertIn(".gitattributes", arch_spec)

        iface_spec = (ROOT / "docs" / "spec" / "interfaces.md").read_text(encoding="utf-8")
        for flag in ("scripts/package_skill.py", "--output-dir", "--install-to", "--clean", "--check", "--json"):
            self.assertIn(flag, iface_spec)

        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        for token in (
            "archive/refs/heads/main.tar.gz",
            "--strip-components=1",
            "scripts/package_skill.py --install-to",
            "~/.gemini/config/skills/",
            ".agents/skills/",
            "~/.codex/skills/",
            ".github/skills/",
            "--profile",
            "--mode",
            "one-pager",
            "six-pager",
            "technical",
            "narrative",
            ".gitattributes",
            "F-007",
        ):
            self.assertIn(token, readme_text, f"README.md missing {token}")

        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        roadmap_text = (ROOT / "docs" / "plans" / "roadmap.md").read_text(encoding="utf-8")
        for doc_name, doc_text in (
            ("AGENTS.md", agents_text),
            ("CHANGELOG.md", changelog_text),
            ("docs/plans/roadmap.md", roadmap_text),
        ):
            self.assertIn("package_skill.py", doc_text, f"{doc_name} missing package_skill.py")
            self.assertIn("F-007", doc_text, f"{doc_name} missing F-007")
            self.assertIn("--profile", doc_text, f"{doc_name} missing --profile")
            self.assertIn("--mode", doc_text, f"{doc_name} missing --mode")

        # Prose hygiene & prose_lint check on all touched Markdown files and this test file
        touched_md = (
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "CHANGELOG.md",
            ROOT / "docs" / "plans" / "roadmap.md",
            ROOT / "docs" / "spec" / "architecture.md",
            ROOT / "docs" / "spec" / "fitness-functions.md",
            ROOT / "docs" / "spec" / "interfaces.md",
        )
        for md_path in touched_md:
            text = md_path.read_text(encoding="utf-8")
            self.assertNotIn(EM_DASH, text, f"Literal em dash in {md_path.relative_to(ROOT)}")
            rep = prose_lint.analyze_text(text, source=md_path.relative_to(ROOT).as_posix())
            for tell_key in ALL_TELL_LIST_KEYS:
                self.assertEqual(
                    rep["mechanics_and_tells"][tell_key],
                    [],
                    f"{md_path.name} triggered {tell_key}: {rep['mechanics_and_tells'][tell_key]}",
                )
            self.assertEqual(rep["substance_and_posture"]["importance_without_mechanism"], [])
            self.assertEqual(rep["cadence"]["overloaded_sentences"], [])

        self.assertNotIn(EM_DASH, Path(__file__).resolve().read_text(encoding="utf-8"))

        # Run make fitness end-to-end
        fitness_proc = _run_cmd(["make", "fitness"])
        self.assertEqual(
            fitness_proc.returncode,
            0,
            f"make fitness failed:\n{fitness_proc.stdout}\n{fitness_proc.stderr}",
        )
        self.assertIn("F-007", fitness_proc.stdout)
        self.assertIn("All fitness checks passed.", fitness_proc.stdout)


if __name__ == "__main__":
    unittest.main()
