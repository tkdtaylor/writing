"""Verification tests for Task 020: v1.3 Evals, Documentation, and Full Integration Sync.

Covers TC-020-01 through TC-020-03 from
docs/tasks/test-specs/020-v13-evals-readme-and-changelog-sync-test-spec.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, validate_skill
from tests import (
    test_task_010_memo_samples_and_sync,
    test_task_014_clean_packaging,
    test_task_015_cli_safety_and_models,
    test_task_016_doc_and_diagram_sync,
)

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"
EM_DASH = "\u2014"
EN_DASH = "\u2013"

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
    "mixed_dialects",
)

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
            tok = match.group(1)
            if fence_marker is None:
                fence_marker = tok[0] * len(tok)
                out.append("")
                continue
            if stripped.startswith(fence_marker):
                fence_marker = None
                out.append("")
                continue
        out.append(line if fence_marker is None else "")
    return "\n".join(out)


class TestTask020V13EvalsAndDocs(unittest.TestCase):
    """Covers TC-020-01 through TC-020-03."""

    def test_tc_020_01_v13_evals_and_balanced_trigger_evals(self) -> None:
        """TC-020-01 (REQ-020-01): evals.json >= 22 cases (ids 20..22), trigger-evals.json >= 34 balanced 50/50, validate_skill passes."""
        evals_path = EVALS_DIR / "evals.json"
        triggers_path = EVALS_DIR / "trigger-evals.json"

        raw_evals = evals_path.read_text(encoding="utf-8")
        raw_triggers = triggers_path.read_text(encoding="utf-8")

        self.assertNotIn(EM_DASH, raw_evals, "evals.json must contain zero literal em dashes")
        self.assertNotIn(EN_DASH, raw_evals, "evals.json must contain zero literal en dashes")
        self.assertNotIn(EM_DASH, raw_triggers, "trigger-evals.json must contain zero literal em dashes")
        self.assertNotIn(EN_DASH, raw_triggers, "trigger-evals.json must contain zero literal en dashes")

        evals_payload = json.loads(raw_evals)
        evals = evals_payload["evals"]
        self.assertGreaterEqual(len(evals), 22, f"Expected >= 22 eval cases, got {len(evals)}")

        by_id = {item["id"]: item for item in evals}
        for required_id in (20, 21, 22):
            self.assertIn(required_id, by_id, f"Missing eval case id={required_id}")

        # (a) Case 20: blameless incident postmortem + Keep-a-Changelog release note (mode=draft)
        case_20 = by_id[20]
        self.assertEqual(case_20["mode"], "draft")
        self.assertEqual(case_20["category"], "medium_fit")
        blob_20 = json.dumps(case_20).lower()
        for tok in (
            "postmortem",
            "root cause",
            "trigger",
            "utc",
            "[tk:",
            "changelog",
            "v2.4.0",
            "breaking",
        ):
            self.assertIn(tok, blob_20, f"Eval case 20 missing expected token '{tok}'")

        # (b) Case 21: 3-way edit triage preserving founder voice + declined-claim [TK] unlock (mode=edit)
        case_21 = by_id[21]
        self.assertEqual(case_21["mode"], "edit")
        self.assertIn(case_21["category"], {"false_positive_restraint", "voice_sample_boundary"})
        blob_21 = json.dumps(case_21).lower()
        for tok in (
            "ship",
            "stuff",
            "45%",
            "no setup call, no templates, no spreadsheets",
            "[tk:",
            "cohort",
        ):
            self.assertIn(tok, blob_21, f"Eval case 21 missing expected token '{tok}'")

        # (c) Case 22: zero-context cold-reader RFC review + reply context-rebuilding (mode=review)
        case_22 = by_id[22]
        self.assertEqual(case_22["mode"], "review")
        self.assertEqual(case_22["category"], "mode_boundary")
        blob_22 = json.dumps(case_22).lower()
        for tok in (
            "cold-reader",
            "context-rebuilding",
            "read-only",
            "piece-level diagnosis",
            "passage-level findings",
        ):
            self.assertIn(tok, blob_22, f"Eval case 22 missing expected token '{tok}'")

        # Trigger evals: >= 34 balanced 50/50 true/false with v1.3 positive & negative queries
        triggers = json.loads(raw_triggers)
        self.assertGreaterEqual(len(triggers), 34, f"Expected >= 34 trigger queries, got {len(triggers)}")
        pos_queries = [t["query"] for t in triggers if t["should_trigger"] is True]
        neg_queries = [t["query"] for t in triggers if t["should_trigger"] is False]
        self.assertEqual(
            len(pos_queries),
            len(neg_queries),
            f"Trigger queries must stay 50/50 balanced, got {len(pos_queries)} true vs {len(neg_queries)} false",
        )
        self.assertGreaterEqual(len(pos_queries), 17)

        pos_blob = " ".join(pos_queries).lower()
        neg_blob = " ".join(neg_queries).lower()
        self.assertIn("blameless", pos_blob)
        self.assertIn("postmortem", pos_blob)
        self.assertIn("keep a changelog", pos_blob)
        self.assertIn("release notes", pos_blob)
        self.assertIn("git tag", neg_blob)
        self.assertIn("jq", neg_blob)

        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertEqual(val_res["errors"], [])

    def test_tc_020_02_readme_agents_changelog_and_roadmap_sync_and_hygiene(self) -> None:
        """TC-020-02 (REQ-020-02): README, AGENTS, CHANGELOG, and roadmap document v1.3 additions with zero prose_lint hits."""
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        roadmap_text = (ROOT / "docs" / "plans" / "roadmap.md").read_text(encoding="utf-8")

        # README.md v1.3 workflow, genre, detector, and prior-art coverage
        readme_lower = readme_text.lower()
        for token in (
            "3-way edit triage",
            "Leave-it-alone",
            "cold-reader",
            "postmortems",
            "changelogs and release notes",
            "3P updates",
            "thread reply discipline",
            "chatbot_artifacts",
            "meta_and_strawman_tells",
            "U+2013",
            "blader/humanizer",
            "Signs of AI Writing",
            "anthropics/skills",
            "coreyhaines31/marketingskills",
            "vidanov/writing-craft-skill",
        ):
            self.assertIn(token.lower(), readme_lower, f"README.md missing v1.3 token: {token}")

        # AGENTS.md v1.3 reference and detector sync
        agents_lower = agents_text.lower()
        for token in (
            "3-way edit triage",
            "leave-it-alone",
            "cold-reader",
            "postmortems",
            "release notes",
            "3p updates",
            "thread reply discipline",
            "chatbot_artifacts",
            "meta_and_strawman_tells",
        ):
            self.assertIn(token, agents_lower, f"AGENTS.md missing v1.3 token: {token}")

        # CHANGELOG.md v1.3 additions
        changelog_lower = changelog_text.lower()
        for token in (
            "leave-it-alone",
            "cold-reader",
            "postmortem",
            "keep-a-changelog",
            "3p",
            "context-rebuilding",
            "chatbot_artifacts",
            "meta_and_strawman_tells",
        ):
            self.assertIn(token, changelog_lower, f"CHANGELOG.md missing v1.3 token: {token}")

        # docs/plans/roadmap.md Tasks 017..020
        for task_heading in (
            "**Task 017:**",
            "**Task 018:**",
            "**Task 019:**",
            "**Task 020:**",
        ):
            self.assertIn(task_heading, roadmap_text, f"roadmap.md missing {task_heading}")

        # Strict prose hygiene across all 4 updated Markdown docs
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
            for tell_key in ALL_TELL_LIST_KEYS:
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

    def test_tc_020_03_all_tell_list_keys_sync_word_budget_and_clean_package(self) -> None:
        """TC-020-03 (REQ-020-03): ALL_TELL_LIST_KEYS synced across tests/, runtime <= 10,000w, lint + fitness + package_skill --check pass."""
        live_mech = prose_lint.analyze_text("Check exit code 0 on Linux.")["mechanics_and_tells"]
        expected_list_keys = {k for k, v in live_mech.items() if isinstance(v, list)}
        self.assertIn("chatbot_artifacts", expected_list_keys)
        self.assertIn("meta_and_strawman_tells", expected_list_keys)

        for mod_name, keys_tuple in (
            ("test_task_010", test_task_010_memo_samples_and_sync.ALL_TELL_LIST_KEYS),
            ("test_task_014", test_task_014_clean_packaging.ALL_TELL_LIST_KEYS),
            ("test_task_015", test_task_015_cli_safety_and_models.ALL_TELL_LIST_KEYS),
            ("test_task_016", test_task_016_doc_and_diagram_sync.ALL_TELL_LIST_KEYS),
            ("test_task_020", ALL_TELL_LIST_KEYS),
        ):
            self.assertIn(
                "chatbot_artifacts",
                keys_tuple,
                f"{mod_name}.ALL_TELL_LIST_KEYS missing chatbot_artifacts",
            )
            self.assertIn(
                "meta_and_strawman_tells",
                keys_tuple,
                f"{mod_name}.ALL_TELL_LIST_KEYS missing meta_and_strawman_tells",
            )
            self.assertEqual(
                set(keys_tuple),
                expected_list_keys,
                f"{mod_name}.ALL_TELL_LIST_KEYS out of sync with prose_lint list keys",
            )

        val_res = validate_skill.validate_repo(ROOT)
        self.assertTrue(val_res["passed"], f"validate_skill failed: {val_res['errors']}")
        self.assertLessEqual(
            val_res["word_counts"]["combined_runtime"],
            10000,
            f"Combined runtime words {val_res['word_counts']['combined_runtime']} exceed 10,000 budget",
        )
        self.assertEqual(validate_skill.COMBINED_MAX_WORDS, 10000)

        lint_proc = _run_cmd(["make", "lint"])
        self.assertEqual(lint_proc.returncode, 0, lint_proc.stdout + lint_proc.stderr)

        fitness_proc = _run_cmd(["make", "fitness"])
        self.assertEqual(fitness_proc.returncode, 0, fitness_proc.stdout + fitness_proc.stderr)
        for fid in ("F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"):
            self.assertIn(fid, fitness_proc.stdout)
        self.assertIn("All fitness checks passed.", fitness_proc.stdout)

        pkg_proc = _run_cmd([sys.executable, "scripts/package_skill.py", "--check", "--json"])
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
