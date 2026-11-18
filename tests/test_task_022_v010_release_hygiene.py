"""Verification tests for Task 022: v0.1.0 Release Hygiene.

Covers TC-022-01 through TC-022-03 from
docs/tasks/test-specs/022-v010-release-prep-changelog-and-readme-test-spec.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
EM_DASH = "\u2014"
EN_DASH = "\u2013"

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _run_cmd(
    args: list[str], stdin_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def _strip_fenced_blocks(text: str) -> str:
    """Replace fenced code blocks with empty lines while preserving line numbering."""
    out: list[str] = []
    fence_marker: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        match = re.match(r"^(`{3,}|~{3,})", stripped)
        if match:
            token = match.group(1)
            if fence_marker is None:
                if not (token[0] == "`" and "`" in stripped[len(token) :]):
                    fence_marker = token
                    out.append("")
                    continue
            elif stripped.startswith(fence_marker[0] * len(fence_marker)) and re.match(
                rf"^{re.escape(fence_marker[0])}{{{len(fence_marker)},}}\s*$",
                stripped,
            ):
                fence_marker = None
                out.append("")
                continue
        if fence_marker is not None:
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


class TestTask022V010ReleaseHygiene(unittest.TestCase):
    """End-to-end verification for v0.1.0 release hygiene across docs."""

    def test_tc_022_01_changelog_cuts_v010_and_preserves_unreleased(self) -> None:
        """TC-022-01 (REQ-022-01): CHANGELOG.md cuts [0.1.0] - 2026-11-18 under [Unreleased] with reference links and zero tells."""
        changelog_path = ROOT / "CHANGELOG.md"
        self.assertTrue(changelog_path.is_file(), "Missing CHANGELOG.md")
        changelog_text = changelog_path.read_text(encoding="utf-8")

        self.assertIn("## [Unreleased]", changelog_text)
        self.assertIn("## [0.1.0] - 2026-11-18", changelog_text)
        self.assertIn("### Added", changelog_text)

        unreleased_pos = changelog_text.index("## [Unreleased]")
        v010_pos = changelog_text.index("## [0.1.0] - 2026-11-18")
        added_pos = changelog_text.index("### Added")
        self.assertLess(
            unreleased_pos,
            v010_pos,
            "CHANGELOG.md must keep ## [Unreleased] above ## [0.1.0] - 2026-11-18",
        )
        self.assertLess(
            v010_pos,
            added_pos,
            "CHANGELOG.md must place ### Added inside ## [0.1.0] - 2026-11-18",
        )

        v010_section = changelog_text[v010_pos:]
        self.assertIn("mixed_dialects", v010_section)
        self.assertIn("--profile technical", v010_section)

        unreleased_link = (
            "[Unreleased]: https://github.com/tkdtaylor/writing/compare/v0.1.0...HEAD"
        )
        v010_link = (
            "[0.1.0]: https://github.com/tkdtaylor/writing/releases/tag/v0.1.0"
        )
        self.assertIn(unreleased_link, changelog_text)
        self.assertIn(v010_link, changelog_text)
        self.assertLess(added_pos, changelog_text.index(unreleased_link))
        self.assertLess(added_pos, changelog_text.index(v010_link))

        rep = prose_lint.analyze_text(changelog_text, source="CHANGELOG.md")
        mech = rep["mechanics_and_tells"]
        tell_list_keys = [k for k, v in mech.items() if isinstance(v, list)]
        for tell_key in tell_list_keys:
            self.assertEqual(
                mech[tell_key],
                [],
                f"CHANGELOG.md triggered {tell_key}: {mech[tell_key]}",
            )
        self.assertEqual(
            rep["cadence"]["overloaded_sentences"],
            [],
            f"CHANGELOG.md has overloaded sentences (>35w): {rep['cadence']['overloaded_sentences']}",
        )

    def test_tc_022_02_readme_agents_and_roadmap_reflect_v010_release(self) -> None:
        """TC-022-02 (REQ-022-02): README.md, AGENTS.md, and roadmap.md reflect shipped v0.1.0, tag tarball, and mixed_dialects."""
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        roadmap_text = (ROOT / "docs" / "plans" / "roadmap.md").read_text(
            encoding="utf-8"
        )

        # Status callout reflects v0.1.0 live on main and drops future release-plan wording
        self.assertIn("Release v0.1.0 is live on main", readme_text)
        self.assertIn("docs/plans/roadmap.md", readme_text)
        self.assertIn("Milestone 2 corpus calibration", readme_text)
        self.assertNotIn("v0.1.0 release plans", readme_text)
        self.assertNotIn("`v0.1.0` release plans", readme_text)

        # Install instructions include pinned v0.1.0 tag tarball alongside main branch tarball
        self.assertIn(
            "https://github.com/tkdtaylor/writing/archive/refs/tags/v0.1.0.tar.gz",
            readme_text,
        )
        self.assertIn(
            "https://github.com/tkdtaylor/writing/archive/refs/heads/main.tar.gz",
            readme_text,
        )

        # Diagnostics summaries in README.md and AGENTS.md mention mixed_dialects
        self.assertIn("mixed_dialects", readme_text)
        self.assertIn("mixed_dialects", agents_text)

        # Roadmap marks Milestone 1 (Completed - v0.1.0) with Tasks 001..022 and Milestone 2 (Active)
        self.assertIn(
            "## Milestone 1: Version 1 Core Skill and Diagnostic Suite (Completed - v0.1.0)",
            roadmap_text,
        )
        for task_num in range(1, 23):
            heading = f"**Task {task_num:03d}:**"
            self.assertIn(heading, roadmap_text, f"roadmap.md missing {heading}")

        self.assertIn(
            "## Milestone 2: Corpus Calibration and Iterative Refinement (Active)",
            roadmap_text,
        )
        self.assertIn(
            "Cut v0.2.0 release after first corpus calibration sweep",
            roadmap_text,
        )
        self.assertNotIn("Tag `v0.1.0` public release", roadmap_text)
        self.assertNotIn("Tag v0.1.0 public release", roadmap_text)

    def test_tc_022_03_zero_prose_lint_tells_and_clean_package_validation(self) -> None:
        """TC-022-03 (REQ-022-03): Touched docs have zero U+2014/U+2013, zero prose_lint tells, zero overloaded sentences, and clean validation."""
        target_docs = (
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "CHANGELOG.md",
            ROOT / "docs" / "plans" / "roadmap.md",
        )
        for doc_path in target_docs:
            rel = doc_path.relative_to(ROOT).as_posix()
            raw = doc_path.read_text(encoding="utf-8")
            self.assertNotIn(EM_DASH, raw, f"{rel} contains literal em dash")
            self.assertNotIn(EN_DASH, raw, f"{rel} contains literal en dash")

            non_fenced = _strip_fenced_blocks(raw)
            lines = non_fenced.splitlines()
            for idx, line in enumerate(lines, start=1):
                if LIST_ITEM_RE.match(line) and idx > 1:
                    prev = lines[idx - 2]
                    self.assertTrue(
                        prev.strip() == "" or bool(LIST_ITEM_RE.match(prev)),
                        f"{rel}:{idx} starts list without preceding blank line",
                    )

            rep = prose_lint.analyze_text(raw, source=rel)
            mech = rep["mechanics_and_tells"]
            tell_list_keys = [k for k, v in mech.items() if isinstance(v, list)]
            self.assertGreaterEqual(len(tell_list_keys), 20)
            for tell_key in tell_list_keys:
                self.assertEqual(
                    mech[tell_key],
                    [],
                    f"{rel} triggered {tell_key}: {mech[tell_key]}",
                )
            self.assertEqual(
                rep["cadence"]["overloaded_sentences"],
                [],
                f"{rel} has overloaded sentences (>35w): {rep['cadence']['overloaded_sentences']}",
            )
            self.assertEqual(
                rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{rel} triggered importance_without_mechanism",
            )
            self.assertEqual(
                rep["substance_and_posture"]["hedge_booster_collisions"],
                [],
                f"{rel} triggered hedge_booster_collisions",
            )

        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])
        self.assertLessEqual(
            val_res["word_counts"]["combined_runtime"],
            10000,
            f"Combined runtime words {val_res['word_counts']['combined_runtime']} exceed 10,000 budget",
        )

        lint_proc = _run_cmd(["make", "lint"])
        self.assertEqual(lint_proc.returncode, 0, lint_proc.stdout + lint_proc.stderr)

        fitness_proc = _run_cmd(["make", "fitness"])
        self.assertEqual(
            fitness_proc.returncode, 0, fitness_proc.stdout + fitness_proc.stderr
        )
        for fid in ("F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"):
            self.assertIn(fid, fitness_proc.stdout)
        self.assertIn("All fitness checks passed.", fitness_proc.stdout)

        pkg_proc = _run_cmd(
            [sys.executable, "scripts/package_skill.py", "--check", "--json"]
        )
        self.assertEqual(pkg_proc.returncode, 0, pkg_proc.stdout + pkg_proc.stderr)
        pkg_report = json.loads(pkg_proc.stdout)
        self.assertTrue(pkg_report["passed"], pkg_report["errors"])
        self.assertEqual(pkg_report["errors"], [])

        # Self-hygiene check on this test file
        self_text = Path(__file__).resolve().read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, self_text)
        self.assertNotIn(EN_DASH, self_text)


if __name__ == "__main__":
    unittest.main()
