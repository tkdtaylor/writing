"""Verification tests for Task 018: Blameless Postmortems, Changelogs, 3P Updates, and Reply Discipline.

Covers TC-018-01 through TC-018-03 from
docs/tasks/test-specs/018-postmortems-changelogs-replies-and-3p-guides-test-spec.md.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, strip_markdown, validate_skill

ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = ROOT / "references"
TECH_REF_PATH = REFS_DIR / "technical-and-docs.md"
EXEC_REF_PATH = REFS_DIR / "business-and-executive.md"
LONGFORM_REF_PATH = REFS_DIR / "longform-and-persuasion.md"

EM_DASH = "\u2014"
EN_DASH = "\u2013"
SPACED_DOUBLE_HYPHEN_RE = re.compile(
    r"(?<=[A-Za-z0-9,)\"'])\s+--\s+(?=[A-Za-z0-9\"'(])"
)
SPACED_EN_DASH_RE = re.compile(r"\s+\u2013\s+")
STACKED_NEGATION_RE = re.compile(
    r"\bno\s+[a-z][a-z -]{1,24},\s+no\s+[a-z][a-z -]{1,24},\s+(?:and\s+)?no\s+[a-z]",
    re.IGNORECASE,
)
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


class TestTask018GenreExpansions(unittest.TestCase):
    """Covers TC-018-01 through TC-018-03."""

    def _assert_clean_reference_hygiene(self, path: Path, max_words: int) -> str:
        self.assertTrue(path.is_file(), f"Missing reference file: {path}")
        raw = path.read_text(encoding="utf-8")
        words = len(raw.split())
        self.assertGreaterEqual(words, 450, f"{path.name} too short ({words} words)")
        self.assertLessEqual(
            words,
            max_words,
            f"{path.name} exceeds task ceiling of {max_words} words ({words} words)",
        )
        self.assertLessEqual(
            words,
            1500,
            f"{path.name} exceeds 1,500-word reference budget ({words} words)",
        )

        # Structural Markdown and dash-bypass checks outside fenced code blocks
        prev_line = ""
        for lineno, line in _iter_non_fenced_lines(raw):
            self.assertNotIn(
                EM_DASH,
                line,
                f"Literal em dash (U+2014) found in {path.name}:{lineno}",
            )
            masked_inline = strip_markdown.mask_inline_syntax_for_tells(line)
            self.assertIsNone(
                SPACED_DOUBLE_HYPHEN_RE.search(masked_inline),
                f"Spaced '--' dash substitute outside inline code in {path.name}:{lineno}",
            )
            self.assertIsNone(
                SPACED_EN_DASH_RE.search(masked_inline),
                f"Spaced en-dash (U+2013) outside inline code in {path.name}:{lineno}",
            )
            self.assertIsNone(
                STACKED_NEGATION_RE.search(masked_inline),
                f"Unbackticked stacked negation tell in {path.name}:{lineno}",
            )
            self.assertIsNone(
                EMOJI_BULLET_RE.match(line),
                f"Emoji bullet in {path.name}:{lineno}",
            )

            is_list = bool(LIST_ITEM_RE.match(line))
            prev_is_list = bool(LIST_ITEM_RE.match(prev_line))
            if is_list and prev_line.strip() and not prev_is_list:
                self.fail(f"Missing blank line before list in {path.name}:{lineno}")

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
                self.fail(f"Hard-wrapped paragraph in {path.name}:{lineno}")
            prev_line = line

        lint_rep = prose_lint.analyze_text(raw, source=path.name)
        for tell_key, tell_val in lint_rep["mechanics_and_tells"].items():
            if isinstance(tell_val, list):
                self.assertEqual(
                    tell_val,
                    [],
                    f"{path.name} triggered {tell_key}: {tell_val}",
                )
        self.assertEqual(
            lint_rep["substance_and_posture"]["importance_without_mechanism"],
            [],
            f"{path.name} triggered importance_without_mechanism",
        )
        self.assertEqual(
            lint_rep["cadence"]["overloaded_sentences"],
            [],
            f"{path.name} has overloaded (>35w) sentences: {lint_rep['cadence']['overloaded_sentences']}",
        )
        return raw

    def test_tc_018_01_postmortems_and_changelogs_in_technical_reference(self) -> None:
        """TC-018-01 (REQ-018-01): Blameless postmortems and Keep-a-Changelog blueprints in technical-and-docs.md."""
        text = self._assert_clean_reference_hygiene(TECH_REF_PATH, max_words=1470)

        # Opening paragraph mentions postmortems and changelogs / release notes
        intro_lines = text.splitlines()[:5]
        intro_lower = "\n".join(intro_lines).lower()
        self.assertIn("postmortems", intro_lower)
        self.assertIn("changelogs", intro_lower)
        self.assertIn("release notes", intro_lower)

        # Blueprint 1: Blameless incident postmortems
        pm_section = _extract_h2_section(text, "Blueprint: Blameless incident postmortems")
        self.assertTrue(
            pm_section,
            "Missing `## Blueprint: Blameless incident postmortems` in technical-and-docs.md",
        )
        pm_lower = pm_section.lower()
        self.assertIn("impact", pm_lower)
        self.assertIn("severity", pm_lower)
        self.assertIn("YYYY-MM-DD HH:MM UTC", pm_section)
        self.assertIn("HH:MM UTC", pm_section)
        self.assertIn("root cause", pm_lower)
        self.assertIn("trigger", pm_lower)
        self.assertIn("timeline", pm_lower)
        for milestone in ("alert", "mitigation", "recovery"):
            self.assertIn(milestone, pm_lower, f"Postmortem timeline missing '{milestone}'")
        self.assertRegex(
            pm_lower,
            r"never\s+blame|systemic\s+controls",
            "Postmortem blueprint must require systemic controls over human blame",
        )
        self.assertIn("Action items", pm_section)
        self.assertIn("[TK: ticket ID]", pm_section)

        # Blueprint 2: Changelogs and release notes
        cl_section = _extract_h2_section(text, "Blueprint: Changelogs and release notes")
        self.assertTrue(
            cl_section,
            "Missing `## Blueprint: Changelogs and release notes` in technical-and-docs.md",
        )
        cl_lower = cl_section.lower()
        self.assertIn("`git log`", cl_section)
        self.assertIn("human upgraders", cl_lower)
        self.assertIn("breaking", cl_lower)
        self.assertIn("migration", cl_lower)
        self.assertIn("YYYY-MM-DD", cl_section)
        for bucket in ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"):
            self.assertIn(
                f"`{bucket}`",
                cl_section,
                f"Changelog blueprint missing Keep-a-Changelog bucket `{bucket}`",
            )

    def test_tc_018_02_3p_updates_and_reply_discipline_in_business_reference(self) -> None:
        """TC-018-02 (REQ-018-02): 3P team updates and no-context-rebuilding thread reply discipline."""
        text = self._assert_clean_reference_hygiene(EXEC_REF_PATH, max_words=1200)

        async_section = _extract_h2_section(
            text, "Async updates, emails, and workplace messages"
        )
        self.assertTrue(
            async_section,
            "Missing `## Async updates, emails, and workplace messages` in business-and-executive.md",
        )
        async_lower = async_section.lower()

        # 3P team updates: Progress, Plans, Problems + blocker, owner, escalation ask
        self.assertIn("3P", async_section)
        for p_bucket in ("Progress", "Plans", "Problems"):
            self.assertIn(
                f"`{p_bucket}`",
                async_section,
                f"3P updates missing `{p_bucket}` bucket",
            )
        for risk_anchor in ("blocker", "owner", "escalation"):
            self.assertIn(
                risk_anchor,
                async_lower,
                f"3P `Problems` rule missing '{risk_anchor}'",
            )

        # Thread and reply discipline: line one decision/answer + single new fact, no context-rebuilding
        self.assertIn("reply", async_lower)
        self.assertIn("context-rebuilding", async_lower)
        self.assertIn("line one", async_lower)
        self.assertRegex(
            async_lower,
            r"single\s+new\s+fact|one\s+new\s+fact",
            "Thread reply discipline must isolate the single new fact or link",
        )
        self.assertRegex(
            async_lower,
            r"never\s+restate|bury\s+the\s+(?:answer|call)",
            "Thread reply discipline must forbid restating shared context or burying the call",
        )

    def test_tc_018_03_voc_negation_discipline_punch_rationing_and_claim_unlocks(self) -> None:
        """TC-018-03 (REQ-018-03): VoC phrasing, positive workflow over stacked negations, punch rationing, and [TK: ...] claim unlocks."""
        text = self._assert_clean_reference_hygiene(LONGFORM_REF_PATH, max_words=1180)

        copy_section = _extract_h2_section(text, "Marketing, launch, and landing copy")
        self.assertTrue(
            copy_section,
            "Missing `## Marketing, launch, and landing copy` in longform-and-persuasion.md",
        )
        copy_lower = copy_section.lower()

        # Voice-of-Customer (VoC) language from tickets/calls/interviews over internal jargon
        self.assertIn("Voice-of-Customer", copy_section)
        self.assertIn("`VoC`", copy_section)
        for voc_source in ("tickets", "interviews"):
            self.assertIn(
                voc_source,
                copy_lower,
                f"VoC guidance missing buyer source '{voc_source}'",
            )
        self.assertIn("jargon", copy_lower)

        # Positive workflow statements over stacked negation lists + punch rationing (1 to 2 per page)
        self.assertIn("negation", copy_lower)
        self.assertIn("`No setup call, no templates, no spreadsheets`", copy_section)
        self.assertIn("`1` to `2`", copy_section)
        self.assertIn("per page", copy_lower)

        # Claim unlocks over silent cuts with [TK: ...]
        self.assertIn("[TK:", copy_section)
        self.assertIn("unlock", copy_lower)

        # Validate full skill package and runtime budgets
        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])
        for ref_name, ref_words in val_res["word_counts"]["references"].items():
            self.assertLessEqual(
                ref_words,
                validate_skill.REFERENCE_MAX_WORDS,
                f"{ref_name} exceeds 1,500 words ({ref_words})",
            )
        self.assertLessEqual(
            val_res["word_counts"]["combined_runtime"],
            validate_skill.COMBINED_MAX_WORDS,
        )

        # CLI prose_lint check on all three touched reference files
        lint_proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "prose_lint.py"),
                "references/technical-and-docs.md",
                "references/business-and-executive.md",
                "references/longform-and-persuasion.md",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )
        self.assertEqual(lint_proc.returncode, 0, lint_proc.stdout + lint_proc.stderr)
        self.assertEqual(
            lint_proc.stdout.count("Findings: none"),
            3,
            f"Expected 'Findings: none' for all 3 genre references, got:\n{lint_proc.stdout}",
        )

        # Ensure this test file itself contains zero literal em or en dashes
        self_text = Path(__file__).resolve().read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, self_text)
        self.assertNotIn(EN_DASH, self_text)


if __name__ == "__main__":
    unittest.main()
