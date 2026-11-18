"""Verification tests for Task 010: Memo Calibration Samples, Evals, and Documentation Sync.

Covers TC-010-01 through TC-010-03 from
docs/tasks/test-specs/010-memo-samples-evals-and-docs-sync-test-spec.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT / "samples"
EVALS_DIR = ROOT / "evals"
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
    "mixed_dialects",
)

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _run_cmd(args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
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


class TestTask010MemoSamplesAndSync(unittest.TestCase):
    """Covers TC-010-01 through TC-010-03."""

    def test_tc_010_01_one_pager_calibration_pair_and_prose_lint_deltas(self) -> None:
        """TC-010-01 (REQ-010-01): one-pager.before.md triggers flourish/mech tells; one-pager.after.md has zero tells and higher anchors."""
        before_path = SAMPLES_DIR / "one-pager.before.md"
        after_path = SAMPLES_DIR / "one-pager.after.md"
        samples_readme_path = SAMPLES_DIR / "README.md"

        self.assertTrue(before_path.is_file(), f"Missing {before_path}")
        self.assertTrue(after_path.is_file(), f"Missing {after_path}")
        self.assertTrue(samples_readme_path.is_file(), f"Missing {samples_readme_path}")

        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        self.assertIn("one-pager.before.md", samples_readme)
        self.assertIn("one-pager.after.md", samples_readme)
        self.assertNotIn(EM_DASH, _strip_fenced_blocks(samples_readme))

        after_text = after_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, after_text, "one-pager.after.md must contain zero em dashes")

        raw_words = len(after_text.split())
        self.assertGreaterEqual(raw_words, 350, f"one-pager.after.md too short ({raw_words}w)")
        self.assertLessEqual(raw_words, 550, f"one-pager.after.md exceeds 550w ceiling ({raw_words}w)")

        # Run prose_lint.py --json on the pair
        json_proc = _run_cmd(
            [
                sys.executable,
                "scripts/prose_lint.py",
                "--json",
                "samples/one-pager.before.md",
                "samples/one-pager.after.md",
            ]
        )
        self.assertEqual(json_proc.returncode, 0, json_proc.stderr)
        before_rep, after_rep = json.loads(json_proc.stdout)

        self.assertGreaterEqual(after_rep["word_count"], 350)
        self.assertLessEqual(after_rep["word_count"], 550)

        # Verify .before.md intentionally triggers mechanical and flourish detectors
        before_mech = before_rep["mechanics_and_tells"]
        before_sub = before_rep["substance_and_posture"]
        for required_tell in (
            "em_dashes",
            "bold_restatement_bullets",
            "emoji_bullets",
            "ai_tell_words",
            "inflated_style_verbs",
            "tech_buzz_nouns",
            "framing_theater",
            "contrastive_pivots",
            "participial_tail_puffery",
            "copula_avoidance",
            "rhetorical_qa_pivots",
            "performative_fragments",
        ):
            self.assertGreater(
                len(before_mech[required_tell]),
                0,
                f"one-pager.before.md must trigger {required_tell}",
            )
        self.assertGreater(before_mech["nominalizations_per_100w"], 0.0)
        imp_triggers = {
            item["trigger"] for item in before_sub["importance_without_mechanism"]
        }
        self.assertIn(
            "without sacrificing",
            imp_triggers,
            f"Expected 'without sacrificing' in importance_without_mechanism, got {imp_triggers}",
        )

        # Verify .after.md achieves [] across every tell list and Findings: none
        after_mech = after_rep["mechanics_and_tells"]
        after_sub = after_rep["substance_and_posture"]
        for tell_key in ALL_TELL_LIST_KEYS:
            self.assertEqual(
                after_mech[tell_key],
                [],
                f"one-pager.after.md must have empty {tell_key}, got {after_mech[tell_key]}",
            )
        self.assertEqual(after_sub["importance_without_mechanism"], [])
        self.assertEqual(after_sub["hedge_booster_collisions"], [])
        self.assertEqual(after_rep["cadence"]["overloaded_sentences"], [])
        self.assertEqual(after_rep["lexical_diversity"]["repeated_trigrams"], [])

        human_proc = _run_cmd(
            [sys.executable, "scripts/prose_lint.py", "samples/one-pager.after.md"]
        )
        self.assertEqual(human_proc.returncode, 0, human_proc.stderr)
        self.assertIn("Findings: none", human_proc.stdout)

        # Verify higher anchor density on .after.md than .before.md
        self.assertGreater(
            after_sub["anchors_per_100w"],
            before_sub["anchors_per_100w"],
            (
                f"Expected one-pager.after.md anchors_per_100w ({after_sub['anchors_per_100w']}) "
                f"> one-pager.before.md ({before_sub['anchors_per_100w']})"
            ),
        )

        # Verify 5-section One-Pager blueprint in order + <100-word baseline + Status Quo + kill switch
        required_sections = [
            "BLUF / Decision Call",
            "Problem and Customer/System Baseline",
            "Scope and Explicit Non-Goals",
            "Viable Options and Tradeoffs",
            "Risks, Kill Switch, and Owned Next Steps",
        ]
        positions = [after_text.find(sec) for sec in required_sections]
        for sec, pos in zip(required_sections, positions):
            self.assertNotEqual(pos, -1, f"Missing One-Pager section in after sample: {sec}")
        self.assertEqual(
            positions,
            sorted(positions),
            "5-section One-Pager headings must appear in sequential order",
        )

        baseline_match = re.search(
            r"##\s*2\.\s*Problem and Customer/System Baseline\s*\n+(.+?)(?=\n##\s*3\.)",
            after_text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(baseline_match, "Could not extract Section 2 baseline body")
        baseline_words = len(baseline_match.group(1).split()) if baseline_match else 999
        self.assertLess(
            baseline_words,
            100,
            f"One-Pager Section 2 baseline must stay under 100 words, got {baseline_words}w",
        )

        for domain_anchor in (
            "Director of Merchant Platform",
            "October 8",
            "14,200",
            "68",
            "POST /v1/webhooks/replays",
            "50 RPS",
            "Option A",
            "Option B",
            "Status Quo",
            "webhooks.self_serve_replay=false",
            "[TK:",
        ):
            self.assertIn(domain_anchor, after_text)

    def test_tc_010_02_evals_and_trigger_evals_memo_and_flourish_coverage(self) -> None:
        """TC-010-02 (REQ-010-02): evals/evals.json >=18 cases and evals/trigger-evals.json >=28 balanced queries."""
        evals_path = EVALS_DIR / "evals.json"
        triggers_path = EVALS_DIR / "trigger-evals.json"

        raw_evals = evals_path.read_text(encoding="utf-8")
        raw_triggers = triggers_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, raw_evals, "evals/evals.json must not contain literal em dashes")
        self.assertNotIn(
            EM_DASH,
            raw_triggers,
            "evals/trigger-evals.json must not contain literal em dashes",
        )

        evals_payload = json.loads(raw_evals)
        evals = evals_payload["evals"]
        self.assertGreaterEqual(len(evals), 18, f"Expected >= 18 eval cases, got {len(evals)}")

        seen_ids: set[int] = set()
        seen_names: set[str] = set()
        for item in evals:
            self.assertNotIn(item["id"], seen_ids)
            seen_ids.add(item["id"])
            self.assertNotIn(item["eval_name"], seen_names)
            seen_names.add(item["eval_name"])
            for rel_file in item.get("files", []):
                self.assertTrue(
                    (ROOT / rel_file).is_file(),
                    f"Eval {item['id']} references missing file {rel_file}",
                )

        # Verify specific new behavioral cases exist for door-type, six-pager tenets/appendix, and anti-flourish restraint
        has_door_type_case = any(
            "type 2" in json.dumps(item).lower()
            and "two-way door" in json.dumps(item).lower()
            and "ceiling" in json.dumps(item).lower()
            and "one-pager" in json.dumps(item).lower()
            for item in evals
        )
        self.assertTrue(
            has_door_type_case,
            "evals.json missing One-Pager vs Six-Pager door-type and ceiling-not-quota case",
        )

        has_six_pager_case = any(
            "six-pager" in json.dumps(item).lower()
            and "sacrifice" in json.dumps(item).lower()
            and "input metrics" in json.dumps(item).lower()
            and "appendix" in json.dumps(item).lower()
            for item in evals
        )
        self.assertTrue(
            has_six_pager_case,
            "evals.json missing Six-Pager sacrifice-bearing Tenets and two-way Appendix contract case",
        )

        has_anti_flourish_restraint_case = any(
            item["category"] in {"false_positive_restraint", "medium_fit"}
            and "serves as a cornerstone" in json.dumps(item).lower()
            and "the result?" in json.dumps(item).lower()
            and "without sacrificing" in json.dumps(item).lower()
            and "parenthetical" in json.dumps(item).lower()
            for item in evals
        )
        self.assertTrue(
            has_anti_flourish_restraint_case,
            "evals.json missing anti-flourish editing + concrete mechanism/parenthetical restraint case",
        )

        # Verify trigger-evals.json balance and new triggers
        triggers = json.loads(raw_triggers)
        self.assertGreaterEqual(
            len(triggers),
            28,
            f"Expected >= 28 trigger queries, got {len(triggers)}",
        )
        pos_queries = [t["query"] for t in triggers if t["should_trigger"] is True]
        neg_queries = [t["query"] for t in triggers if t["should_trigger"] is False]
        self.assertGreaterEqual(len(pos_queries), 14)
        self.assertGreaterEqual(len(neg_queries), 14)
        self.assertEqual(
            len(pos_queries),
            len(neg_queries),
            f"Expected balanced positive/negative trigger queries, got {len(pos_queries)} vs {len(neg_queries)}",
        )

        pos_blob = " ".join(pos_queries).lower()
        self.assertIn("one-pager", pos_blob)
        self.assertIn("six-pager", pos_blob)
        self.assertIn("pr/faq", pos_blob)
        self.assertIn("serves as a cornerstone", pos_blob)

    def test_tc_010_03_docs_sync_package_validation_and_fitness(self) -> None:
        """TC-010-03 (REQ-010-03): README, AGENTS, CHANGELOG, roadmap, validate_skill.py, and make fitness all sync cleanly."""
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        roadmap_text = (ROOT / "docs" / "plans" / "roadmap.md").read_text(encoding="utf-8")

        for doc_name, doc_text in (
            ("README.md", readme_text),
            ("AGENTS.md", agents_text),
            ("CHANGELOG.md", changelog_text),
            ("docs/plans/roadmap.md", roadmap_text),
        ):
            self.assertIn(
                "one-pager-and-six-pager.md",
                doc_text,
                f"{doc_name} must reference one-pager-and-six-pager.md",
            )
            self.assertIn("one-pager", doc_text.lower(), f"{doc_name} must reference one-pager")
            self.assertIn("10,000", doc_text, f"{doc_name} must reference 10,000-word combined budget")

        for flourish_key in (
            "participial_tail_puffery",
            "copula_avoidance",
            "rhetorical_qa_pivots",
            "performative_fragments",
            "nominalizations_per_100w",
        ):
            self.assertIn(flourish_key, readme_text, f"README.md missing {flourish_key}")
            self.assertIn(flourish_key, changelog_text, f"CHANGELOG.md missing {flourish_key}")

        self.assertIn("samples/one-pager.before.md", readme_text)
        self.assertIn("samples/one-pager.after.md", readme_text)

        # Mermaid check on README.md and docs/
        mermaid_proc = _run_cmd([sys.executable, "scripts/check-mermaid.py"])
        self.assertEqual(mermaid_proc.returncode, 0, mermaid_proc.stdout + mermaid_proc.stderr)

        # validate_skill.py --json
        val_proc = _run_cmd([sys.executable, "scripts/validate_skill.py", "--json"])
        self.assertEqual(val_proc.returncode, 0, val_proc.stdout + val_proc.stderr)
        val_report = json.loads(val_proc.stdout)
        self.assertTrue(val_report["passed"], val_report["errors"])
        self.assertEqual(val_report["errors"], [])
        self.assertLessEqual(val_report["word_counts"]["combined_runtime"], 10000)

        # Zero-tell prose hygiene across all authored Markdown files
        authored_files = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "CHANGELOG.md",
            ROOT / "docs" / "plans" / "roadmap.md",
            ROOT / "samples" / "README.md",
            ROOT / "evals" / "JUDGE.md",
            *sorted((ROOT / "references").glob("*.md")),
            *sorted((ROOT / "samples").glob("*.after.md")),
        ]
        for path in authored_files:
            raw_md = path.read_text(encoding="utf-8")
            non_fenced = _strip_fenced_blocks(raw_md)
            self.assertNotIn(
                EM_DASH,
                non_fenced,
                f"{path.relative_to(ROOT)} contains prohibited em dash outside code fences",
            )
            lines = non_fenced.splitlines()
            for idx, line in enumerate(lines, start=1):
                if LIST_ITEM_RE.match(line) and idx > 1:
                    prev = lines[idx - 2]
                    self.assertTrue(
                        prev.strip() == "" or bool(LIST_ITEM_RE.match(prev)),
                        f"{path.relative_to(ROOT)}:{idx} starts list without preceding blank line",
                    )

            rep = prose_lint.analyze_text(raw_md, source=path.relative_to(ROOT).as_posix())
            for tell_key in ALL_TELL_LIST_KEYS:
                if tell_key == "stacked_questions" and path.name == "draft-and-brief.md":
                    # draft-and-brief.md intentionally lists the 5 perspective interview questions.
                    continue
                self.assertEqual(
                    rep["mechanics_and_tells"][tell_key],
                    [],
                    f"{path.name} has unexpected {tell_key}: {rep['mechanics_and_tells'][tell_key]}",
                )
            self.assertEqual(
                rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{path.name} has unexpected importance_without_mechanism",
            )

        # Ensure this test file itself contains zero literal em dashes
        self_text = Path(__file__).resolve().read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, self_text)

        # Run make lint and make fitness end-to-end
        lint_proc = _run_cmd(["make", "lint"])
        self.assertEqual(lint_proc.returncode, 0, lint_proc.stdout + lint_proc.stderr)
        fitness_proc = _run_cmd(["make", "fitness"])
        self.assertEqual(fitness_proc.returncode, 0, fitness_proc.stdout + fitness_proc.stderr)
        self.assertIn("All fitness checks passed.", fitness_proc.stdout)


if __name__ == "__main__":
    unittest.main()
