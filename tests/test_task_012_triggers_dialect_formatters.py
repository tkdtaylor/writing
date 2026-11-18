"""Verification tests for Task 012: Negative Triggers, Dialect Consistency, and Formatter Precedence.

Covers TC-012-01 through TC-012-03 from
docs/tasks/test-specs/012-negative-triggers-dialect-and-formatter-rules-test-spec.md.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "SKILL.md"
TECH_REF_PATH = ROOT / "references" / "technical-and-docs.md"
CONFIG_SPEC_PATH = ROOT / "docs" / "spec" / "configuration.md"

EM_DASH = "\u2014"
EMOJI_BULLET_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s*[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55]"
)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _extract_h2_section(markdown: str, heading_prefix: str) -> str:
    """Extract content under a matching `## ` heading up to the next `## ` heading."""
    lines = markdown.splitlines()
    collecting = False
    collected: list[str] = []
    target_lower = heading_prefix.lower()
    for line in lines:
        if line.startswith("## "):
            if collecting:
                break
            if line[3:].strip().lower().startswith(target_lower):
                collecting = True
                collected.append(line)
                continue
        if collecting:
            collected.append(line)
    return "\n".join(collected)


def _iter_non_fenced_lines(text: str) -> list[tuple[int, str]]:
    """Return (1-based line_number, line) outside fenced code blocks."""
    out: list[tuple[int, str]] = []
    fence_marker: str | None = None
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        match = re.match(r"^(`{3,}|~{3,})", stripped)
        if match:
            token = match.group(1)
            if fence_marker is None:
                fence_marker = token[0] * len(token)
                continue
            if stripped.startswith(fence_marker):
                fence_marker = None
                continue
        if fence_marker is None:
            out.append((idx, line))
    return out


class TestTask012TriggersDialectFormatters(unittest.TestCase):
    """Covers TC-012-01 through TC-012-03."""

    def test_tc_012_01_skill_negative_triggers_and_word_budget(self) -> None:
        """TC-012-01 (REQ-012-01): SKILL.md frontmatter description has Don't use for... negative triggers and <= 1500 words."""
        self.assertTrue(SKILL_PATH.is_file(), f"Missing {SKILL_PATH}")
        raw_text = SKILL_PATH.read_text(encoding="utf-8")
        word_count = len(raw_text.split())
        self.assertGreaterEqual(word_count, 400)
        self.assertLessEqual(
            word_count,
            1500,
            f"SKILL.md word count {word_count} exceeds 1,500-word budget",
        )

        fm, body, has_fm = validate_skill.parse_frontmatter(raw_text)
        self.assertTrue(has_fm, "SKILL.md must have top-of-file YAML frontmatter")
        self.assertEqual(fm.get("name"), "writing")
        self.assertTrue(body.strip(), "SKILL.md body must not be empty")

        description = fm.get("description", "")
        self.assertIn("Don't use for", description)
        pos_part, neg_part = description.split("Don't use for", 1)
        self.assertTrue(pos_part.strip(), "Positive trigger guidance must precede Don't use for")

        neg_lower = neg_part.lower()
        for required_term in (
            "code",
            "debugging",
            "sql",
            "migrations",
            "container",
            "ci/cd",
            "security",
            "scanning",
            "auto-formatters",
        ):
            self.assertIn(
                required_term,
                neg_lower,
                f"Negative trigger clause missing expected exclusion '{required_term}': {neg_part}",
            )

    def test_tc_012_02_dialect_consistency_and_literal_identifier_preservation(self) -> None:
        """TC-012-02 (REQ-012-02): SKILL.md Step 3 and technical-and-docs.md Layer 4 enforce single dialect and literal UI/API/CLI preservation."""
        self.assertTrue(SKILL_PATH.is_file(), f"Missing {SKILL_PATH}")
        self.assertTrue(TECH_REF_PATH.is_file(), f"Missing {TECH_REF_PATH}")

        skill_raw = SKILL_PATH.read_text(encoding="utf-8")
        tech_raw = TECH_REF_PATH.read_text(encoding="utf-8")

        tech_words = len(tech_raw.split())
        self.assertGreaterEqual(tech_words, 450)
        self.assertLessEqual(
            tech_words,
            1500,
            f"references/technical-and-docs.md word count {tech_words} exceeds 1,500-word budget",
        )

        _, skill_body, _ = validate_skill.parse_frontmatter(skill_raw)
        step3_section = _extract_h2_section(skill_body, "Step 3:")
        layer4_section = _extract_h2_section(tech_raw, "Layer 4: Global English disambiguation")

        self.assertTrue(step3_section, "Could not locate Step 3 section in SKILL.md")
        self.assertTrue(layer4_section, "Could not locate Layer 4 section in technical-and-docs.md")

        for label, section_text in (
            ("SKILL.md Step 3", step3_section),
            ("references/technical-and-docs.md Layer 4", layer4_section),
        ):
            sec_lower = section_text.lower()
            self.assertIn("dialect", sec_lower, f"{label} missing dialect rule")
            self.assertIn("`en-US`", section_text, f"{label} missing `en-US`")
            self.assertIn("`en-GB`", section_text, f"{label} missing `en-GB`")
            self.assertIn("`en-AU`", section_text, f"{label} missing `en-AU`")
            self.assertIn("mixing dialects", sec_lower, f"{label} missing ban on mixing dialects")
            self.assertRegex(
                sec_lower,
                r"never\s+localize\s+or\s+respell",
                f"{label} must forbid localizing or respelling literal identifiers",
            )
            for literal_category in (
                "ui labels",
                "api field names",
                "config keys",
                "cli flags",
                "code identifiers",
            ):
                self.assertIn(
                    literal_category,
                    sec_lower,
                    f"{label} missing protected category '{literal_category}'",
                )
            self.assertIn("`--color`", section_text, f"{label} missing `--color` example")
            self.assertIn(
                "`organization_id`",
                section_text,
                f"{label} missing `organization_id` example",
            )

    def test_tc_012_03_formatter_precedence_hygiene_and_skill_validation(self) -> None:
        """TC-012-03 (REQ-012-03): SKILL.md and configuration.md clarify formatter precedence, pass hygiene/lint, and validate_skill exits 0."""
        self.assertTrue(SKILL_PATH.is_file(), f"Missing {SKILL_PATH}")
        self.assertTrue(CONFIG_SPEC_PATH.is_file(), f"Missing {CONFIG_SPEC_PATH}")

        skill_raw = SKILL_PATH.read_text(encoding="utf-8")
        config_raw = CONFIG_SPEC_PATH.read_text(encoding="utf-8")

        _, skill_body, _ = validate_skill.parse_frontmatter(skill_raw)
        step3_section = _extract_h2_section(skill_body, "Step 3:")
        overrides_section = _extract_h2_section(config_raw, "House-style and voice overrides")

        self.assertTrue(step3_section, "Could not locate Step 3 in SKILL.md")
        self.assertTrue(
            overrides_section,
            "Could not locate House-style and voice overrides in docs/spec/configuration.md",
        )

        for label, section_text in (
            ("SKILL.md Step 3", step3_section),
            ("docs/spec/configuration.md House-style and voice overrides", overrides_section),
        ):
            sec_lower = section_text.lower()
            self.assertIn(
                "no formatter governs",
                sec_lower,
                f"{label} must clarify baseline rule applies when no formatter governs the repo",
            )
            self.assertIn(
                "`prettier --prose-wrap always`",
                section_text,
                f"{label} missing `prettier --prose-wrap always`",
            )
            self.assertIn("`mdformat`", section_text, f"{label} missing `mdformat`")
            self.assertIn("`.editorconfig`", section_text, f"{label} missing `.editorconfig`")
            self.assertIn("`markdownlint`", section_text, f"{label} missing `markdownlint`")
            self.assertIn("precedence", sec_lower, f"{label} missing precedence statement")

        # Verify prose hygiene and zero prose_lint findings across all touched Markdown files
        for md_path in (SKILL_PATH, TECH_REF_PATH, CONFIG_SPEC_PATH):
            raw = md_path.read_text(encoding="utf-8")
            _, body, _ = validate_skill.parse_frontmatter(raw)
            prev_line = ""
            for lineno, line in _iter_non_fenced_lines(body):
                self.assertNotIn(
                    EM_DASH,
                    line,
                    f"Prose em dash (U+2014) found in {md_path.name}:{lineno}",
                )
                self.assertIsNone(
                    EMOJI_BULLET_RE.match(line),
                    f"Emoji bullet found in {md_path.name}:{lineno}",
                )
                is_list = bool(LIST_ITEM_RE.match(line))
                prev_is_list = bool(LIST_ITEM_RE.match(prev_line))
                if is_list and prev_line.strip() and not prev_is_list:
                    self.fail(f"Missing blank line before list in {md_path.name}:{lineno}")
                is_plain = (
                    bool(line.strip())
                    and not is_list
                    and not line.lstrip().startswith(("#", "|", ">", "---"))
                )
                prev_is_plain = (
                    bool(prev_line.strip())
                    and not prev_is_list
                    and not prev_line.lstrip().startswith(("#", "|", ">", "---"))
                )
                if is_plain and prev_is_plain and not prev_line.endswith("  "):
                    self.fail(f"Hard-wrapped paragraph in {md_path.name}:{lineno}")
                prev_line = line

            lint_rep = prose_lint.analyze_text(raw, source=md_path.name)
            for tell_key, tell_val in lint_rep["mechanics_and_tells"].items():
                if isinstance(tell_val, list):
                    self.assertEqual(
                        tell_val,
                        [],
                        f"{md_path.name} triggered {tell_key}: {tell_val}",
                    )
            self.assertEqual(
                lint_rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{md_path.name} triggered importance_without_mechanism",
            )
            self.assertEqual(
                lint_rep["cadence"]["overloaded_sentences"],
                [],
                f"{md_path.name} has overloaded (>35w) sentences: {lint_rep['cadence']['overloaded_sentences']}",
            )

        # Ensure this test file itself contains zero literal em dashes
        self.assertNotIn(EM_DASH, Path(__file__).resolve().read_text(encoding="utf-8"))

        # Run CLIprose_lint and validate_skill checks
        lint_proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "prose_lint.py"),
                "SKILL.md",
                "references/technical-and-docs.md",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )
        self.assertEqual(lint_proc.returncode, 0, lint_proc.stdout + lint_proc.stderr)
        self.assertEqual(
            lint_proc.stdout.count("Findings: none"),
            2,
            f"Expected 'Findings: none' for both files, got:\n{lint_proc.stdout}",
        )

        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])

        val_proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skill.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )
        self.assertEqual(val_proc.returncode, 0, val_proc.stdout + val_proc.stderr)


if __name__ == "__main__":
    unittest.main()
