"""Verification tests for Task 017: Edit Input Triage, Cold-Reader Verification, and Humanizer Rules.

Covers TC-017-01 through TC-017-03 from
docs/tasks/test-specs/017-edit-triage-cold-reader-and-humanizer-rules-test-spec.md.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, strip_markdown, validate_skill

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "SKILL.md"
EDIT_REF_PATH = ROOT / "references" / "edit-and-anti-slop.md"
REVIEW_REF_PATH = ROOT / "references" / "review-rubric.md"

EM_DASH = "\u2014"
EN_DASH = "\u2013"

# Pre-verify compatibility with Task 019's dash-bypass, chatbot, and meta/strawman patterns
# on inline-code-masked and double-quote-masked prose lines.
SPACED_DOUBLE_HYPHEN_RE = re.compile(
    r"(?<=[A-Za-z0-9,)\"'])\s+--\s+(?=[A-Za-z0-9\"'(])"
)
SPACED_EN_DASH_RE = re.compile(r"\s+\u2013\s+")
UPCOMING_CHATBOT_RE = re.compile(
    r"(?:"
    r"\b(?:great|excellent|wonderful)\s+question\b|"
    r"\bi\s+hope\s+this\s+helps\b|"
    r"\bhappy\s+to\s+help\b|"
    r"\blet\s+me\s+know\s+if\s+you(?:'d\s+like|\s+want|\s+need)\b|"
    r"\bwould\s+you\s+like\s+me\s+to\b|"
    r"\bfeel\s+free\s+to\s+ask\b|"
    r"^\s*(?:certainly|of\s+course|sure\s+thing)[,!.]|"
    r"\bas\s+of\s+my\s+(?:last\s+)?(?:knowledge|training)\s+(?:update|cutoff)\b|"
    r"\bup\s+to\s+my\s+(?:last\s+)?(?:training|knowledge)\b|"
    r"\bwhile\s+specific\s+details\s+are\s+(?:limited|scarce)\b|"
    r"\bnot\s+(?:widely|extensively)\s+documented\s+in\s+(?:readily\s+)?available\s+sources\b"
    r")",
    re.IGNORECASE,
)
UPCOMING_META_STRAWMAN_RE = re.compile(
    r"(?:"
    r"\bthis\s+(?:section|document|guide|page)\s+is\s+organized\s+by\b|"
    r"\bthe\s+table\s+below\s+(?:compares|lists|summarizes|shows)\b|"
    r"\bthe\s+figures\s+below\s+(?:are|were)\s+(?:compiled|drawn)\s+from\b|"
    r"\bdespite\s+these\s+challenges,\s+[^.?!]{1,80}\bcontinues\s+to\s+thrive\b|"
    r"\bthe\s+future\s+looks\s+(?:bright|promising)\b|"
    r"\bexciting\s+times\s+lie\s+ahead\b|"
    r"\bdon't\s+get\s+me\s+wrong\b|"
    r"\bi'm\s+not\s+saying\s+that\b|"
    r"\b(?:a\s+tempting|an\s+obvious)\s+approach\s+would\s+be\s+to\b|"
    r"\bone\s+might\s+be\s+tempted\s+to\b|"
    r"\bno\s+[a-z][a-z -]{1,24},\s+no\s+[a-z][a-z -]{1,24},\s+(?:and\s+)?no\s+[a-z]"
    r")",
    re.IGNORECASE,
)
DOUBLE_QUOTED_RE = re.compile(r'"(?:\\.|[^"\\\n])*"|\u201c[^\u201d\n]*\u201d')


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


class TestTask017EditTriageAndColdReader(unittest.TestCase):
    """Covers TC-017-01 through TC-017-03."""

    def _assert_clean_prose_and_upcoming_detectors(self, md_path: Path) -> None:
        raw = md_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, raw, f"{md_path.name} contains literal em dash (U+2014)")
        self.assertNotIn(EN_DASH, raw, f"{md_path.name} contains literal en dash (U+2013)")

        rep = prose_lint.analyze_text(raw, source=md_path.name)
        for tell_key, tell_val in rep["mechanics_and_tells"].items():
            if isinstance(tell_val, list):
                self.assertEqual(
                    tell_val,
                    [],
                    f"{md_path.name} triggered {tell_key}: {tell_val}",
                )
        self.assertEqual(
            rep["substance_and_posture"]["importance_without_mechanism"],
            [],
            f"{md_path.name} triggered importance_without_mechanism",
        )
        self.assertEqual(
            rep["cadence"]["overloaded_sentences"],
            [],
            f"{md_path.name} has overloaded (>35w) sentences: {rep['cadence']['overloaded_sentences']}",
        )

        md_struct = strip_markdown.extract_markdown_structure(raw)
        for idx, mline in enumerate(md_struct.masked_lines, start=1):
            if not mline.strip():
                continue
            code_masked = strip_markdown.mask_inline_syntax_for_tells(mline)
            self.assertIsNone(
                SPACED_DOUBLE_HYPHEN_RE.search(code_masked),
                f"{md_path.name}:{idx} has unbackticked spaced double-hyphen: {mline!r}",
            )
            self.assertIsNone(
                SPACED_EN_DASH_RE.search(code_masked),
                f"{md_path.name}:{idx} has unbackticked spaced en-dash: {mline!r}",
            )
            quote_masked = DOUBLE_QUOTED_RE.sub(" ", code_masked)
            self.assertIsNone(
                UPCOMING_CHATBOT_RE.search(quote_masked),
                f"{md_path.name}:{idx} has unbackticked chatbot tell phrase: {mline!r}",
            )
            self.assertIsNone(
                UPCOMING_META_STRAWMAN_RE.search(quote_masked),
                f"{md_path.name}:{idx} has unbackticked meta/strawman tell phrase: {mline!r}",
            )

    def test_tc_017_01_skill_triggers_triage_cold_reader_and_dash_mechanics(self) -> None:
        """TC-017-01 (REQ-017-01): SKILL.md triggers, 3-way edit triage, cold-reader review hook, and dash-bypass mechanics."""
        self.assertTrue(SKILL_PATH.is_file(), f"Missing {SKILL_PATH}")
        raw = SKILL_PATH.read_text(encoding="utf-8")
        words = len(raw.split())
        self.assertGreaterEqual(words, 400)
        self.assertLessEqual(words, 1480, f"SKILL.md exceeds 1,480-word cap: {words}")
        self.assertLessEqual(words, 1500)

        fm, body, has_fm = validate_skill.parse_frontmatter(raw)
        self.assertTrue(has_fm)
        description = fm.get("description", "")
        self.assertIn("Don't use for", description)
        pos_part, neg_part = description.split("Don't use for", 1)
        pos_lower = pos_part.lower()
        self.assertIn("postmortems", pos_lower)
        self.assertIn("release notes", pos_lower)
        self.assertTrue(neg_part.strip())

        step0 = _extract_h2_section(body, "Step 0:")
        self.assertTrue(step0, "Missing Step 0 section in SKILL.md")
        edit_line = next(
            (ln for ln in step0.splitlines() if "`mode=edit`" in ln),
            "",
        )
        review_line = next(
            (ln for ln in step0.splitlines() if "`mode=review`" in ln),
            "",
        )
        self.assertTrue(edit_line, "Missing mode=edit bullet in SKILL.md Step 0")
        self.assertIn("triage", edit_line.lower())
        for triage_mode in ("`slop/notes`", "`real voice`", "`point edit`"):
            self.assertIn(triage_mode, edit_line)

        self.assertTrue(review_line, "Missing mode=review bullet in SKILL.md Step 0")
        self.assertIn("zero-context", review_line.lower())
        self.assertIn("cold-reader", review_line.lower())
        self.assertIn("high-stakes", review_line.lower())

        step3 = _extract_h2_section(body, "Step 3:")
        self.assertTrue(step3, "Missing Step 3 section in SKILL.md")
        step3_lower = step3.lower()
        self.assertIn("sentence-case headings", step3_lower)
        self.assertIn("`## Verify webhook signatures`", step3)
        self.assertIn("Title Case", step3)
        self.assertIn("` -- `", step3)
        self.assertIn("`U+2013`", step3)
        self.assertIn("`U+2014`", step3)

        self._assert_clean_prose_and_upcoming_detectors(SKILL_PATH)

    def test_tc_017_02_edit_and_anti_slop_triage_leave_it_alone_unlocks_and_catalog(self) -> None:
        """TC-017-02 (REQ-017-02): edit-and-anti-slop.md 3-way triage, Leave-it-alone test, claim unlocks, and WP:AI catalog."""
        self.assertTrue(EDIT_REF_PATH.is_file(), f"Missing {EDIT_REF_PATH}")
        raw = EDIT_REF_PATH.read_text(encoding="utf-8")
        lower = raw.lower()
        words = len(raw.split())
        self.assertGreaterEqual(words, 450)
        self.assertLessEqual(
            words,
            1350,
            f"references/edit-and-anti-slop.md exceeds 1,350-word cap: {words}",
        )
        self.assertLessEqual(words, 1500)

        # Section 1: 3-way input diagnosis
        sec1 = _extract_h2_section(raw, "1.")
        self.assertTrue(sec1, "Missing Section 1 in edit-and-anti-slop.md")
        for bucket in (
            "Slop or rough notes",
            "Real author voice present",
            "Point edit",
        ):
            self.assertIn(bucket, sec1)
        self.assertIn("`ship`", sec1)
        self.assertIn("`stuff`", sec1)
        self.assertIn("lock", sec1.lower())
        self.assertIn("surrounding text untouched", sec1.lower())

        # Section 2: Declined claims name their unlock + Leave-it-alone test
        sec2 = _extract_h2_section(raw, "2.")
        self.assertTrue(sec2, "Missing Section 2 in edit-and-anti-slop.md")
        self.assertIn("Declined claims name their unlock", sec2)
        self.assertIn("[TK:", sec2)
        self.assertIn("Leave-it-alone test", sec2)
        self.assertRegex(sec2.lower(), r"merely\s+different\s+rather\s+than\s+(?:measurably\s+)?clearer")

        # Section 4: WP:AI / humanizer catalog entries wrapped in inline code spans
        sec4 = _extract_h2_section(raw, "4.")
        self.assertTrue(sec4, "Missing Section 4 in edit-and-anti-slop.md")
        self.assertIn("` -- `", sec4)
        self.assertIn("U+2013", sec4)
        self.assertIn("en-dash", sec4.lower())

        for code_example in (
            "`Great question`",
            "`I hope this helps`",
            "`Happy to help`",
            "`Certainly,`",
            "`as of my last update`",
            "`while specific details are limited`",
            "`based on available information`",
            "`this section is organized by`",
            "`the table below compares`",
            "`Despite these challenges",
            "`This isn't about`",
            "`I'm not saying`",
            "`Don't get me wrong`",
            "`A tempting approach would be`",
            "`No setup call, no templates, no spreadsheets`",
        ):
            self.assertIn(
                code_example,
                sec4,
                f"Section 4 missing inline-code tell example: {code_example}",
            )
        self.assertIn("arguing with no one", lower)
        self.assertIn("No X, no Y, no Z", sec4)
        self.assertRegex(sec4.lower(), r"repeat.*heading")

        self._assert_clean_prose_and_upcoming_detectors(EDIT_REF_PATH)

    def test_tc_017_03_review_rubric_cold_reader_and_runtime_budgets(self) -> None:
        """TC-017-03 (REQ-017-03): review-rubric.md Cold-reader pass, runtime word budgets, and zero prose_lint tells."""
        self.assertTrue(REVIEW_REF_PATH.is_file(), f"Missing {REVIEW_REF_PATH}")
        raw = REVIEW_REF_PATH.read_text(encoding="utf-8")
        words = len(raw.split())
        self.assertGreaterEqual(words, 300)
        self.assertLessEqual(
            words,
            1000,
            f"references/review-rubric.md exceeds 1,000-word cap: {words}",
        )
        self.assertLessEqual(words, 1500)

        sec5 = _extract_h2_section(raw, "5. Zero-context cold-reader pass")
        self.assertTrue(
            sec5,
            "Missing '## 5. Zero-context cold-reader pass' section in review-rubric.md",
        )
        sec5_lower = sec5.lower()
        for doc_kind in ("rfcs", "six-pagers", "specs", "onboarding"):
            self.assertIn(doc_kind, sec5_lower, f"Cold-reader section missing doc kind '{doc_kind}'")
        self.assertRegex(sec5, r"3.*5")
        self.assertIn("subagent", sec5_lower)
        self.assertTrue(
            "zero chat history" in sec5_lower or "without conversation history" in sec5_lower,
            "Cold-reader pass must specify zero chat/conversation history",
        )
        for check_dim in ("assumptions", "ambiguous", "contradict"):
            self.assertIn(check_dim, sec5_lower)
        self.assertIn("Passage-level findings", sec5)
        self.assertIn("`revise`", sec5)
        self.assertIn("`ask-author`", sec5)
        self.assertIn("read-only", sec5_lower)

        self._assert_clean_prose_and_upcoming_detectors(REVIEW_REF_PATH)

        # Validate full repo budgets and prose_lint CLI across all 3 touched files
        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])
        self.assertLessEqual(
            val_res["word_counts"]["combined_runtime"],
            validate_skill.COMBINED_MAX_WORDS,
        )

        lint_proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "prose_lint.py"),
                "SKILL.md",
                "references/edit-and-anti-slop.md",
                "references/review-rubric.md",
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
            f"Expected 'Findings: none' on all 3 files, got:\n{lint_proc.stdout}",
        )

        # Ensure this test file itself contains zero literal em or en dashes
        self_text = Path(__file__).resolve().read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, self_text)
        self.assertNotIn(EN_DASH, self_text)


if __name__ == "__main__":
    unittest.main()
