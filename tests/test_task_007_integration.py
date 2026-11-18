"""End-to-end integration and release-readiness tests for Task 007.

Covers TC-007-01 through TC-007-03 from
docs/tasks/test-specs/007-fitness-gates-and-release-docs-test-spec.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import validate_skill

ROOT = Path(__file__).resolve().parent.parent
EM_DASH = "\u2014"

EXPECTED_FITNESS_TARGETS = {
    "F-001": "fitness-task-state",
    "F-002": "fitness-mermaid",
    "F-003": "fitness-agy-sync",
    "F-004": "fitness-skill-package",
    "F-005": "fitness-prose-hygiene",
    "F-006": "fitness-samples",
    "F-007": "fitness-clean-package",
}


def _run_cmd(args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


class TestTask007Integration(unittest.TestCase):
    """End-to-end verification for fitness gates, README.md, CHANGELOG.md, and CLI pipeline."""

    def test_tc_007_01_fitness_gates_and_makefile(self) -> None:
        """TC-007-01: REQ-007-01 F-001..F-007 are Active in fitness-functions.md and wired in Makefile."""
        spec_path = ROOT / "docs" / "spec" / "fitness-functions.md"
        makefile_path = ROOT / "Makefile"
        self.assertTrue(spec_path.is_file(), f"Missing {spec_path}")
        self.assertTrue(makefile_path.is_file(), f"Missing {makefile_path}")

        spec_text = spec_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, spec_text, "fitness-functions.md must not contain literal em dashes")
        self.assertNotIn("Planned", spec_text, "No fitness function should remain Planned")

        rows_by_id: dict[str, tuple[str, str, str]] = {}
        for line in spec_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or stripped.startswith("|----"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) == 4 and cells[0].startswith("`F-"):
                fid = cells[0].strip("`")
                rows_by_id[fid] = (cells[1], cells[2], cells[3])

        self.assertEqual(
            set(rows_by_id.keys()),
            set(EXPECTED_FITNESS_TARGETS.keys()),
            f"Expected F-001..F-007 rows, found {sorted(rows_by_id.keys())}",
        )
        for fid, target_name in EXPECTED_FITNESS_TARGETS.items():
            _, target_col, status_col = rows_by_id[fid]
            self.assertEqual(status_col, "Active", f"{fid} must have Status 'Active'")
            self.assertIn(
                f"make {target_name}",
                target_col,
                f"{fid} row must reference 'make {target_name}'",
            )

        makefile_text = makefile_path.read_text(encoding="utf-8")
        phony_match = re.search(r"^\.PHONY:\s*(.+)$", makefile_text, flags=re.MULTILINE)
        self.assertIsNotNone(phony_match, "Makefile must define .PHONY")
        phony_targets = set(phony_match.group(1).split()) if phony_match else set()

        fitness_match = re.search(r"^fitness:\s*(.+)$", makefile_text, flags=re.MULTILINE)
        self.assertIsNotNone(fitness_match, "Makefile must define 'fitness:' prerequisites")
        fitness_prereqs = fitness_match.group(1).split() if fitness_match else []

        for fid, target_name in EXPECTED_FITNESS_TARGETS.items():
            self.assertIn(target_name, phony_targets, f"{target_name} missing from .PHONY")
            self.assertIn(
                target_name,
                fitness_prereqs,
                f"{target_name} ({fid}) missing from 'fitness:' prerequisites",
            )
            self.assertRegex(
                makefile_text,
                rf"(?m)^{re.escape(target_name)}:\s*$",
                f"Makefile missing target rule '{target_name}:'",
            )

        check_match = re.search(r"^check:\s*(.+)$", makefile_text, flags=re.MULTILINE)
        self.assertIsNotNone(check_match, "Makefile must define 'check:' target")
        check_prereqs = check_match.group(1).split() if check_match else []
        self.assertEqual(check_prereqs, ["lint", "test", "fitness"])

        # Run make lint and make fitness directly (avoiding recursive make test / make check).
        lint_proc = _run_cmd(["make", "lint"])
        self.assertEqual(
            lint_proc.returncode,
            0,
            f"make lint failed:\nSTDOUT:\n{lint_proc.stdout}\nSTDERR:\n{lint_proc.stderr}",
        )

        fitness_proc = _run_cmd(["make", "fitness"])
        self.assertEqual(
            fitness_proc.returncode,
            0,
            f"make fitness failed:\nSTDOUT:\n{fitness_proc.stdout}\nSTDERR:\n{fitness_proc.stderr}",
        )
        for fid in EXPECTED_FITNESS_TARGETS:
            self.assertIn(fid, fitness_proc.stdout, f"Expected {fid} pass output in make fitness")
        self.assertIn("All fitness checks passed.", fitness_proc.stdout)

    def test_tc_007_02_readme_completeness_and_hygiene(self) -> None:
        """TC-007-02: REQ-007-02 README.md has required sections, install guides, attribution, links, and clean Mermaid."""
        readme_path = ROOT / "README.md"
        self.assertTrue(readme_path.is_file(), "Missing README.md")
        readme_text = readme_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, readme_text, "README.md must not contain literal em dashes")

        # Badges, value proposition, and status callout
        self.assertIn("https://img.shields.io/badge/License-MIT-yellow.svg", readme_text)
        self.assertIn("https://img.shields.io/github/last-commit/tkdtaylor/writing", readme_text)
        self.assertIn("> **Status.**", readme_text)

        # Mermaid architecture diagram
        self.assertIn("```mermaid", readme_text)
        mermaid_proc = _run_cmd([sys.executable, "scripts/check-mermaid.py", "README.md"])
        self.assertEqual(
            mermaid_proc.returncode,
            0,
            f"check-mermaid.py failed on README.md:\n{mermaid_proc.stdout}\n{mermaid_proc.stderr}",
        )

        # Modes, slash commands, and genre references
        for token in (
            "/write-draft",
            "/write-edit",
            "/write-review",
            "/write-lint",
            "mode=draft",
            "mode=edit",
            "mode=review",
            "mode=lint",
            "references/technical-and-docs.md",
            "references/business-and-executive.md",
            "references/one-pager-and-six-pager.md",
            "references/longform-and-persuasion.md",
        ):
            self.assertIn(token, readme_text, f"README.md missing mode or reference token: {token}")

        # Cross-harness install instructions
        for harness_token in (
            "Claude Code",
            "~/.claude/skills/writing",
            "~/.claude/commands",
            "Google Antigravity",
            "~/.gemini/config/skills/writing",
            ".agents/skills/writing",
            "OpenAI Codex",
            "~/.codex/skills/writing",
            "Cursor",
            ".cursor/rules",
            "GitHub Copilot",
            ".github/skills/writing",
            "Windsurf",
            ".windsurfrules",
        ):
            self.assertIn(
                harness_token,
                readme_text,
                f"README.md missing cross-harness installation token: {harness_token}",
            )

        # CLI usage, samples, training inbox, and prior-art attribution
        for required_snippet in (
            "scripts/prose_lint.py",
            "scripts/strip_markdown.py",
            "scripts/validate_skill.py",
            "samples/technical-doc.before.md",
            "samples/executive-memo.before.md",
            "samples/one-pager.before.md",
            "samples/one-pager.after.md",
            "training/inbox/",
            "https://github.com/addyosmani/clarity",
            "https://github.com/cursor/plugins/tree/main/pstack",
            "clean-room",
            "https://github.com/sponsors/tkdtaylor",
        ):
            self.assertIn(
                required_snippet,
                readme_text,
                f"README.md missing required content: {required_snippet}",
            )

        # Required docs/ and governance links
        for doc_link in (
            "docs/architecture/overview.md",
            "docs/architecture/diagrams.md",
            "docs/spec/SPEC.md",
            "docs/plans/roadmap.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "LICENSE",
        ):
            self.assertIn(doc_link, readme_text, f"README.md missing required link: {doc_link}")
            self.assertTrue((ROOT / doc_link).is_file(), f"Linked target missing on disk: {doc_link}")

        report = validate_skill.validate_repo(ROOT)
        self.assertTrue(report["passed"], f"validate_skill failed: {report['errors']}")

    def test_tc_007_03_changelog_and_end_to_end_pipeline(self) -> None:
        """TC-007-03: REQ-007-03 CHANGELOG.md covers V1 deliverables and CLI pipeline exits 0."""
        changelog_path = ROOT / "CHANGELOG.md"
        self.assertTrue(changelog_path.is_file(), "Missing CHANGELOG.md")
        changelog_text = changelog_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, changelog_text, "CHANGELOG.md must not contain literal em dashes")
        self.assertIn("## [Unreleased]", changelog_text)

        for v1_item in (
            "SKILL.md",
            "commands/",
            "references/",
            "draft-and-brief.md",
            "edit-and-anti-slop.md",
            "review-rubric.md",
            "technical-and-docs.md",
            "business-and-executive.md",
            "one-pager-and-six-pager.md",
            "longform-and-persuasion.md",
            "scripts/",
            "strip_markdown.py",
            "prose_lint.py",
            "validate_skill.py",
            "evals/",
            "JUDGE.md",
            "evals.json",
            "trigger-evals.json",
            "samples/",
            "one-pager",
            "F-001",
            "F-006",
            "F-007",
        ):
            self.assertIn(v1_item, changelog_text, f"CHANGELOG.md missing Version 1 item: {v1_item}")

        # Pipeline 1: strip_markdown.py README.md | prose_lint.py --raw --json
        strip_proc = _run_cmd([sys.executable, "scripts/strip_markdown.py", "README.md"])
        self.assertEqual(strip_proc.returncode, 0, f"strip_markdown.py failed: {strip_proc.stderr}")
        self.assertTrue(strip_proc.stdout.strip(), "strip_markdown.py produced empty stdout on README.md")

        lint_pipe_proc = _run_cmd(
            [sys.executable, "scripts/prose_lint.py", "--raw", "--json"],
            stdin_text=strip_proc.stdout,
        )
        self.assertEqual(
            lint_pipe_proc.returncode,
            0,
            f"prose_lint.py --raw --json failed: {lint_pipe_proc.stderr}",
        )
        lint_payload = json.loads(lint_pipe_proc.stdout)
        self.assertIsInstance(lint_payload, dict)
        for expected_key in (
            "source",
            "word_count",
            "sentence_count",
            "paragraph_count",
            "cadence",
            "lexical_diversity",
            "substance_and_posture",
            "mechanics_and_tells",
        ):
            self.assertIn(expected_key, lint_payload)
        self.assertGreater(lint_payload["word_count"], 500)
        for forbidden_score_key in ("score", "ai_score", "composite_score", "probability"):
            self.assertNotIn(forbidden_score_key, lint_payload)

        # Direct prose_lint check on authored Task 007 Markdown deliverables
        direct_lint = _run_cmd(
            [
                sys.executable,
                "scripts/prose_lint.py",
                "--json",
                "README.md",
                "CHANGELOG.md",
                "docs/spec/fitness-functions.md",
            ]
        )
        self.assertEqual(direct_lint.returncode, 0, f"prose_lint.py failed: {direct_lint.stderr}")
        reports = json.loads(direct_lint.stdout)
        self.assertEqual(len(reports), 3)
        for rep in reports:
            fname = rep.get("source")
            tells = rep["mechanics_and_tells"]
            self.assertEqual(tells["em_dashes"], [], f"{fname} has em_dashes: {tells['em_dashes']}")
            self.assertEqual(tells["emoji_bullets"], [], f"{fname} has emoji_bullets")
            self.assertEqual(tells["hard_wrapped_lines"], [], f"{fname} has hard_wrapped_lines")
            self.assertEqual(tells["connector_colons"], [], f"{fname} has connector_colons: {tells['connector_colons']}")
            self.assertEqual(tells["bold_restatement_bullets"], [], f"{fname} has bold_restatement_bullets")
            self.assertEqual(tells["false_scales"], [], f"{fname} has false_scales: {tells['false_scales']}")
            self.assertEqual(tells["ai_tell_words"], [], f"{fname} has ai_tell_words: {tells['ai_tell_words']}")
            self.assertEqual(tells["inflated_style_verbs"], [], f"{fname} has inflated_style_verbs: {tells['inflated_style_verbs']}")
            self.assertEqual(tells["tech_buzz_nouns"], [], f"{fname} has tech_buzz_nouns: {tells['tech_buzz_nouns']}")
            self.assertEqual(tells["framing_theater"], [], f"{fname} has framing_theater: {tells['framing_theater']}")
            self.assertEqual(tells["contrastive_pivots"], [], f"{fname} has contrastive_pivots")
            self.assertEqual(
                tells["participial_tail_puffery"],
                [],
                f"{fname} has participial_tail_puffery: {tells['participial_tail_puffery']}",
            )
            self.assertEqual(
                tells["copula_avoidance"],
                [],
                f"{fname} has copula_avoidance: {tells['copula_avoidance']}",
            )
            self.assertEqual(
                tells["rhetorical_qa_pivots"],
                [],
                f"{fname} has rhetorical_qa_pivots: {tells['rhetorical_qa_pivots']}",
            )
            self.assertEqual(
                tells["performative_fragments"],
                [],
                f"{fname} has performative_fragments: {tells['performative_fragments']}",
            )
            self.assertEqual(
                tells["stacked_questions"],
                [],
                f"{fname} has stacked_questions: {tells['stacked_questions']}",
            )
            self.assertEqual(
                tells["shorthand_ambiguities"],
                [],
                f"{fname} has shorthand_ambiguities: {tells['shorthand_ambiguities']}",
            )
            self.assertEqual(
                tells["exclamation_marks"],
                [],
                f"{fname} has exclamation_marks: {tells['exclamation_marks']}",
            )
            self.assertEqual(
                tells["false_agency"],
                [],
                f"{fname} has false_agency: {tells['false_agency']}",
            )
            self.assertEqual(
                rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{fname} has importance_without_mechanism: {rep['substance_and_posture']['importance_without_mechanism']}",
            )
            self.assertEqual(
                rep["cadence"]["overloaded_sentences"],
                [],
                f"{fname} has overloaded_sentences: {rep['cadence']['overloaded_sentences']}",
            )

        # Pipeline 2: validate_skill.py --json
        val_proc = _run_cmd([sys.executable, "scripts/validate_skill.py", "--json"])
        self.assertEqual(val_proc.returncode, 0, f"validate_skill.py --json failed:\n{val_proc.stdout}")
        val_payload = json.loads(val_proc.stdout)
        self.assertTrue(val_payload["passed"], f"validate_skill errors: {val_payload['errors']}")
        self.assertEqual(val_payload["errors"], [])
        self.assertLessEqual(val_payload["word_counts"]["SKILL.md"], 1500)
        self.assertLessEqual(val_payload["word_counts"]["combined_runtime"], 10000)


if __name__ == "__main__":
    unittest.main()
