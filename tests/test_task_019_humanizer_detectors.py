"""Unit and integration tests for Task 019: dash-bypass and humanizer detectors.

Covers TC-019-01 through TC-019-03 from
docs/tasks/test-specs/019-prose-lint-humanizer-and-dash-bypass-detectors-test-spec.md.
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


class TestTask019HumanizerAndDashBypassDetectors(unittest.TestCase):
    """Verification suite for REQ-019-01..REQ-019-03 (TC-019-01..TC-019-03)."""

    def test_tc_019_01_spaced_double_hyphen_and_en_dash_bypass_detection(self) -> None:
        """TC-019-01: em_dashes flags spaced -- and spaced U+2013 alongside U+2014 while ignoring safe syntax."""
        positive_fixture = (
            "The ingress proxy caches TLS sessions -- cutting handshake latency by 40%.\n\n"
            f"The worker validates HMAC digests {EN_DASH} rejecting unsigned payloads.\n\n"
            ' Inspect the queue depth, -- "hot shard" -- (shard 4) before draining.\n\n'
            f"Combine literal{EM_DASH}dash, spaced -- hyphen, and spaced {EN_DASH} en-dash.\n"
        )
        pos_rep = prose_lint.analyze_text(positive_fixture, source="dash_positive.md")
        hits = pos_rep["mechanics_and_tells"]["em_dashes"]

        self.assertEqual([h["line"] for h in hits], [1, 3, 5, 7])
        self.assertEqual([h["count"] for h in hits], [1, 1, 2, 3])

        human_out = prose_lint.format_human_report(pos_rep)
        self.assertIn("[em_dash]", human_out)

        immune_fixture = (
            "---\n"
            "title: Dash Immunity Check\n"
            f"summary: Frontmatter with -- and {EN_DASH} and {EM_DASH}\n"
            "---\n\n"
            "# Safe Syntax Check\n\n"
            "Secondary Heading\n"
            "-----------------\n\n"
            "---\n\n"
            f"<!-- HTML comment with word -- word and word {EN_DASH} word -->\n\n"
            "Pass --profile technical or --install-to /tmp/skill when running the CLI.\n\n"
            "Run `git checkout -- path`, `word -- word`, "
            f"`word {EN_DASH} word`, and `` `git checkout -- path` `` safely.\n\n"
            f"Check ports 8000-8080, pages 14{EN_DASH}18, and 2{EN_DASH}3 replicas.\n\n"
            "| Flag | Meaning |\n"
            "|------|---------|\n"
            f"| --profile | Mode -- or {EN_DASH} inside table cell |\n\n"
            "Column A | Column B\n"
            "--- | ---\n"
            "alpha | beta\n\n"
            "```bash\n"
            "git checkout -- README.md\n"
            f'echo "fenced -- and {EN_DASH} and {EM_DASH}"\n'
            "```\n\n"
            "~~~text\n"
            f"tilde fenced -- and {EN_DASH}\n"
            "~~~\n"
        )
        immune_rep = prose_lint.analyze_text(immune_fixture, source="dash_immune.md")
        self.assertEqual(
            immune_rep["mechanics_and_tells"]["em_dashes"],
            [],
            f"Unexpected em_dashes false positive: {immune_rep['mechanics_and_tells']['em_dashes']}",
        )

    def test_tc_019_02_chatbot_artifacts_and_meta_strawman_detectors(self) -> None:
        """TC-019-02: chatbot_artifacts and meta_and_strawman_tells fire accurately with quote/code immunity and zero score."""
        slop_fixture = (
            "Great question. Verify the webhook signature before parsing JSON.\n\n"
            "Certainly, here is the updated timeout table.\n\n"
            "Of course, the worker retries transient HTTP 503 responses.\n\n"
            "Sure thing. Drain one replica before upgrading the kernel.\n\n"
            "I hope this helps clarify the lease renewal interval. Happy to help with staging tests.\n\n"
            "Let me know if you\u2019d like me to generate the migration script, or feel free to ask.\n\n"
            "Would you like me to benchmark the connection pool next?\n\n"
            "As of my last training update, the v3 client requires TLS 1.3, and up to my last knowledge the flag is experimental.\n\n"
            "While specific details are limited, this behavior is not widely documented in readily available sources.\n\n"
            "This section is organized by deployment phase. The table below compares regional error budgets.\n\n"
            "The figures below were compiled from Q3 load tests.\n\n"
            "Despite these challenges, the storage engine continues to thrive. The future looks bright, and exciting times lie ahead.\n\n"
            "Don\u2019t get me wrong, local caches help, and I\u2019m not saying that indexes are free.\n\n"
            "A tempting approach would be to disable fsync, and one might be tempted to skip checksums.\n\n"
            "No setup call, no templates, no spreadsheets.\n"
        )

        rep = prose_lint.analyze_text(slop_fixture, source="humanizer_tells.md")
        mech = rep["mechanics_and_tells"]

        self.assertIn("chatbot_artifacts", mech)
        self.assertIn("meta_and_strawman_tells", mech)

        chat_hits = mech["chatbot_artifacts"]
        meta_hits = mech["meta_and_strawman_tells"]
        chat_matches = " | ".join(h["match"] for h in chat_hits)
        meta_matches = " | ".join(h["match"] for h in meta_hits)

        for expected_chat in (
            "great question",
            "certainly,",
            "of course,",
            "sure thing.",
            "i hope this helps",
            "happy to help",
            "let me know if you'd like",
            "feel free to ask",
            "would you like me to",
            "as of my last training update",
            "up to my last knowledge",
            "while specific details are limited",
            "not widely documented in readily available sources",
        ):
            self.assertIn(expected_chat, chat_matches)

        for expected_meta in (
            "this section is organized by",
            "the table below compares",
            "the figures below were compiled from",
            "continues to thrive",
            "the future looks bright",
            "exciting times lie ahead",
            "don't get me wrong",
            "i'm not saying that",
            "a tempting approach would be to",
            "one might be tempted to",
            "no setup call, no templates, no spreadsheets",
        ):
            self.assertIn(expected_meta, meta_matches)

        # Human-readable formatter and CLI JSON checks
        human_out = prose_lint.format_human_report(rep)
        self.assertIn("[chatbot_artifacts]", human_out)
        self.assertIn("[meta_and_strawman_tells]", human_out)

        cli_proc = _run_lint_cli("--json", stdin_text=slop_fixture)
        self.assertEqual(cli_proc.returncode, 0, cli_proc.stderr)
        cli_json = json.loads(cli_proc.stdout)
        self.assertEqual(
            len(cli_json["mechanics_and_tells"]["chatbot_artifacts"]),
            len(chat_hits),
        )
        self.assertEqual(
            len(cli_json["mechanics_and_tells"]["meta_and_strawman_tells"]),
            len(meta_hits),
        )

        # Hard invariant: zero composite AI detector score keys anywhere
        banned_key_substrings = (
            "score",
            "detector",
            "probability",
            "slop_index",
            "ai_likelihood",
            "human_rating",
        )
        for key_name in _collect_all_keys(cli_json):
            for banned in banned_key_substrings:
                self.assertNotIn(banned, key_name.lower())

        # Immunity check: inline code spans, ASCII/curly double quotes, fenced blocks, and mid-sentence prose
        immune_fixture = (
            'Delete leaked wrappers like "Great question", "I hope this helps", '
            '"Certainly, here is the draft", and \u201cAs of my last training update\u201d.\n\n'
            'Avoid meta filler such as "This section is organized by", "The table below compares", '
            '"Don\'t get me wrong", and \u201cNo setup call, no templates, no spreadsheets\u201d.\n\n'
            "Strip `Great question`, `Happy to help`, `Would you like me to`, "
            "`A tempting approach would be to`, and `Exciting times lie ahead` during editing.\n\n"
            "Checksum mismatches will certainly trigger an HTTP 400 rejection. "
            "No data loss and no downtime occurred during the shard drain.\n\n"
            "```markdown\n"
            "Certainly, Great question! I hope this helps.\n"
            "This document is organized by tier. No setup call, no templates, no spreadsheets.\n"
            "```\n"
        )
        immune_rep = prose_lint.analyze_text(immune_fixture, source="immune_tells.md")
        immune_mech = immune_rep["mechanics_and_tells"]
        self.assertEqual(immune_mech["chatbot_artifacts"], [])
        self.assertEqual(immune_mech["meta_and_strawman_tells"], [])

    def test_tc_019_03_spec_sync_and_clean_repo_zero_false_positives(self) -> None:
        """TC-019-03: data-model.md and behaviors.md stay synced and clean repo prose yields zero false positives."""
        data_model_path = ROOT / "docs" / "spec" / "data-model.md"
        behaviors_path = ROOT / "docs" / "spec" / "behaviors.md"
        data_model_text = data_model_path.read_text(encoding="utf-8")
        behaviors_text = behaviors_path.read_text(encoding="utf-8")

        self.assertIn('"chatbot_artifacts"', data_model_text)
        self.assertIn('"meta_and_strawman_tells"', data_model_text)

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

        # behaviors.md B-007 documents spaced --, en-dash, chatbot_artifacts, and meta_and_strawman_tells
        self.assertIn("--", behaviors_text)
        self.assertIn("en-dash", behaviors_text.lower())
        self.assertIn("chatbot_artifacts", behaviors_text)
        self.assertIn("meta_and_strawman_tells", behaviors_text)

        # Both edited spec files must have zero overloaded sentences (<=35w), zero tells, and zero literal U+2014
        for spec_path in (data_model_path, behaviors_path):
            raw_spec = spec_path.read_text(encoding="utf-8")
            self.assertNotIn(
                EM_DASH, raw_spec, f"Literal em dash found in {spec_path.name}"
            )
            spec_rep = prose_lint.analyze_text(raw_spec, source=spec_path.name)
            self.assertEqual(
                spec_rep["cadence"]["overloaded_sentences"],
                [],
                f"{spec_path.name} has overloaded sentences (>35w): {spec_rep['cadence']['overloaded_sentences']}",
            )
            for key, val in spec_rep["mechanics_and_tells"].items():
                if isinstance(val, list):
                    self.assertEqual(
                        val,
                        [],
                        f"{spec_path.name} triggered {key}: {val}",
                    )
            self.assertEqual(
                spec_rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{spec_path.name} triggered importance_without_mechanism",
            )

        # Sweep all clean repository Markdown files required by TC-019-03
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
        # Also include all authored hygiene files discovered by validate_skill
        seen = {p.resolve() for p in sweep_files}
        for extra in validate_skill._collect_prose_hygiene_files(ROOT):
            if extra.resolve() not in seen:
                seen.add(extra.resolve())
                sweep_files.append(extra)

        self.assertGreaterEqual(len(sweep_files), 28)
        for md_path in sweep_files:
            self.assertTrue(md_path.is_file(), f"Expected file missing: {md_path}")
            rel = md_path.relative_to(ROOT).as_posix()
            rep = prose_lint.analyze_text(
                md_path.read_text(encoding="utf-8"), source=rel
            )
            mech = rep["mechanics_and_tells"]
            for key in ("em_dashes", "chatbot_artifacts", "meta_and_strawman_tells"):
                self.assertEqual(
                    mech[key],
                    [],
                    f"{rel} triggered false positive on {key}: {mech[key]}",
                )

        # Zero literal em dashes in modified Python files
        for py_path in (
            LINT_CLI,
            ROOT / "tests" / "test_task_004_prose_lint.py",
            Path(__file__).resolve(),
        ):
            self.assertNotIn(
                EM_DASH,
                py_path.read_text(encoding="utf-8"),
                f"Literal em dash found in {py_path.name}",
            )


if __name__ == "__main__":
    unittest.main()
