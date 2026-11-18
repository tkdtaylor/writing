"""Unit and CLI tests for Task 011: OSError/PermissionError handling and restricted-FS tests.

Covers TC-011-01 through TC-011-03 from
docs/tasks/test-specs/011-fix-cli-oserror-and-restricted-fs-tests-test-spec.md.
"""
from __future__ import annotations

from contextlib import redirect_stderr
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import strip_markdown, validate_skill

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_CLI = ROOT / "scripts" / "validate_skill.py"
STRIP_CLI = ROOT / "scripts" / "strip_markdown.py"
TASK_006_TEST = ROOT / "tests" / "test_task_006_validate_skill.py"


class TestTask011CliOsError(unittest.TestCase):
    """Verification suite for REQ-011-01..REQ-011-03 (TC-011-01..TC-011-03)."""

    def test_tc_011_01_validate_skill_oserror_and_missing_root(self) -> None:
        """TC-011-01 (REQ-011-01): validate_skill.main handles PermissionError and missing root cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "restricted-root"
            stderr_buf = io.StringIO()
            with (
                patch.object(
                    Path,
                    "is_dir",
                    side_effect=PermissionError(13, "Permission denied"),
                ),
                redirect_stderr(stderr_buf),
            ):
                rc = validate_skill.main(["--root", str(candidate)])

            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr_buf.getvalue())
            self.assertIn("Permission denied", stderr_buf.getvalue())

            missing_root = Path(tmp) / "nonexistent" / "skill" / "root"
            proc = subprocess.run(
                [sys.executable, str(VALIDATOR_CLI), "--root", str(missing_root)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error:", proc.stderr)

    def test_tc_011_02_strip_markdown_oserror_and_missing_file(self) -> None:
        """TC-011-02 (REQ-011-02): strip_markdown.main handles PermissionError and missing file cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "restricted.md"
            stderr_buf = io.StringIO()
            with (
                patch.object(
                    Path,
                    "is_file",
                    side_effect=PermissionError(13, "Permission denied"),
                ),
                redirect_stderr(stderr_buf),
            ):
                rc = strip_markdown.main([str(candidate)])

            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr_buf.getvalue())
            self.assertIn("Permission denied", stderr_buf.getvalue())

            candidate.write_text("# Sample\n", encoding="utf-8")
            read_err_buf = io.StringIO()
            with (
                patch.object(
                    Path,
                    "read_text",
                    side_effect=OSError(13, "Input/output error"),
                ),
                redirect_stderr(read_err_buf),
            ):
                rc_read = strip_markdown.main([str(candidate)])

            self.assertEqual(rc_read, 2)
            self.assertIn("error:", read_err_buf.getvalue())

            missing_file = Path(tmp) / "nonexistent" / "input.md"
            proc = subprocess.run(
                [sys.executable, str(STRIP_CLI), str(missing_file)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error:", proc.stderr)

    def test_tc_011_03_task_006_uses_tempdir_and_passes(self) -> None:
        """TC-011-03 (REQ-011-03): test_task_006_validate_skill.py has no hardcoded /nonexistent/ paths and passes."""
        source = TASK_006_TEST.read_text(encoding="utf-8")
        self.assertNotIn('"/nonexistent/', source)
        self.assertNotIn("'/nonexistent/", source)
        self.assertIn("TemporaryDirectory", source)

        suite = unittest.defaultTestLoader.loadTestsFromName(
            "tests.test_task_006_validate_skill"
        )
        runner_out = io.StringIO()
        result = unittest.TextTestRunner(stream=runner_out, verbosity=1).run(suite)
        self.assertTrue(
            result.wasSuccessful(),
            f"tests.test_task_006_validate_skill failed:\n{runner_out.getvalue()}",
        )


if __name__ == "__main__":
    unittest.main()
