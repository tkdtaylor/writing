"""Verification suite for Task 003: Genre and Register References (TC-003-01..TC-003-04)."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = ROOT / "references"

GENRE_FILES = (
    "technical-and-docs.md",
    "business-and-executive.md",
    "longform-and-persuasion.md",
)

EMOJI_RE = re.compile(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")


def strip_fenced_code(markdown: str) -> list[tuple[int, str]]:
    """Return (1-based line number, line) pairs outside fenced code blocks."""
    kept: list[tuple[int, str]] = []
    fence_marker: str | None = None
    for lineno, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_marker is None and fence_match:
            fence_marker = fence_match.group(1)[0] * len(fence_match.group(1))
            continue
        if fence_marker is not None:
            if stripped.startswith(fence_marker[0] * len(fence_marker)) and re.fullmatch(
                rf"{re.escape(fence_marker[0])}{{{len(fence_marker)},}}", stripped
            ):
                fence_marker = None
            continue
        kept.append((lineno, line))
    return kept


def find_prose_hygiene_issues(markdown: str) -> dict[str, list[int]]:
    """Scan non-code lines for em dashes, emoji bullets, hard-wrapped prose, and list spacing."""
    em_dashes: list[int] = []
    emoji_bullets: list[int] = []
    hard_wrapped: list[int] = []
    unspaced_lists: list[int] = []

    non_code = strip_fenced_code(markdown)

    def is_plain_prose(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        if s.startswith(("#", "|", ">", "---")):
            return False
        if LIST_LINE_RE.match(line):
            return False
        return True

    for idx, (lineno, line) in enumerate(non_code):
        if "\u2014" in line:
            em_dashes.append(lineno)
        if LIST_LINE_RE.match(line) and EMOJI_RE.search(line):
            emoji_bullets.append(lineno)
        if LIST_LINE_RE.match(line) and idx > 0:
            prev_lineno, prev_line = non_code[idx - 1]
            if prev_lineno == lineno - 1 and prev_line.strip() and not LIST_LINE_RE.match(prev_line):
                unspaced_lists.append(lineno)
        if idx > 0:
            prev_lineno, prev_line = non_code[idx - 1]
            if (
                prev_lineno == lineno - 1
                and is_plain_prose(prev_line)
                and is_plain_prose(line)
                and not prev_line.endswith("  ")
            ):
                hard_wrapped.append(lineno)

    return {
        "em_dashes": em_dashes,
        "emoji_bullets": emoji_bullets,
        "hard_wrapped": hard_wrapped,
        "unspaced_lists": unspaced_lists,
    }


class TestTask003GenreReferences(unittest.TestCase):
    """Tests for REQ-003-01 through REQ-003-04 (TC-003-01..TC-003-04)."""

    def test_tc_003_01_technical_and_docs_reference(self) -> None:
        """TC-003-01 (REQ-003-01): 4-layer technical writing standard and technical blueprints."""
        path = REFS_DIR / "technical-and-docs.md"
        self.assertTrue(path.is_file(), f"Missing reference file: {path}")

        text = path.read_text(encoding="utf-8")
        word_count = len(text.split())
        self.assertGreaterEqual(word_count, 450, f"Too short ({word_count} words)")
        self.assertLessEqual(word_count, 1500, f"Exceeds 1,500-word budget ({word_count} words)")

        lower = text.lower()
        # Layer 1: Diataxis mode purity and all 4 modes
        self.assertIn("diataxis", lower)
        for mode in ("Tutorial", "How-to", "Reference", "Explanation"):
            self.assertIn(mode, text, f"Missing Diataxis mode: {mode}")
        self.assertRegex(lower, r"split.*link|one mode per")

        # Layer 2: Developer style
        self.assertIn("`you`", text)
        self.assertIn("present tense", lower)
        self.assertIn("conditions before instructions", lower)
        self.assertIn("common path first", lower)
        for filler in ("`simply`", "`easily`", "`just`", "`please`"):
            self.assertIn(filler, text)
        self.assertIn("sentence-case", lower)

        # Layer 3: ASD-STE100 procedural clarity
        self.assertIn("ASD-STE100", text)
        self.assertRegex(text, r"<= ?20|20[- ]word")
        self.assertRegex(lower, r"warnings.*before|before.*command|before.*step")

        # Layer 4: Global English disambiguation
        self.assertIn("Global English", text)
        self.assertIn("`only`", text)
        self.assertIn("`not`", text)
        self.assertIn("`this`", text)
        self.assertIn("`which`", text)
        self.assertIn("and/or", text)

        # Concrete blueprints: README, RFC/ADR, PR/change briefings (< 40 lines)
        self.assertIn("README", text)
        self.assertIn("quickstart", lower)
        self.assertIn("RFC", text)
        self.assertIn("ADR", text)
        self.assertIn("non-goals", lower)
        self.assertRegex(text, r"<\s*40\s*lines|under `40` lines")
        for pr_field in ("Why", "What changed", "Scope", "Tradeoffs", "Blast radius", "Verification"):
            self.assertIn(pr_field, text, f"Missing PR briefing field: {pr_field}")

    def test_tc_003_02_business_and_executive_reference(self) -> None:
        """TC-003-02 (REQ-003-02): BLUF memos, decision briefs, epistemic tags, metric vetting, emails."""
        path = REFS_DIR / "business-and-executive.md"
        self.assertTrue(path.is_file(), f"Missing reference file: {path}")

        text = path.read_text(encoding="utf-8")
        word_count = len(text.split())
        self.assertGreaterEqual(word_count, 400, f"Too short ({word_count} words)")
        self.assertLessEqual(word_count, 1500, f"Exceeds 1,500-word budget ({word_count} words)")

        lower = text.lower()
        # BLUF memos and governing takeaways
        self.assertIn("BLUF", text)
        self.assertIn("Bottom Line Up Front", text)
        self.assertIn("governing takeaways", lower)

        # Self-contained decision briefs (< 100 words backstory, riskiest first, baseline cost, 5 fields)
        self.assertRegex(text, r"<\s*100|under `100` words")
        self.assertIn("consumer impact", lower)
        self.assertIn("riskiest first", lower)
        self.assertIn("baseline cost", lower)
        for field in ("Call", "Recommendation", "Impact", "Evidence", "Risk"):
            self.assertIn(field, text, f"Missing decision brief field: {field}")

        # Epistemic labels
        for tag in ("measured", "inferred", "open"):
            self.assertIn(f"`{tag}`", text, f"Missing epistemic label: {tag}")

        # 4-part metric vetting checklist
        for item in ("Unit", "Sample", "Baseline", "Limiter"):
            self.assertIn(item, text, f"Missing metric vetting item: {item}")
        self.assertIn("inconclusive", lower)

        # Async updates, emails, and messages
        self.assertIn("line one", lower)
        self.assertIn("standalone bullets", lower)
        self.assertIn("emails", lower)
        self.assertRegex(lower, r"sycophan|flattery")

    def test_tc_003_03_longform_and_persuasion_reference(self) -> None:
        """TC-003-03 (REQ-003-03): Essays, landing copy, UX microcopy, speeches/slides/diagrams, narrative."""
        path = REFS_DIR / "longform-and-persuasion.md"
        self.assertTrue(path.is_file(), f"Missing reference file: {path}")

        text = path.read_text(encoding="utf-8")
        word_count = len(text.split())
        self.assertGreaterEqual(word_count, 450, f"Too short ({word_count} words)")
        self.assertLessEqual(word_count, 1500, f"Exceeds 1,500-word budget ({word_count} words)")

        lower = text.lower()
        # Essays, blog posts, newsletters
        self.assertIn("sentence one", lower)
        self.assertIn("sentence two", lower)
        self.assertIn("cover-the-page", lower)
        self.assertIn("steelman", lower)
        self.assertIn("victory-lap", lower)

        # Marketing and landing copy: problem -> mechanism -> proof -> single CTA
        self.assertIn("job-to-be-done", lower)
        self.assertIn("mechanism", lower)
        self.assertIn("proof", lower)
        self.assertIn("CTA", text)

        # UX microcopy
        self.assertIn("Error messages", text)
        self.assertIn("Verb + Noun", text)
        self.assertIn("empty states", lower)

        # Speeches, slides, and progressive visuals
        self.assertIn("breath", lower)
        self.assertIn("one point per slide", lower)
        self.assertRegex(text, r"<=\s*6.*boxes")
        self.assertRegex(text, r"<=\s*8.*words")
        self.assertIn("reader", lower)
        self.assertIn("one new component per step", lower)

        # Creative and narrative prose
        self.assertIn("sensory detail", lower)
        self.assertIn("fragments", lower)
        self.assertIn("dialogue", lower)

    def test_tc_003_04_prose_hygiene_across_genre_references(self) -> None:
        """TC-003-04 (REQ-003-04): Zero em dashes outside code, zero emoji bullets, single-line paragraphs."""
        for filename in GENRE_FILES:
            path = REFS_DIR / filename
            self.assertTrue(path.is_file(), f"Missing reference file: {path}")
            content = path.read_text(encoding="utf-8")
            issues = find_prose_hygiene_issues(content)
            self.assertEqual(
                issues["em_dashes"],
                [],
                f"{filename} contains prose em dashes on lines {issues['em_dashes']}",
            )
            self.assertEqual(
                issues["emoji_bullets"],
                [],
                f"{filename} contains emoji bullets on lines {issues['emoji_bullets']}",
            )
            self.assertEqual(
                issues["hard_wrapped"],
                [],
                f"{filename} contains hard-wrapped multi-line paragraphs on lines {issues['hard_wrapped']}",
            )
            self.assertEqual(
                issues["unspaced_lists"],
                [],
                f"{filename} is missing a blank line before list on lines {issues['unspaced_lists']}",
            )

        # Verify the detector catches violations outside code while ignoring fenced code blocks.
        dirty_sample = (
            "# Sample\n\n"
            "First line of a wrapped paragraph\n"
            "second line of that wrapped paragraph \u2014 bad dash.\n"
            "- \u2705 Emoji bullet without blank line\n\n"
            "```text\n"
            "Code block line one \u2014 allowed inside fence\n"
            "- \u2705 Allowed inside fence\n"
            "```\n"
        )
        detected = find_prose_hygiene_issues(dirty_sample)
        self.assertEqual(detected["em_dashes"], [4])
        self.assertEqual(detected["hard_wrapped"], [4])
        self.assertEqual(detected["emoji_bullets"], [5])
        self.assertEqual(detected["unspaced_lists"], [5])


if __name__ == "__main__":
    unittest.main()
