"""Verification tests for Task 005 evals, JUDGE.md, and calibration samples (TC-005-01..TC-005-04)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import prose_lint

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"
SAMPLES_DIR = ROOT / "samples"

EXPECTED_MODES = {"draft", "edit", "review", "lint"}
EXPECTED_CATEGORIES = {
    "factual_fidelity",
    "medium_fit",
    "false_positive_restraint",
    "voice_sample_boundary",
    "mode_boundary",
    "prompt_injection_isolation",
}

EXPECTED_DIMENSIONS = (
    "Medium and register fit",
    "Factual and epistemic fidelity",
    "Substance and specificity",
    "Structural clarity and reader load",
    "Voice and authorship",
    "Craft and editorial restraint",
)

EXPECTED_HARD_GATES = (
    "truth_and_attribution_fidelity",
    "mode_boundary_compliance",
    "operational_and_medium_preservation",
    "prompt_injection_immunity",
)

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+(.+)$")
WORD_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019_-][A-Za-z0-9]+)*")


def strip_fenced_code_blocks(text: str) -> str:
    """Replace fenced code blocks with blank lines while preserving line numbers."""
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


class TestTask005EvalsAndSamples(unittest.TestCase):
    """Test suite verifying evals/, JUDGE.md, and samples/ calibration pairs."""

    def test_tc_005_01_evals_json_schema_and_coverage(self) -> None:
        """TC-005-01: REQ-005-01 evals/evals.json schema, >=12 cases, 4 modes, and 6 categories."""
        path = EVALS_DIR / "evals.json"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        raw = path.read_text(encoding="utf-8")
        self.assertNotIn(
            "\u2014",
            raw,
            "evals/evals.json should use \\u2014 JSON escapes rather than literal em dashes",
        )
        data = json.loads(raw)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("skill_name"), "writing")

        evals = data.get("evals")
        self.assertIsInstance(evals, list)
        self.assertGreaterEqual(len(evals), 12, f"Expected >= 12 evals, got {len(evals)}")

        seen_ids: set[int] = set()
        seen_names: set[str] = set()
        seen_modes: set[str] = set()
        seen_categories: set[str] = set()

        required_keys = {
            "id",
            "eval_name",
            "category",
            "mode",
            "prompt",
            "expected_output",
            "files",
            "assertions",
        }

        for item in evals:
            self.assertIsInstance(item, dict)
            self.assertTrue(
                required_keys.issubset(item.keys()),
                f"Eval missing required keys: {required_keys - set(item.keys())}",
            )

            eval_id = item["id"]
            self.assertIsInstance(eval_id, int)
            self.assertNotIn(eval_id, seen_ids, f"Duplicate eval id: {eval_id}")
            seen_ids.add(eval_id)

            eval_name = item["eval_name"]
            self.assertIsInstance(eval_name, str)
            self.assertRegex(eval_name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertNotIn(eval_name, seen_names, f"Duplicate eval_name: {eval_name}")
            seen_names.add(eval_name)

            mode = item["mode"]
            self.assertIn(mode, EXPECTED_MODES, f"Invalid mode {mode!r} in eval {eval_id}")
            seen_modes.add(mode)

            category = item["category"]
            self.assertIn(
                category,
                EXPECTED_CATEGORIES,
                f"Invalid category {category!r} in eval {eval_id}",
            )
            seen_categories.add(category)

            self.assertIsInstance(item["prompt"], str)
            self.assertGreaterEqual(len(item["prompt"].strip()), 40)
            self.assertIsInstance(item["expected_output"], str)
            self.assertGreaterEqual(len(item["expected_output"].strip()), 30)

            files = item["files"]
            self.assertIsInstance(files, list)
            for rel_file in files:
                self.assertIsInstance(rel_file, str)
                self.assertTrue(
                    (ROOT / rel_file).is_file(),
                    f"Eval {eval_id} references missing file: {rel_file}",
                )

            assertions = item["assertions"]
            self.assertIsInstance(assertions, list)
            self.assertGreaterEqual(
                len(assertions),
                1,
                f"Eval {eval_id} must have non-empty assertions",
            )
            for assertion in assertions:
                self.assertIsInstance(assertion, str)
                self.assertGreaterEqual(len(assertion.strip()), 20)

        self.assertEqual(seen_modes, EXPECTED_MODES, "Must cover all 4 workflow modes")
        self.assertEqual(
            seen_categories,
            EXPECTED_CATEGORIES,
            "Must cover all 6 safeguard categories",
        )

        # Verify key behavioral scenarios from Task 005 are represented
        combined_blob = json.dumps(evals).lower()
        self.assertIn("may reduce", combined_blob)
        self.assertIn("war stories", combined_blob)
        self.assertIn("diataxis", combined_blob)
        self.assertIn("bluf", combined_blob)
        self.assertIn("contrarian thesis", combined_blob)
        self.assertIn("voice sample", combined_blob)
        self.assertIn("override", combined_blob)
        self.assertIn("microcopy", combined_blob)
        self.assertIn("landing-page", combined_blob)

    def test_tc_005_02_trigger_evals_json_balance_and_realism(self) -> None:
        """TC-005-02: REQ-005-02 evals/trigger-evals.json >=20 queries, >=10 true and >=10 false."""
        path = EVALS_DIR / "trigger-evals.json"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        raw = path.read_text(encoding="utf-8")
        self.assertNotIn("\u2014", raw, "trigger-evals.json must not contain literal em dashes")

        entries = json.loads(raw)
        self.assertIsInstance(entries, list)
        self.assertGreaterEqual(len(entries), 20, f"Expected >= 20 trigger queries, got {len(entries)}")

        pos_count = 0
        neg_count = 0
        seen_queries: set[str] = set()

        for idx, entry in enumerate(entries):
            self.assertIsInstance(entry, dict, f"Entry {idx} is not an object")
            self.assertEqual(
                set(entry.keys()),
                {"query", "should_trigger"},
                f"Entry {idx} must have exact keys query and should_trigger",
            )
            query = entry["query"]
            should_trigger = entry["should_trigger"]

            self.assertIsInstance(query, str)
            self.assertGreaterEqual(
                len(query.strip()),
                40,
                f"Trigger query {idx} shorter than 40 chars: {query!r}",
            )
            self.assertNotIn(query, seen_queries, f"Duplicate trigger query: {query!r}")
            seen_queries.add(query)

            self.assertIs(
                type(should_trigger),
                bool,
                f"Entry {idx} should_trigger must be bool, got {type(should_trigger)}",
            )
            if should_trigger:
                pos_count += 1
            else:
                neg_count += 1

        self.assertGreaterEqual(pos_count, 10, f"Expected >= 10 positive triggers, got {pos_count}")
        self.assertGreaterEqual(neg_count, 10, f"Expected >= 10 negative triggers, got {neg_count}")

    def test_tc_005_03_judge_rubric_gates_dimensions_and_hygiene(self) -> None:
        """TC-005-03: REQ-005-03 evals/JUDGE.md 4 hard gates, 6 dimensions, and prose hygiene."""
        path = EVALS_DIR / "JUDGE.md"
        self.assertTrue(path.is_file(), f"Missing file: {path}")

        raw_text = path.read_text(encoding="utf-8")
        prose_only = strip_fenced_code_blocks(raw_text)

        self.assertNotIn(
            "\u2014",
            prose_only,
            "evals/JUDGE.md contains prohibited em dash (U+2014) outside fenced code blocks",
        )

        lower = raw_text.lower()
        self.assertIn("blinded", lower)
        self.assertIn("candidate a", lower)
        self.assertIn("candidate b", lower)
        self.assertIn("single-output", lower)

        for gate_idx, gate_key in enumerate(EXPECTED_HARD_GATES, start=1):
            self.assertIn(f"Gate {gate_idx}", raw_text, f"Missing Gate {gate_idx} heading")
            self.assertIn(gate_key, raw_text, f"Missing hard gate identifier: {gate_key}")

        for dimension in EXPECTED_DIMENSIONS:
            self.assertIn(dimension, raw_text, f"Missing scored dimension: {dimension}")

        # Verify list spacing and prose_lint hygiene on JUDGE.md
        lines = prose_only.splitlines()
        for idx, line in enumerate(lines, start=1):
            if LIST_ITEM_RE.match(line) and idx > 1:
                prev = lines[idx - 2]
                self.assertTrue(
                    prev.strip() == "" or bool(LIST_ITEM_RE.match(prev)),
                    f"evals/JUDGE.md:{idx} starts a list without a preceding blank line",
                )

        report = prose_lint.analyze_text(raw_text, source="evals/JUDGE.md")
        mech = report["mechanics_and_tells"]
        self.assertEqual(mech["em_dashes"], [])
        self.assertEqual(mech["emoji_bullets"], [])
        self.assertEqual(mech["bold_restatement_bullets"], [])
        self.assertEqual(mech["ai_tell_words"], [])
        self.assertEqual(mech["framing_theater"], [])
        self.assertEqual(mech["hard_wrapped_lines"], [])

    def test_tc_005_04_calibration_samples_and_prose_lint_deltas(self) -> None:
        """TC-005-04: REQ-005-04 samples/ pairs eliminate tells in prose_lint while keeping anchors."""
        readme_path = SAMPLES_DIR / "README.md"
        self.assertTrue(readme_path.is_file(), f"Missing file: {readme_path}")
        readme_text = readme_path.read_text(encoding="utf-8")
        self.assertIn("training/inbox/", readme_text)
        self.assertIn("prose_lint.py", readme_text)
        self.assertNotIn("\u2014", strip_fenced_code_blocks(readme_text))

        readme_report = prose_lint.analyze_text(readme_text, source="samples/README.md")
        for tell_key in (
            "em_dashes",
            "emoji_bullets",
            "bold_restatement_bullets",
            "ai_tell_words",
            "framing_theater",
            "hard_wrapped_lines",
        ):
            self.assertEqual(
                readme_report["mechanics_and_tells"][tell_key],
                [],
                f"samples/README.md has unexpected {tell_key}",
            )

        sample_stems = ("technical-doc", "executive-memo")
        zero_tell_keys = (
            "em_dashes",
            "emoji_bullets",
            "bold_restatement_bullets",
            "ai_tell_words",
            "framing_theater",
            "hard_wrapped_lines",
            "connector_colons",
            "false_scales",
            "inflated_style_verbs",
            "tech_buzz_nouns",
            "contrastive_pivots",
        )

        for stem in sample_stems:
            before_path = SAMPLES_DIR / f"{stem}.before.md"
            after_path = SAMPLES_DIR / f"{stem}.after.md"
            self.assertTrue(before_path.is_file(), f"Missing file: {before_path}")
            self.assertTrue(after_path.is_file(), f"Missing file: {after_path}")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prose_lint.py"),
                    "--json",
                    str(before_path),
                    str(after_path),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            reports = json.loads(proc.stdout)
            self.assertEqual(len(reports), 2)
            before_report, after_report = reports

            before_mech = before_report["mechanics_and_tells"]
            after_mech = after_report["mechanics_and_tells"]

            # .before.md must intentionally trigger all core tell detectors
            for must_trigger in (
                "em_dashes",
                "emoji_bullets",
                "bold_restatement_bullets",
                "ai_tell_words",
                "framing_theater",
            ):
                self.assertGreater(
                    len(before_mech[must_trigger]),
                    0,
                    f"{stem}.before.md expected to trigger {must_trigger}",
                )

            # .after.md must reduce tells to zero while retaining concrete domain anchors
            for clean_key in zero_tell_keys:
                self.assertEqual(
                    after_mech[clean_key],
                    [],
                    f"{stem}.after.md must have zero {clean_key}, got {after_mech[clean_key]}",
                )

            self.assertGreater(
                after_report["substance_and_posture"]["anchors_per_100w"],
                0.0,
                f"{stem}.after.md must preserve concrete anchors_per_100w > 0",
            )

        # Verify domain-specific structural preservation on technical-doc.after.md
        tech_after = (SAMPLES_DIR / "technical-doc.after.md").read_text(encoding="utf-8")
        for token in (
            "X-Signature-256",
            "X-Signature-Timestamp",
            "WEBHOOK_SECRET",
            "300",
            "hmac.compare_digest",
            "Warning:",
        ):
            self.assertIn(token, tech_after)
        self.assertLess(
            tech_after.index("Warning:"),
            tech_after.index("1. "),
            "Warnings must appear before guarded numbered steps in technical-doc.after.md",
        )
        for line in strip_fenced_code_blocks(tech_after).splitlines():
            step_match = NUMBERED_STEP_RE.match(line)
            if step_match:
                step_words = WORD_TOKEN_RE.findall(step_match.group(1))
                self.assertLessEqual(
                    len(step_words),
                    20,
                    f"Procedural step exceeds 20-word STE ceiling ({len(step_words)}w): {line!r}",
                )

        # Verify BLUF decision-brief fields and vetted metrics on executive-memo.after.md
        memo_after = (SAMPLES_DIR / "executive-memo.after.md").read_text(encoding="utf-8")
        for field in (
            "**Call**",
            "**Recommendation**",
            "**Impact**",
            "**Evidence**",
            "**Risk**",
            "[measured]",
            "[inferred]",
            "[open]",
            "[TK:",
            "p95",
        ):
            self.assertIn(field, memo_after, f"executive-memo.after.md missing {field}")


if __name__ == "__main__":
    unittest.main()
