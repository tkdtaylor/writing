"""Verification tests for Task 002 workflow mode references (TC-002-01..TC-002-04)."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = ROOT / "references"

WORKFLOW_REFS = (
    "draft-and-brief.md",
    "edit-and-anti-slop.md",
    "review-rubric.md",
)

EMOJI_BULLET_RE = re.compile(
    r"^\s*(?:[-*+]|\d+\.)\s*[\U0001F300-\U0001FAFF\u2600-\u27BF]"
)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")


def strip_fenced_code_blocks(text: str) -> str:
    """Replace fenced code blocks with blank lines while preserving line count."""
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if not in_fence:
            match = re.match(r"^(`{3,}|~{3,})", stripped)
            if match:
                in_fence = True
                fence_marker = match.group(1)[0] * len(match.group(1))
                out.append("")
                continue
            out.append(line)
        else:
            if stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            out.append("")
    return "\n".join(out)


def count_words(text: str) -> int:
    """Return whitespace-delimited word count for a Markdown reference file."""
    return len(text.split())


class TestTask002WorkflowRefs(unittest.TestCase):
    """Test suite verifying workflow mode references under references/."""

    def test_tc_002_01_draft_and_brief_reference(self) -> None:
        """TC-002-01: REQ-002-01 draft-and-brief.md budget and required sections."""
        path = REFS_DIR / "draft-and-brief.md"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        words = count_words(text)
        self.assertGreaterEqual(words, 350, f"draft-and-brief.md too short: {words} words")
        self.assertLessEqual(words, 1500, f"draft-and-brief.md exceeds budget: {words} words")

        # Goal and reader restatement
        self.assertIn("mode=draft", text)
        self.assertIn("Pictured reader", text)
        self.assertIn("Job-to-be-done", text)
        self.assertIn("Core claim or outcome", text)
        self.assertIn("2 to 3", text)

        # Primary-source brief deepening
        self.assertIn("primary", lower)
        self.assertIn("diffs", lower)
        self.assertIn("transcripts", lower)
        self.assertIn("practitioner", lower)

        # Targeted perspective interview capped at <= 5 questions
        self.assertTrue(
            "<= 5" in text or "up to 5" in lower,
            "draft-and-brief.md must cap perspective interview at <= 5 questions",
        )
        self.assertIn("disagrees", lower)
        self.assertIn("caveats", lower)
        self.assertIn("generic filler", lower)

        # [TK: ...] placeholders and external provenance fields
        self.assertIn("[TK:", text)
        self.assertIn("Author material", text)
        self.assertIn("Model contribution", text)
        self.assertIn("Open [TK] items", text)
        self.assertIn("outside", lower)

    def test_tc_002_02_edit_and_anti_slop_reference(self) -> None:
        """TC-002-02: REQ-002-02 edit-and-anti-slop.md 5-step order, 4 tests, and anti-slop rules."""
        path = REFS_DIR / "edit-and-anti-slop.md"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        words = count_words(text)
        self.assertGreaterEqual(words, 450, f"edit-and-anti-slop.md too short: {words} words")
        self.assertLessEqual(words, 1500, f"edit-and-anti-slop.md exceeds budget: {words} words")

        self.assertIn("mode=edit", text)

        # Pre-edit inventory
        self.assertIn("inventory", lower)
        for qualifier in ("`may`", "`can`", "`correlates`"):
            self.assertIn(qualifier, text)

        # Strict 5-step single-pass order verified sequentially
        steps = [
            "Truth and scope",
            "Substance and concrete mechanisms",
            "Structure and mode purity",
            "Sentences and anti-slop mechanics",
            "Craft restoration",
        ]
        positions: list[int] = []
        for step in steps:
            pos = text.find(step)
            self.assertNotEqual(pos, -1, f"Missing edit step: {step}")
            positions.append(pos)
        self.assertEqual(positions, sorted(positions), "Edit steps must appear in strict 1..5 order")

        # Single-pass stop rule
        self.assertIn("Single-pass stop rule", text)
        self.assertIn("one deliberate", lower)

        # Four contextual diagnostic tests
        for test_name in (
            "Importance-without-mechanism test",
            "Flatten test",
            "Relation test",
            "Paragraph swap test",
        ):
            self.assertIn(test_name, text, f"Missing diagnostic test: {test_name}")

        for connector in ("`because`", "`although`", "`when`", "`if`", "`so that`"):
            self.assertIn(connector, text)

        # Structural and lexical anti-slop catalog
        self.assertIn("em dash (U+2014)", text)
        self.assertIn("connector colons", lower)
        self.assertIn("restatement bullets", lower)
        self.assertIn("synonym cycling", lower)
        self.assertIn("one name per thing; repeat it", lower)
        self.assertIn("from X to Y", text)
        self.assertIn("throat-clearing", lower)
        self.assertIn("summary sentences", lower)
        self.assertIn("inflated", lower)
        for buzz in ("`substrate`", "`flywheel`", "`scaffolding`", "`paradigm`", "`nexus`"):
            self.assertIn(buzz, text)
        for theater in ("`here is where it gets interesting`", "`the key insight`"):
            self.assertIn(theater, text)
        self.assertIn("rubric", lower)
        self.assertIn("mirror", lower)

    def test_tc_002_03_review_rubric_reference(self) -> None:
        """TC-002-03: REQ-002-03 review-rubric.md read-only contract, candor, and verdict schema."""
        path = REFS_DIR / "review-rubric.md"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        words = count_words(text)
        self.assertGreaterEqual(words, 300, f"review-rubric.md too short: {words} words")
        self.assertLessEqual(words, 1500, f"review-rubric.md exceeds budget: {words} words")

        self.assertIn("mode=review", text)
        self.assertIn("read-only", lower)
        self.assertIn("never rewrite the document or modify files", lower)
        self.assertIn("candor", lower)
        self.assertIn("sycophancy", lower)

        # Top-level sections in order
        piece_idx = text.find("Piece-level diagnosis")
        passage_idx = text.find("Passage-level findings")
        self.assertNotEqual(piece_idx, -1, "Missing Piece-level diagnosis section")
        self.assertNotEqual(passage_idx, -1, "Missing Passage-level findings section")
        self.assertLess(piece_idx, passage_idx, "Piece-level diagnosis must precede Passage-level findings")

        # Required piece-level fields
        for field in ("`Job`", "`Substance`", "`Trust`", "`Structure`", "`Voice`", "`Ending`", "`Top fixes`"):
            self.assertIn(field, text, f"Missing piece-level field: {field}")

        # Required passage-level verdicts
        for verdict in ("`keep`", "`revise`", "`ask-author`", "`cut`"):
            self.assertIn(verdict, text, f"Missing passage-level verdict: {verdict}")
        self.assertIn("intentional rule-breaking", lower)

    def test_tc_002_04_workflow_references_prose_hygiene(self) -> None:
        """TC-002-04: REQ-002-04 zero em dashes, zero emoji bullets, and continuous paragraphs."""
        for filename in WORKFLOW_REFS:
            path = REFS_DIR / filename
            self.assertTrue(path.is_file(), f"Missing workflow reference: {filename}")
            raw_text = path.read_text(encoding="utf-8")
            prose_text = strip_fenced_code_blocks(raw_text)

            # Zero em dashes outside fenced code blocks
            self.assertNotIn(
                "\u2014",
                prose_text,
                f"{filename} contains prohibited em dash (U+2014) in prose",
            )

            lines = prose_text.splitlines()
            for idx, line in enumerate(lines, start=1):
                # Zero emoji bullets
                self.assertIsNone(
                    EMOJI_BULLET_RE.match(line),
                    f"{filename}:{idx} uses an emoji bullet: {line!r}",
                )

                # Blank line before first list item
                if LIST_ITEM_RE.match(line) and idx > 1:
                    prev = lines[idx - 2]
                    self.assertTrue(
                        prev.strip() == "" or bool(LIST_ITEM_RE.match(prev)),
                        f"{filename}:{idx} starts a list without a preceding blank line",
                    )

                # Continuous single-line prose paragraphs (no hard-wrapped adjacent prose lines)
                is_prose = (
                    bool(line.strip())
                    and not line.lstrip().startswith(("#", ">", "|"))
                    and not LIST_ITEM_RE.match(line)
                )
                if is_prose and idx > 1:
                    prev = lines[idx - 2]
                    prev_is_prose = (
                        bool(prev.strip())
                        and not prev.lstrip().startswith(("#", ">", "|"))
                        and not LIST_ITEM_RE.match(prev)
                        and not prev.endswith("  ")
                    )
                    self.assertFalse(
                        prev_is_prose,
                        f"{filename}:{idx - 1}-{idx} contains hard-wrapped multi-line paragraph",
                    )


if __name__ == "__main__":
    unittest.main()
