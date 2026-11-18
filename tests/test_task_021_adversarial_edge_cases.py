"""Unit and integration tests for Task 021: prose_lint.py edge cases and mixed_dialects.

Covers TC-021-01 through TC-021-03 from
docs/tasks/test-specs/021-prose-lint-edge-cases-and-mixed-dialects-test-spec.md.
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
    test_task_020_v13_evals_and_docs,
)

ROOT = Path(__file__).resolve().parent.parent
LINT_CLI = ROOT / "scripts" / "prose_lint.py"
EM_DASH = "\u2014"
EN_DASH = "\u2013"


def _run_lint_cli(
    *args: str, stdin_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINT_CLI), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def _collect_all_keys(obj: object) -> list[str]:
    keys: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(str(k))
            keys.extend(_collect_all_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(_collect_all_keys(item))
    return keys


class TestTask021AdversarialEdgeCases(unittest.TestCase):
    """Verification suite for REQ-021-01..REQ-021-03 (TC-021-01..TC-021-03)."""

    def test_tc_021_01_technical_profile_excludes_bold_conceptual_enumerations(
        self,
    ) -> None:
        """TC-021-01: --profile technical skips bold-labeled conceptual enumerations while flagging >20w procedural steps."""
        repo_tech_targets = (
            "README.md",
            "SKILL.md",
            "CONTRIBUTING.md",
            "references/technical-and-docs.md",
            "samples/technical-doc.after.md",
        )
        for rel in repo_tech_targets:
            target_path = ROOT / rel
            self.assertTrue(target_path.is_file(), f"Missing target file: {rel}")
            rep = prose_lint.analyze_text(
                target_path.read_text(encoding="utf-8"),
                source=rel,
                profile="technical",
            )
            pc = rep["profile_checks"]
            self.assertEqual(
                pc["overlong_steps"],
                [],
                f"{rel} triggered false-positive overlong_steps: {pc['overlong_steps']}",
            )
            self.assertEqual(pc["date_time_issues"], [])
            self.assertTrue(pc["passed"], f"{rel} failed technical profile: {pc}")

        # Verify CLI --profile technical README.md (JSON and human output)
        cli_json_proc = _run_lint_cli("--profile", "technical", "README.md", "--json")
        self.assertEqual(cli_json_proc.returncode, 0, cli_json_proc.stderr)
        cli_readme_rep = json.loads(cli_json_proc.stdout)
        self.assertEqual(cli_readme_rep["profile_checks"]["overlong_steps"], [])
        self.assertTrue(cli_readme_rep["profile_checks"]["passed"])

        cli_human_proc = _run_lint_cli("--profile", "technical", "README.md")
        self.assertEqual(cli_human_proc.returncode, 0, cli_human_proc.stderr)
        self.assertIn("Profile (technical): PASS", cli_human_proc.stdout)
        self.assertNotIn("[overlong_step]", cli_human_proc.stdout)

        # Synthetic conceptual enumerations with bold title labels stay exempt
        conceptual_md = (
            "# Design Principles\n\n"
            "1. **Truth, claim strength, and attribution preservation.** Never invent facts, "
            "quotes, citations, benchmarks, dates, or customer names when source context is incomplete.\n"
            "2. **BLUF:** State the decision, owner, deadline, and expected latency impact in "
            "sentence one before expanding background context or alternative designs.\n"
            "3. **Scope**: Keep all configuration schema edits isolated to the regional worker "
            "pool so ingress proxies never reload active TLS certificates.\n"
            "4. **Fallback** - Drain one canary replica first, monitor HTTP 5xx rates for ten "
            "minutes, and abort immediately if queue depth doubles.\n"
            "5. **Explicit `[TK]` placeholders.** Insert `[TK: specific question]` whenever "
            "concrete numbers, dates, or owners are missing from the author's notes.\n"
        )
        concept_rep = prose_lint.analyze_text(
            conceptual_md, source="concepts.md", profile="technical"
        )
        self.assertEqual(concept_rep["profile_checks"]["overlong_steps"], [])
        self.assertTrue(concept_rep["profile_checks"]["passed"])

        # Bare >20-word procedural steps and unpunctuated bold-verb steps still flag
        procedural_md = (
            "# Rollout Runbook\n\n"
            "1. Open the regional staging console, inspect every active worker lease, verify "
            "all pending migration rows, and confirm zero errors before promoting traffic.\n"
            "2. **Click** the regional staging console button, inspect every active worker lease, "
            "verify all pending migration rows, and confirm zero errors before promoting traffic.\n"
            "3. Run `deploy.sh` and check HTTP 200.\n"
        )
        proc_rep = prose_lint.analyze_text(
            procedural_md, source="runbook.md", profile="technical"
        )
        proc_pc = proc_rep["profile_checks"]
        self.assertFalse(proc_pc["passed"])
        self.assertEqual(len(proc_pc["overlong_steps"]), 2)
        self.assertEqual([item["line"] for item in proc_pc["overlong_steps"]], [3, 4])
        for item in proc_pc["overlong_steps"]:
            self.assertGreater(item["words"], 20)
        self.assertIn("[overlong_step]", prose_lint.format_human_report(proc_rep))

    def test_tc_021_02_twelve_hour_time_period_and_meta_strawman_gaps(self) -> None:
        """TC-021-02: _TWELVE_HOUR_TIME_RE excludes sentence-ending period and _META_AND_STRAWMAN_TELLS_RE closes 3 gaps."""
        sentence_end_rep = prose_lint.analyze_text(
            "We shipped 10/18/2026 at 3:30 PM.",
            source="ship.md",
            profile="technical",
        )
        dt_hits = sentence_end_rep["profile_checks"]["date_time_issues"]
        self.assertEqual([h["match"] for h in dt_hits], ["10/18/2026", "3:30 PM"])

        dotted_abbrev_rep = prose_lint.analyze_text(
            "Schedule the window at 3:30 p.m. and verify logs at 9:15 a.m.",
            source="window.md",
            profile="technical",
        )
        abbrev_hits = dotted_abbrev_rep["profile_checks"]["date_time_issues"]
        self.assertEqual([h["match"] for h in abbrev_hits], ["3:30 p.m.", "9:15 a.m."])

        # Quote and inline-code immunity for 12-hour clock times
        immune_dt_rep = prose_lint.analyze_text(
            'Ignore `"3:30 PM"`, `3:30 PM.`, and "We met at 3:30 PM." in literal examples.',
            source="immune_dt.md",
            profile="technical",
        )
        self.assertEqual(immune_dt_rep["profile_checks"]["date_time_issues"], [])

        # _META_AND_STRAWMAN_TELLS_RE gap closures
        meta_fixture = (
            "I'm not saying we should rewrite it.\n\n"
            "I\u2019m not saying the cache is broken, and I am not saying retries are free.\n\n"
            "This isn't about speed, it's about reliability.\n\n"
            "This is not really about latency, it is about durability.\n\n"
            "No fluff. No filler. No jargon.\n\n"
            "No lock-in; no hidden tiers; no surprise overages.\n"
        )
        meta_rep = prose_lint.analyze_text(meta_fixture, source="meta_gaps.md")
        meta_hits = meta_rep["mechanics_and_tells"]["meta_and_strawman_tells"]
        hit_lines = [h["line"] for h in meta_hits]
        for expected_line in (1, 3, 5, 7, 9, 11):
            self.assertIn(
                expected_line,
                hit_lines,
                f"Expected line {expected_line} to trigger meta_and_strawman_tells, got {meta_hits}",
            )

        matches_blob = " | ".join(h["match"] for h in meta_hits)
        self.assertIn("i'm not saying", matches_blob)
        self.assertIn("i am not saying", matches_blob)
        self.assertIn("this isn't about", matches_blob)
        self.assertIn("this is not really about", matches_blob)
        self.assertIn("no fluff. no filler. no jargon", matches_blob)
        self.assertIn("no lock-in; no hidden tiers; no surprise", matches_blob)

        # Quote/code immunity and non-strawman 2-part negation restraint
        clean_meta_fixture = (
            'Quote "I\'m not saying we should rewrite it." and `No fluff. No filler. No jargon.` safely.\n\n'
            'Quote "This isn\'t about speed, it\'s about reliability." as an anti-pattern.\n\n'
            "No data loss and no downtime occurred during the regional shard failover.\n"
        )
        clean_meta_rep = prose_lint.analyze_text(
            clean_meta_fixture, source="clean_meta.md"
        )
        self.assertEqual(
            clean_meta_rep["mechanics_and_tells"]["meta_and_strawman_tells"], []
        )

    def test_tc_021_03_mixed_dialects_detector_restraint_and_repo_sweep(self) -> None:
        """TC-021-03: mixed_dialects flags US/UK mixes, ignores code/CLI/quotes, and returns [] across all clean repo Markdown files."""
        mixed_text = (
            "The organisation optimized color rendering while we analysed the behavior in our centre.\n"
        )
        mixed_rep = prose_lint.analyze_text(mixed_text, source="mixed.md")
        mech = mixed_rep["mechanics_and_tells"]
        self.assertIn("mixed_dialects", mech)
        hits = mech["mixed_dialects"]
        self.assertEqual(len(hits), 3, f"Expected 3 minority-dialect hits, got {hits}")

        expected_item_keys = {
            "line",
            "match",
            "dialect",
            "dominant_dialect",
            "us_samples",
            "uk_samples",
            "excerpt",
        }
        for item in hits:
            self.assertEqual(set(item.keys()), expected_item_keys)
            self.assertEqual(item["line"], 1)
            self.assertEqual(item["dominant_dialect"], "en-US")
            self.assertEqual(item["dialect"], "en-GB")
        self.assertEqual(
            [item["match"] for item in hits],
            ["organisation", "analysed", "centre"],
        )
        self.assertEqual(hits[0]["us_samples"], ["optimized", "color", "behavior"])
        self.assertEqual(hits[0]["uk_samples"], ["organisation", "analysed", "centre"])

        # Human formatter and CLI JSON output
        human_report = prose_lint.format_human_report(mixed_rep)
        self.assertIn("[mixed_dialects]", human_report)

        cli_proc = _run_lint_cli("--json", stdin_text=mixed_text)
        self.assertEqual(cli_proc.returncode, 0, cli_proc.stderr)
        cli_json = json.loads(cli_proc.stdout)
        self.assertEqual(cli_json["mechanics_and_tells"]["mixed_dialects"], hits)

        # Verify UK-dominant document emits minority en-US occurrences
        uk_dominant_text = (
            "The organisation optimised colour rendering while we analysed the behaviour in our centre, "
            "except for one gray status badge.\n"
        )
        uk_dom_rep = prose_lint.analyze_text(uk_dominant_text, source="uk_dom.md")
        uk_dom_hits = uk_dom_rep["mechanics_and_tells"]["mixed_dialects"]
        self.assertEqual(len(uk_dom_hits), 1)
        self.assertEqual(uk_dom_hits[0]["match"], "gray")
        self.assertEqual(uk_dom_hits[0]["dialect"], "en-US")
        self.assertEqual(uk_dom_hits[0]["dominant_dialect"], "en-GB")

        # Pure en-US, pure en-GB, and en-GB with CLI flags, identifiers, quotes, URLs, and cross-dialect tech nouns
        pure_us = (
            "The organization optimized color rendering while we analyzed the behavior in our center "
            "and cataloged gray artifacts.\n"
        )
        pure_uk = (
            "The organisation optimised colour rendering while we analysed the behaviour in our centre "
            "and catalogued grey artefacts.\n"
        )
        uk_with_code_and_identifiers = (
            "Pass `--color`, set `organization_id`, or open \"Color Picker\" and \u201cBehavior Center\u201d "
            "in the centre to customise the behaviour of grey artefacts.\n\n"
            "Flags like --color, env keys like organization_id, and URLs like "
            "https://example.com/organization/color stay untouched while our organisation analyses "
            "the disk program and latency meter under a standard license.\n\n"
            "```python\n"
            'organization_color = "gray"\n'
            "```\n"
        )
        for label, sample in (
            ("pure_us", pure_us),
            ("pure_uk", pure_uk),
            ("uk_with_code", uk_with_code_and_identifiers),
        ):
            rep = prose_lint.analyze_text(sample, source=f"{label}.md")
            self.assertEqual(
                rep["mechanics_and_tells"]["mixed_dialects"],
                [],
                f"{label} triggered false positive mixed_dialects: {rep['mechanics_and_tells']['mixed_dialects']}",
            )

        # Hard invariant: zero composite AI detector score keys anywhere
        banned_substrings = (
            "score",
            "detector",
            "probability",
            "slop_index",
            "ai_likelihood",
            "human_rating",
        )
        for key_name in _collect_all_keys(mixed_rep):
            for banned in banned_substrings:
                self.assertNotIn(banned, key_name.lower())

        # Spec synchronization and prose hygiene on data-model.md and behaviors.md
        data_model_path = ROOT / "docs" / "spec" / "data-model.md"
        behaviors_path = ROOT / "docs" / "spec" / "behaviors.md"
        data_model_text = data_model_path.read_text(encoding="utf-8")
        behaviors_text = behaviors_path.read_text(encoding="utf-8")

        self.assertIn('"mixed_dialects"', data_model_text)
        self.assertIn("mixed_dialects", behaviors_text)

        json_blocks = re.findall(
            r"```json\n(.*?)\n```", data_model_text, flags=re.DOTALL
        )
        self.assertGreaterEqual(len(json_blocks), 2)
        schema_example = json.loads(json_blocks[1])
        live_mech = prose_lint.analyze_text("Check exit code 0 on Linux.")[
            "mechanics_and_tells"
        ]
        self.assertEqual(
            set(schema_example["mechanics_and_tells"].keys()),
            set(live_mech.keys()),
        )

        # Verify ALL_TELL_LIST_KEYS synchronization across test modules
        expected_list_keys = {k for k, v in live_mech.items() if isinstance(v, list)}
        self.assertIn("mixed_dialects", expected_list_keys)
        for mod_name, keys_tuple in (
            ("test_task_010", test_task_010_memo_samples_and_sync.ALL_TELL_LIST_KEYS),
            ("test_task_014", test_task_014_clean_packaging.ALL_TELL_LIST_KEYS),
            ("test_task_015", test_task_015_cli_safety_and_models.ALL_TELL_LIST_KEYS),
            ("test_task_016", test_task_016_doc_and_diagram_sync.ALL_TELL_LIST_KEYS),
            ("test_task_020", test_task_020_v13_evals_and_docs.ALL_TELL_LIST_KEYS),
        ):
            self.assertIn(
                "mixed_dialects",
                keys_tuple,
                f"{mod_name}.ALL_TELL_LIST_KEYS missing mixed_dialects",
            )
            self.assertEqual(set(keys_tuple), expected_list_keys)

        # Sweep all clean repository Markdown files
        sweep_files: list[Path] = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "CLAUDE.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "CHANGELOG.md",
            *sorted((ROOT / "commands").glob("*.md")),
            *sorted((ROOT / "references").glob("*.md")),
            *sorted((ROOT / "samples").glob("*.after.md")),
            *sorted((ROOT / "docs" / "spec").glob("*.md")),
            *sorted((ROOT / "docs" / "architecture").glob("*.md")),
            ROOT / "evals" / "JUDGE.md",
        ]
        seen = {p.resolve() for p in sweep_files}
        for extra in validate_skill._collect_prose_hygiene_files(ROOT):
            if extra.resolve() not in seen:
                seen.add(extra.resolve())
                sweep_files.append(extra)

        self.assertGreaterEqual(len(sweep_files), 28)
        for md_path in sweep_files:
            self.assertTrue(md_path.is_file(), f"Missing repo file: {md_path}")
            rel = md_path.relative_to(ROOT).as_posix()
            rep = prose_lint.analyze_text(
                md_path.read_text(encoding="utf-8"), source=rel
            )
            self.assertEqual(
                rep["mechanics_and_tells"]["mixed_dialects"],
                [],
                f"{rel} triggered false-positive mixed_dialects: {rep['mechanics_and_tells']['mixed_dialects']}",
            )

        # Spec files must stay <=35 words per sentence with zero literal em dashes or tells
        for spec_path in (data_model_path, behaviors_path):
            raw_spec = spec_path.read_text(encoding="utf-8")
            self.assertNotIn(EM_DASH, raw_spec)
            self.assertNotIn(EN_DASH, raw_spec)
            spec_rep = prose_lint.analyze_text(raw_spec, source=spec_path.name)
            self.assertEqual(
                spec_rep["cadence"]["overloaded_sentences"],
                [],
                f"{spec_path.name} has overloaded sentences: {spec_rep['cadence']['overloaded_sentences']}",
            )
            for k in expected_list_keys:
                self.assertEqual(
                    spec_rep["mechanics_and_tells"][k],
                    [],
                    f"{spec_path.name} triggered {k}: {spec_rep['mechanics_and_tells'][k]}",
                )

        # Zero literal em dashes in modified Python files
        for py_path in (
            LINT_CLI,
            ROOT / "tests" / "test_task_004_prose_lint.py",
            Path(__file__).resolve(),
        ):
            raw_py = py_path.read_text(encoding="utf-8")
            self.assertNotIn(EM_DASH, raw_py, f"Literal em dash in {py_path.name}")
            self.assertNotIn(EN_DASH, raw_py, f"Literal en dash in {py_path.name}")


if __name__ == "__main__":
    unittest.main()
