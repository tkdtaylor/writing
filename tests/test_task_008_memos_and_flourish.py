"""Verification tests for Task 008: One-Pager, Six-Pager, and Anti-Flourish Skill Guides.

Covers TC-008-01 through TC-008-04 from
docs/tasks/test-specs/008-one-pager-six-pager-and-anti-flourish-guides-test-spec.md.
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
MEMO_REF_PATH = ROOT / "references" / "one-pager-and-six-pager.md"
EXEC_REF_PATH = ROOT / "references" / "business-and-executive.md"
EDIT_REF_PATH = ROOT / "references" / "edit-and-anti-slop.md"
ADR_002_PATH = (
    ROOT
    / "docs"
    / "architecture"
    / "decisions"
    / "002-narrative-memos-and-anti-flourish-rules.md"
)

EM_DASH = "\u2014"
EMOJI_BULLET_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s*[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55]"
)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _strip_fenced_lines(text: str) -> list[tuple[int, str]]:
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


class TestTask008MemosAndFlourish(unittest.TestCase):
    """Covers TC-008-01 through TC-008-04."""

    def test_tc_008_01_one_pager_and_six_pager_reference(self) -> None:
        """TC-008-01 (REQ-008-01): Format matrix, 5-part One-Pager, 7-part Six-Pager, PR/FAQ, 80%+ prose, Appendix contract."""
        self.assertTrue(
            MEMO_REF_PATH.is_file(),
            f"Missing dedicated memo reference: {MEMO_REF_PATH}",
        )
        text = MEMO_REF_PATH.read_text(encoding="utf-8")
        lower = text.lower()
        words = len(text.split())
        self.assertGreaterEqual(words, 450, f"one-pager-and-six-pager.md too thin ({words}w)")
        self.assertLessEqual(words, 1500, f"one-pager-and-six-pager.md over budget ({words}w)")

        # (a) Format selection matrix (Door-Type Rule)
        self.assertIn("Type 2", text)
        self.assertIn("two-way door", lower)
        self.assertIn("350", text)
        self.assertIn("550", text)
        self.assertIn("Type 1", text)
        self.assertIn("one-way door", lower)
        self.assertIn("2,500", text)
        self.assertIn("15", text)
        self.assertIn("30", text)
        self.assertIn("study hall", lower)
        self.assertIn("ceiling", lower)
        self.assertIn("quota", lower)
        self.assertIn("[TK:", text)

        # Working Backwards PR/FAQ and Safeguard #1 quote rules
        self.assertIn("PR/FAQ", text)
        self.assertIn("Working Backwards", text)
        self.assertIn("[Hypothetical PR-FAQ illustration]", text)
        self.assertIn("[TK: customer quote]", text)
        self.assertRegex(lower, r"never invent quotes.*one-pagers|never invent quotes.*operational")

        # (b) 5-section One-Pager blueprint in sequential order
        one_pager_sections = [
            "BLUF / Decision Call",
            "Problem and Customer/System Baseline",
            "Scope and Explicit Non-Goals",
            "Viable Options and Tradeoffs",
            "Risks, Kill Switch, and Owned Next Steps",
        ]
        op_positions = [text.find(sec) for sec in one_pager_sections]
        for sec, pos in zip(one_pager_sections, op_positions):
            self.assertNotEqual(pos, -1, f"Missing One-Pager section: {sec}")
        self.assertEqual(
            op_positions,
            sorted(op_positions),
            "One-Pager 5-section blueprint must appear in order",
        )
        self.assertIn("Status Quo", text)

        # (c) 7-part Six-Pager blueprint in sequential order
        six_pager_sections = [
            "Context and Governing Question",
            "Tenets",
            "Current State and Candid Lessons Learned",
            "Goals and Vetted Targets",
            "Proposed Plan and Causal Mechanism",
            "Alternatives Considered, Hostile Objections, and Risks",
            "Appendices",
        ]
        sp_positions = [text.find(sec) for sec in six_pager_sections]
        for sec, pos in zip(six_pager_sections, sp_positions):
            self.assertNotEqual(pos, -1, f"Missing Six-Pager section: {sec}")
        self.assertEqual(
            sp_positions,
            sorted(sp_positions),
            "Six-Pager 7-part blueprint must appear in order",
        )
        self.assertIn("mystery novel", lower)
        self.assertIn("real sacrifice", lower)
        self.assertIn("prioritize security, quality, and velocity", lower)
        self.assertIn("input metrics", lower)
        self.assertIn("output metrics", lower)
        self.assertIn("Lessons Learned", text)
        self.assertIn("steelman", lower)

        # (d) 80%+ complete-prose rule, two-way Appendix contract, and anti-failure rules
        self.assertIn("80%+", text)
        self.assertIn("stand alone", lower)
        self.assertIn("Appendix B, Table 2", text)
        self.assertIn("zero narrative overflow", lower)
        self.assertIn("**Bold Pillar:**", text)
        self.assertIn("without sacrificing", text)
        self.assertIn("strawman", lower)

    def test_tc_008_02_skill_and_business_routing_and_comma_splice_guidance(self) -> None:
        """TC-008-02 (REQ-008-02): SKILL.md and business-and-executive.md route memos and warn against comma-splice flattening."""
        self.assertTrue(SKILL_PATH.is_file())
        self.assertTrue(EXEC_REF_PATH.is_file())

        skill_text = SKILL_PATH.read_text(encoding="utf-8")
        exec_text = EXEC_REF_PATH.read_text(encoding="utf-8")

        self.assertLessEqual(len(skill_text.split()), 1500)
        self.assertLessEqual(len(exec_text.split()), 1500)

        fm, body, has_fm = validate_skill.parse_frontmatter(skill_text)
        self.assertTrue(has_fm)
        desc_lower = fm.get("description", "").lower()
        for trigger in ("one-pager", "six-pager", "pr/faq"):
            self.assertIn(
                trigger,
                desc_lower,
                f"SKILL.md frontmatter description missing '{trigger}'",
            )

        # Routing rows in SKILL.md Step 2
        argument_row = next(
            (ln for ln in body.splitlines() if ln.strip().startswith("| `Argument`")),
            "",
        )
        decision_row = next(
            (ln for ln in body.splitlines() if ln.strip().startswith("| `Decision/Update`")),
            "",
        )
        self.assertIn("references/one-pager-and-six-pager.md", argument_row)
        self.assertIn("references/one-pager-and-six-pager.md", decision_row)
        self.assertIn("one-pagers", decision_row.lower())
        self.assertIn("six-pagers", decision_row.lower())
        self.assertIn("pr/faqs", decision_row.lower())

        # Cross-link in references/business-and-executive.md
        exec_lower = exec_text.lower()
        self.assertIn("one-pager-and-six-pager.md", exec_text)
        for term in ("one-pager", "six-pager", "pr/faq"):
            self.assertIn(term, exec_lower, f"business-and-executive.md missing '{term}'")

        # Step 3 punctuation overcorrection / comma-splice warning in SKILL.md
        body_lower = body.lower()
        self.assertIn("comma-splice", body_lower)
        self.assertIn("overcorrection", body_lower)
        self.assertIn("`(...)`", body)
        self.assertIn("parentheses", body_lower)
        self.assertIn("periods", body_lower)
        self.assertIn("flourish", body_lower)

    def test_tc_008_03_edit_and_anti_slop_empirical_flourish_catalog(self) -> None:
        """TC-008-03 (REQ-008-03): edit-and-anti-slop.md documents empirical 2025-2026 anti-flourish patterns."""
        self.assertTrue(EDIT_REF_PATH.is_file())
        text = EDIT_REF_PATH.read_text(encoding="utf-8")
        lower = text.lower()
        words = len(text.split())
        self.assertGreaterEqual(words, 450)
        self.assertLessEqual(words, 1500)

        # Punctuation overcorrection trap
        self.assertIn("overcorrection", lower)
        self.assertIn("comma splices", lower)
        self.assertIn("`(...)`", text)

        # Trailing participial -ing puffery clauses
        for tail in (
            "highlighting",
            "underscoring",
            "ensuring",
            "fostering",
            "showcasing",
            "paving the way for",
        ):
            self.assertIn(tail, lower, f"Missing participial -ing tell: {tail}")

        # Copula avoidance
        for copula in ("serves as a", "stands as a", "functions as a", "marks a", "boasts"):
            self.assertIn(copula, lower, f"Missing copula avoidance tell: {copula}")

        # Self-posed rhetorical Q&A pivots and performative mic-drop fragments
        for qa_or_frag in (
            "The result?",
            "The catch?",
            "Why does this matter?",
            "Full stop.",
            "Simple as that.",
            "And maybe that's the point.",
        ):
            self.assertIn(qa_or_frag, text, f"Missing Q&A pivot or mic-drop tell: {qa_or_frag}")

        # Metaphorical flourish verbs and magic adverbs
        for verb in ("unleash", "harness", "reimagine", "ignite", "weave", "illuminate", "unpack"):
            self.assertIn(f"`{verb}`", text, f"Missing metaphorical flourish verb `{verb}`")
        for adv in ("quietly", "genuinely", "deeply", "remarkably"):
            self.assertIn(f"`{adv}`", text, f"Missing evaluative magic adverb `{adv}`")

        # Expanded negative parallelisms & corrective frames
        for frame in (
            "This isn't X. It's Y.",
            "less like X and more like Y",
            "rather than merely",
            "rather than simply",
            "Not X. Not Y. Z.",
        ):
            self.assertIn(frame, text, f"Missing negative parallelism frame: {frame}")

        # Tradeoff denial, nominalizations, tie-backs, vague plural attributions
        for phrase in (
            "`without sacrificing`",
            "`without compromising`",
            "`the implementation of`",
            "`Together, these...`",
            "`Ultimately, this...`",
            "`Experts argue`",
            "`Industry reports suggest`",
        ):
            self.assertIn(phrase, text, f"Missing anti-flourish pattern {phrase}")

    def test_tc_008_04_adr_002_and_prose_hygiene_and_validator(self) -> None:
        """TC-008-04 (REQ-008-04): ADR 002 exists, touched Markdown passes hygiene and prose_lint, validate_skill exits 0."""
        self.assertTrue(ADR_002_PATH.is_file(), f"Missing ADR 002: {ADR_002_PATH}")
        adr_text = ADR_002_PATH.read_text(encoding="utf-8")
        self.assertIn("# ADR 002", adr_text)
        self.assertIn("Accepted", adr_text)
        for heading in ("## Context", "## Decision", "## Consequences"):
            self.assertIn(heading, adr_text)
        self.assertIn("one-pager-and-six-pager.md", adr_text)
        self.assertIn("comma-splice", adr_text.lower())

        touched_files = (
            SKILL_PATH,
            MEMO_REF_PATH,
            EXEC_REF_PATH,
            EDIT_REF_PATH,
            ADR_002_PATH,
        )
        for md_path in touched_files:
            raw = md_path.read_text(encoding="utf-8")
            _, body, _ = validate_skill.parse_frontmatter(raw)
            non_fenced = _strip_fenced_lines(body)
            prev_line = ""
            for lineno, line in non_fenced:
                self.assertNotIn(
                    EM_DASH,
                    line,
                    f"Prose em dash (U+2014) in {md_path.name}:{lineno}",
                )
                self.assertIsNone(
                    EMOJI_BULLET_RE.match(line),
                    f"Emoji bullet in {md_path.name}:{lineno}",
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
            tells = lint_rep["mechanics_and_tells"]
            for zero_key in (
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
            ):
                self.assertEqual(
                    tells[zero_key],
                    [],
                    f"{md_path.name} triggered {zero_key}: {tells[zero_key]}",
                )
            self.assertEqual(
                lint_rep["cadence"]["overloaded_sentences"],
                [],
                f"{md_path.name} has overloaded sentences: {lint_rep['cadence']['overloaded_sentences']}",
            )

        # Validate full skill package and runtime budget
        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])
        self.assertLessEqual(val_res["word_counts"]["combined_runtime"], 8500)
        self.assertLessEqual(
            val_res["word_counts"]["combined_runtime"],
            validate_skill.COMBINED_MAX_WORDS,
        )

        cli_proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skill.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )
        self.assertEqual(cli_proc.returncode, 0, cli_proc.stdout + cli_proc.stderr)


if __name__ == "__main__":
    unittest.main()
