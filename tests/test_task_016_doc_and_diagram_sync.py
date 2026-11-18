"""Verification tests for Task 016: Architecture, Spec, and Documentation Drift Closure.

Covers TC-016-01 through TC-016-03 from
docs/tasks/test-specs/016-architecture-spec-and-doc-sync-test-spec.md.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
EM_DASH = "\u2014"

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
)

HYGIENE_TARGET_FILES = (
    "CONTRIBUTING.md",
    "docs/architecture/overview.md",
    "README.md",
    "CHANGELOG.md",
    "docs/spec/SPEC.md",
    "references/draft-and-brief.md",
)


def _run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


class TestTask016DocAndDiagramSync(unittest.TestCase):
    """Covers TC-016-01 through TC-016-03."""

    def test_tc_016_01_architecture_overview_diagrams_and_adr_links(self) -> None:
        """TC-016-01 (REQ-016-01): overview.md, diagrams.md, ADR links, and check-mermaid.py sync cleanly."""
        overview_path = ROOT / "docs" / "architecture" / "overview.md"
        diagrams_path = ROOT / "docs" / "architecture" / "diagrams.md"
        self.assertTrue(overview_path.is_file(), f"Missing {overview_path}")
        self.assertTrue(diagrams_path.is_file(), f"Missing {diagrams_path}")

        overview_text = overview_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, overview_text)
        self.assertNotIn(
            "git clone",
            overview_text,
            "docs/architecture/overview.md must not recommend raw git clone for skill install",
        )
        self.assertIn("package_skill.py", overview_text)
        self.assertIn("--install-to", overview_text)
        self.assertGreaterEqual(
            overview_text.count("one-pager-and-six-pager.md"),
            2,
            "overview.md must cite one-pager-and-six-pager.md in Principle 2 and Genre references",
        )
        self.assertIn("10,000", overview_text)
        self.assertIn("F-007", overview_text)
        self.assertIn("## Architecture decisions", overview_text)

        for adr_rel in (
            "decisions/001-register-and-genre-routing.md",
            "decisions/002-narrative-memos-and-anti-flourish-rules.md",
        ):
            self.assertIn(adr_rel, overview_text, f"overview.md missing ADR link: {adr_rel}")
            self.assertTrue(
                (overview_path.parent / adr_rel).is_file(),
                f"Linked ADR file missing on disk: {adr_rel}",
            )

        diagrams_text = diagrams_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, diagrams_text)
        self.assertIn("Last updated: 2026-11-18", diagrams_text)
        self.assertIn("references/one-pager-and-six-pager.md", diagrams_text)
        self.assertIn("GenreRouter --> Memo", diagrams_text)
        self.assertIn("validate_skill", diagrams_text)
        self.assertIn("package_skill", diagrams_text)

        mermaid_proc = _run_cmd([sys.executable, "scripts/check-mermaid.py"])
        self.assertEqual(
            mermaid_proc.returncode,
            0,
            f"check-mermaid.py failed:\n{mermaid_proc.stdout}\n{mermaid_proc.stderr}",
        )

    def test_tc_016_02_spec_readme_changelog_and_draft_reference_alignment(self) -> None:
        """TC-016-02 (REQ-016-02): SPEC.md, CHANGELOG.md, README.md, and draft-and-brief.md align with repo specs."""
        spec_text = (ROOT / "docs" / "spec" / "SPEC.md").read_text(encoding="utf-8")
        changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        draft_ref_text = (ROOT / "references" / "draft-and-brief.md").read_text(encoding="utf-8")

        self.assertIn("F-007", spec_text)
        self.assertNotIn("`F-001`..`F-006`", spec_text)

        self.assertIn("F-007", changelog_text)
        self.assertNotIn("Six active fitness gates", changelog_text)
        self.assertIn("Seven active fitness gates", changelog_text)

        readme_lower = readme_text.lower()
        for token in ("`measured`", "`inferred`", "`open`"):
            self.assertIn(token, readme_text, f"README.md missing epistemic tag {token}")
        for metric_term in ("unit", "sample or runs", "baseline", "limiter"):
            self.assertIn(
                metric_term,
                readme_lower,
                f"README.md missing 4-part metric vetting anchor '{metric_term}'",
            )
        self.assertIn("archive/refs/heads/main.tar.gz", readme_text)
        self.assertRegex(
            readme_text,
            r"#\s+SPEC\.md,\s*behaviors,\s*architecture,\s*data-model,\s*interfaces,\s*configuration,\s*fitness",
            "README.md docs/spec/ tree comment must include configuration",
        )

        self.assertIn("references/one-pager-and-six-pager.md", draft_ref_text)
        self.assertIn("prettier", draft_ref_text)
        self.assertIn("mdformat", draft_ref_text)
        self.assertIn("precedence", draft_ref_text.lower())

        draft_words = len(draft_ref_text.split())
        self.assertLessEqual(
            draft_words,
            1500,
            f"references/draft-and-brief.md exceeds 1,500-word cap: {draft_words}",
        )

        val_report = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_report["passed"], f"validate_skill failed: {val_report['errors']}")
        self.assertEqual(val_report["errors"], [])
        self.assertLessEqual(val_report["word_counts"]["combined_runtime"], 10000)

    def test_tc_016_03_prose_hygiene_and_zero_em_dashes(self) -> None:
        """TC-016-03 (REQ-016-03): target docs pass prose_lint with zero tells/overloaded sentences and Task 013 has zero em dashes."""
        for rel_path in HYGIENE_TARGET_FILES:
            path = ROOT / rel_path
            self.assertTrue(path.is_file(), f"Missing {rel_path}")
            raw_text = path.read_text(encoding="utf-8")
            self.assertNotIn(EM_DASH, raw_text, f"{rel_path} contains literal em dash")

            rep = prose_lint.analyze_text(raw_text, source=rel_path)
            mech = rep["mechanics_and_tells"]
            for tell_key in ALL_TELL_LIST_KEYS:
                self.assertEqual(
                    mech[tell_key],
                    [],
                    f"{rel_path} triggered {tell_key}: {mech[tell_key]}",
                )
            self.assertEqual(
                rep["cadence"]["overloaded_sentences"],
                [],
                f"{rel_path} has overloaded sentences: {rep['cadence']['overloaded_sentences']}",
            )
            self.assertEqual(
                rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{rel_path} has importance_without_mechanism: {rep['substance_and_posture']['importance_without_mechanism']}",
            )

        task_013_path = (
            ROOT / "docs" / "tasks" / "completed" / "013-prose-lint-gaps-and-genre-profiles.md"
        )
        self.assertTrue(task_013_path.is_file(), f"Missing {task_013_path}")
        self.assertNotIn(
            EM_DASH,
            task_013_path.read_text(encoding="utf-8"),
            "Completed Task 013 file must contain zero literal em dashes",
        )

        self.assertNotIn(
            EM_DASH,
            Path(__file__).resolve().read_text(encoding="utf-8"),
            "Test file itself must contain zero literal em dashes",
        )


if __name__ == "__main__":
    unittest.main()
