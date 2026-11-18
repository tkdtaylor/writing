"""Unit and CLI integration tests for Task 004: strip_markdown.py and prose_lint.py.

Covers TC-004-01 through TC-004-04 from
docs/tasks/test-specs/004-prose-lint-and-stripper-cli-test-spec.md.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import prose_lint, strip_markdown

ROOT = Path(__file__).resolve().parent.parent
STRIP_CLI = ROOT / "scripts" / "strip_markdown.py"
LINT_CLI = ROOT / "scripts" / "prose_lint.py"
EM_DASH = "\u2014"


def _run_cli(
    script: Path, *args: str, stdin_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


class TestTask004ProseLintAndStripper(unittest.TestCase):
    """Verification suite for REQ-004-01..REQ-004-04 (TC-004-01..TC-004-04)."""

    def test_tc_004_01_strip_markdown_fixture_and_cli(self) -> None:
        """TC-004-01: strip_markdown.py strips non-prose syntax, separates headings, and detects hard wraps."""
        fixture = (
            "---\n"
            "title: Webhook Guide\n"
            "draft: false\n"
            "---\n"
            "\n"
            "# Webhook Verification\n"
            "\n"
            "<!-- internal editorial comment\n"
            "spanning two lines -->\n"
            "\n"
            "Read the [architecture guide](https://example.com/docs/arch) before editing "
            "![diagram](https://example.com/arch.png) the **handler** `config.py`.\n"
            "\n"
            "| Header A | Header B |\n"
            "|----------|----------|\n"
            "| cell_one | cell_two |\n"
            "\n"
            "```python\n"
            f'secret = "fenced_code_token {EM_DASH} ignored"\n'
            "```\n"
            "\n"
            "~~~bash\n"
            "curl -s https://example.com/tilde_fenced_ignored\n"
            "~~~\n"
            "\n"
            "Secondary Heading\n"
            "-----------------\n"
            "\n"
            "This paragraph is intentionally wrapped right around column seventy-five so\n"
            "the prose continues directly on the next line without a blank separator.\n"
            "\n"
            "Line one uses two trailing spaces for an explicit break.  \n"
            "Line two finishes the intentional break cleanly.\n"
            "\n"
            "[unused-ref]: https://example.com/unused\n"
        )

        # Direct library call check
        result = strip_markdown.strip_markdown(fixture, source="fixture.md")
        self.assertEqual(
            set(result.keys()),
            {
                "source",
                "text",
                "paragraphs",
                "headings",
                "hard_wrapped_lines",
                "word_count",
            },
        )
        self.assertEqual(result["source"], "fixture.md")
        self.assertEqual(
            result["headings"],
            ["Webhook Verification", "Secondary Heading"],
        )

        body = result["text"]
        # Preserves reader-visible anchor text and unwrapped inline code/bold text
        self.assertIn("Read the architecture guide before editing", body)
        self.assertIn("the handler config.py.", body)
        # Strips frontmatter, comments, tables, code blocks, image syntax, and link URLs
        for forbidden in (
            "title: Webhook Guide",
            "internal editorial comment",
            "Header A",
            "cell_one",
            "fenced_code_token",
            "tilde_fenced_ignored",
            "https://example.com",
            "![diagram]",
            "unused-ref",
            "Webhook Verification",
            "Secondary Heading",
        ):
            self.assertNotIn(forbidden, body)

        # Lines 28 and 29 in the fixture are the 80-col wrapped paragraph; lines 31-32 use two trailing spaces.
        self.assertEqual(result["hard_wrapped_lines"], [28, 29])
        self.assertGreater(result["word_count"], 20)

        # CLI --json and plain-text checks via temp file and stdin
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "sample.md"
            md_path.write_text(fixture, encoding="utf-8")

            json_proc = _run_cli(STRIP_CLI, str(md_path), "--json")
            self.assertEqual(json_proc.returncode, 0, json_proc.stderr)
            cli_data = json.loads(json_proc.stdout)
            self.assertEqual(cli_data["headings"], result["headings"])
            self.assertEqual(cli_data["hard_wrapped_lines"], [28, 29])
            self.assertEqual(cli_data["text"], result["text"])

            plain_proc = _run_cli(STRIP_CLI, stdin_text=fixture)
            self.assertEqual(plain_proc.returncode, 0, plain_proc.stderr)
            self.assertIn("architecture guide", plain_proc.stdout)
            self.assertNotIn("https://example.com", plain_proc.stdout)

            missing_proc = _run_cli(STRIP_CLI, str(Path(tmpdir) / "missing.md"))
            self.assertEqual(missing_proc.returncode, 2)
            self.assertIn("not found", missing_proc.stderr.lower())

        # Verify executable bit and stdlib-only imports
        self.assertTrue(os.access(STRIP_CLI, os.X_OK))
        tree = ast.parse(STRIP_CLI.read_text(encoding="utf-8"))
        stdlib_names = sys.stdlib_module_names
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    self.assertIn(root_mod, stdlib_names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root_mod = node.module.split(".")[0]
                self.assertIn(root_mod, stdlib_names)

    def test_tc_004_02_cadence_and_lexical_diversity(self) -> None:
        """TC-004-02: prose_lint.py computes cadence CV, cadence_masking, overloaded sentences, MATTR-50, and 3-grams."""
        uniform_prose = (
            "The service reads incoming requests from the queue and validates every header before routing work.\n\n"
            "The worker parses payload fields from the message and writes structured records into local storage.\n\n"
            "The scheduler checks active leases across the cluster and assigns pending partitions during each cycle.\n\n"
            "The monitor collects latency counters from each node and publishes summary snapshots every single minute.\n"
        )

        varied_prose = (
            "Stop guessing at tail latency.\n\n"
            "Measure p99 response times at the ingress proxy before tuning thread pools or connection limits.\n\n"
            "Small queues hide big stalls. When a downstream database locks a hot row during a schema migration, "
            "worker threads pile up behind the connection pool, memory pressure climbs across every replica, and "
            "health probes begin timing out within seconds even though CPU utilization looks completely idle on "
            "the primary dashboard.\n\n"
            "Drain one shard first, watch error budgets for ten minutes, and keep rollback scripts ready.\n"
        )

        masked_cadence_fixture = (
            "- Fast setup\n"
            "- Zero config\n"
            "- Clean logs\n"
            "- Quick deploys\n"
            "- Simple flags\n\n"
            "The platform processes incoming customer events and stores normalized records inside the primary database table.\n\n"
            "The pipeline validates incoming schema versions and routes verified payloads toward the downstream analytics cluster.\n\n"
            "The operator reviews scheduled job metrics and updates capacity thresholds across the regional worker fleet.\n\n"
            "The gateway enforces strict request timeouts and returns structured errors whenever upstream dependencies stall.\n"
        )

        repetitive_fixture = (
            "In order to scale the system we cache hot keys in memory. "
            "In order to scale the database we partition large tables by tenant. "
            "In order to scale the workers we batch outbound webhook deliveries. "
            "Teams scale the system when they cache hot keys in memory.\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            u_path = Path(tmpdir) / "uniform.md"
            v_path = Path(tmpdir) / "varied.md"
            m_path = Path(tmpdir) / "masked.md"
            r_path = Path(tmpdir) / "repeat.md"
            u_path.write_text(uniform_prose, encoding="utf-8")
            v_path.write_text(varied_prose, encoding="utf-8")
            m_path.write_text(masked_cadence_fixture, encoding="utf-8")
            r_path.write_text(repetitive_fixture, encoding="utf-8")

            u_rep = json.loads(_run_cli(LINT_CLI, str(u_path), "--json").stdout)
            v_rep = json.loads(_run_cli(LINT_CLI, str(v_path), "--json").stdout)
            m_rep = json.loads(_run_cli(LINT_CLI, str(m_path), "--json").stdout)
            r_rep = json.loads(_run_cli(LINT_CLI, str(r_path), "--json").stdout)

        # Verify exact cadence and lexical_diversity schema keys
        self.assertEqual(
            set(v_rep["cadence"].keys()),
            {
                "mean_sentence_words",
                "body_sentence_cv",
                "paragraph_word_cv",
                "cadence_masking",
                "overloaded_sentences",
                "ari_grade",
                "flesch_kincaid_grade",
            },
        )
        self.assertEqual(
            set(v_rep["lexical_diversity"].keys()),
            {"mattr_50", "repeated_trigram_rate", "repeated_trigrams"},
        )

        # Varied prose has higher body_sentence_cv and paragraph_word_cv than uniform prose
        self.assertLess(u_rep["cadence"]["body_sentence_cv"], 0.12)
        self.assertGreater(
            v_rep["cadence"]["body_sentence_cv"],
            u_rep["cadence"]["body_sentence_cv"] + 0.25,
        )
        self.assertGreater(v_rep["cadence"]["paragraph_word_cv"], 0.30)
        self.assertFalse(v_rep["cadence"]["cadence_masking"])

        # Overloaded sentence (>35 words) flagged in varied_prose
        self.assertEqual(len(v_rep["cadence"]["overloaded_sentences"]), 1)
        self.assertGreater(v_rep["cadence"]["overloaded_sentences"][0]["words"], 35)
        self.assertGreater(v_rep["cadence"]["ari_grade"], 0.0)
        self.assertGreater(v_rep["cadence"]["flesch_kincaid_grade"], 0.0)

        # Short bullets + flat 15-word body sentences trigger cadence_masking
        self.assertTrue(m_rep["cadence"]["cadence_masking"])
        self.assertLess(m_rep["cadence"]["body_sentence_cv"], 0.35)

        # Repeated phrase fixture detects repeated trigrams and lower MATTR-50 than varied prose
        trigram_strings = [
            item["trigram"]
            for item in r_rep["lexical_diversity"]["repeated_trigrams"]
        ]
        self.assertIn("in order to", trigram_strings)
        self.assertIn("order to scale", trigram_strings)
        self.assertGreater(r_rep["lexical_diversity"]["repeated_trigram_rate"], 0.0)
        self.assertLess(
            r_rep["lexical_diversity"]["mattr_50"],
            v_rep["lexical_diversity"]["mattr_50"],
        )

    def test_tc_004_03_substance_posture_and_mechanical_tells(self) -> None:
        """TC-004-03: prose_lint.py distinguishes slop-heavy prose from concrete anchored prose."""
        slop_fixture = (
            "In today's fast-paced engineering landscape, let's dive in to how teams delve into "
            f"a robust, seamless tapestry of microservices {EM_DASH} a pivotal paradigm and north star.\n\n"
            "Observability plays a pivotal role in modern organizations and stands as a testament to excellence.\n\n"
            "This shift might arguably represent an absolutely transformative milestone for platform teams.\n\n"
            "The takeaway is simple: teams must bolster and catalyze their core substrate and flywheel.\n\n"
            "From strategy to execution, this isn't just a tool, it's a holistic scaffolding that "
            "not only streamlines workflows, but also supercharges outcomes.\n\n"
            "- **Security:** Security was meticulously prioritized across every single layer.\n"
            "- \u2705 Ship updates rapidly and effortlessly\n\n"
            "Why do migrations stall? What are teams missing? Are legacy queues holding you back?\n\n"
            "This paragraph is hard-wrapped near eighty columns so the first line continues right\n"
            "into the second line without any blank line separating the two prose lines.\n"
        )

        anchored_fixture = (
            "Verify HMAC-SHA256 signatures in `verify_webhook()` before parsing JSON request bodies. "
            'Reject requests missing the `"X-Hub-Signature-256"` header with HTTP 401 in under 2 ms.\n\n'
            "Signature verification is crucial because it blocks forged payloads before Postgres writes occur. "
            "During Q3 load tests on Linux, p95 latency stayed at 4.2 ms across 1,500 rps. "
            "Only early daily batches likely apply to family accounts when operators supply or reply with overrides.\n"
        )

        slop_report = prose_lint.analyze_text(slop_fixture, source="slop.md")
        clean_report = prose_lint.analyze_text(anchored_fixture, source="clean.md")

        # Verify exact substance_and_posture and mechanics_and_tells schema keys
        self.assertEqual(
            set(slop_report["substance_and_posture"].keys()),
            {
                "anchors_per_100w",
                "hedges_per_100w",
                "boosters_per_100w",
                "importance_without_mechanism",
                "hedge_booster_collisions",
            },
        )
        expected_mech_keys = {
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
            "passive_voice_per_100w",
            "adverbs_per_100w",
            "nominalizations_per_100w",
        }
        self.assertEqual(
            set(slop_report["mechanics_and_tells"].keys()), expected_mech_keys
        )

        sub = slop_report["substance_and_posture"]
        mech = slop_report["mechanics_and_tells"]

        # Every slop category must fire on slop_fixture
        self.assertGreaterEqual(len(sub["importance_without_mechanism"]), 1)
        self.assertGreaterEqual(len(sub["hedge_booster_collisions"]), 1)
        self.assertGreaterEqual(len(mech["em_dashes"]), 1)
        self.assertGreaterEqual(len(mech["connector_colons"]), 1)
        self.assertGreaterEqual(len(mech["bold_restatement_bullets"]), 1)
        self.assertGreaterEqual(len(mech["emoji_bullets"]), 1)
        self.assertTrue(mech["hard_wrapped_lines"])
        self.assertGreaterEqual(len(mech["false_scales"]), 1)
        self.assertGreaterEqual(len(mech["ai_tell_words"]), 4)
        self.assertGreaterEqual(len(mech["inflated_style_verbs"]), 3)
        self.assertGreaterEqual(len(mech["tech_buzz_nouns"]), 3)
        self.assertGreaterEqual(len(mech["framing_theater"]), 2)
        self.assertGreaterEqual(len(mech["contrastive_pivots"]), 2)
        self.assertGreaterEqual(len(mech["copula_avoidance"]), 1)
        self.assertGreaterEqual(len(mech["stacked_questions"]), 1)
        self.assertGreater(mech["passive_voice_per_100w"], 0.0)
        self.assertGreater(mech["adverbs_per_100w"], 0.0)

        # Concrete anchored fixture should have higher anchor density, zero tells,
        # zero importance_without_mechanism (because 'because' + '2 ms' ground 'crucial'),
        # and zero adverbs despite '-ly' stoplist words (only, early, daily, likely, family, supply, apply, reply).
        clean_sub = clean_report["substance_and_posture"]
        clean_mech = clean_report["mechanics_and_tells"]
        self.assertGreater(clean_sub["anchors_per_100w"], sub["anchors_per_100w"])
        self.assertLess(clean_sub["boosters_per_100w"], sub["boosters_per_100w"])
        self.assertEqual(clean_sub["importance_without_mechanism"], [])
        self.assertEqual(clean_sub["hedge_booster_collisions"], [])
        self.assertEqual(clean_mech["em_dashes"], [])
        self.assertEqual(clean_mech["connector_colons"], [])
        self.assertEqual(clean_mech["bold_restatement_bullets"], [])
        self.assertEqual(clean_mech["emoji_bullets"], [])
        self.assertEqual(clean_mech["hard_wrapped_lines"], [])
        self.assertEqual(clean_mech["false_scales"], [])
        self.assertEqual(clean_mech["ai_tell_words"], [])
        self.assertEqual(clean_mech["inflated_style_verbs"], [])
        self.assertEqual(clean_mech["tech_buzz_nouns"], [])
        self.assertEqual(clean_mech["framing_theater"], [])
        self.assertEqual(clean_mech["contrastive_pivots"], [])
        self.assertEqual(clean_mech["participial_tail_puffery"], [])
        self.assertEqual(clean_mech["copula_avoidance"], [])
        self.assertEqual(clean_mech["rhetorical_qa_pivots"], [])
        self.assertEqual(clean_mech["performative_fragments"], [])
        self.assertEqual(clean_mech["stacked_questions"], [])
        self.assertEqual(clean_mech["shorthand_ambiguities"], [])
        self.assertEqual(clean_mech["exclamation_marks"], [])
        self.assertEqual(clean_mech["false_agency"], [])
        self.assertEqual(clean_mech["adverbs_per_100w"], 0.0)
        self.assertEqual(clean_mech["nominalizations_per_100w"], 0.0)

    def test_tc_004_04_code_fence_masking_no_composite_score_and_cli_modes(
        self,
    ) -> None:
        """TC-004-04: Code-fenced tells are ignored, no composite score exists, and CLI handles stdin/multi-file/errors."""
        code_fenced_fixture = (
            "---\n"
            f"description: Frontmatter with {EM_DASH} delve and pivotal\n"
            "---\n\n"
            "# Clean Guide\n\n"
            "Run the verification script before merging changes into the release branch.\n\n"
            "```markdown\n"
            f"In today's realm {EM_DASH} delve into a seamless, robust tapestry.\n"
            "- **Security:** Security is paramount.\n"
            "- \u2705 Emoji bullet inside code example\n"
            "```\n\n"
            "~~~python\n"
            f'msg = "Not just a script, it\'s a paradigm {EM_DASH} let that sink in"\n'
            "~~~\n"
        )

        second_clean_fixture = (
            "Check exit code 0 after running unit tests on Linux.\n"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "fenced.md"
            f2 = Path(tmpdir) / "second.md"
            f1.write_text(code_fenced_fixture, encoding="utf-8")
            f2.write_text(second_clean_fixture, encoding="utf-8")

            # Single-file JSON mode
            single_proc = _run_cli(LINT_CLI, str(f1), "--json")
            self.assertEqual(single_proc.returncode, 0, single_proc.stderr)
            report = json.loads(single_proc.stdout)
            self.assertIsInstance(report, dict)

            mech = report["mechanics_and_tells"]
            sub = report["substance_and_posture"]
            self.assertEqual(mech["em_dashes"], [])
            self.assertEqual(mech["ai_tell_words"], [])
            self.assertEqual(mech["bold_restatement_bullets"], [])
            self.assertEqual(mech["emoji_bullets"], [])
            self.assertEqual(mech["framing_theater"], [])
            self.assertEqual(mech["contrastive_pivots"], [])
            self.assertEqual(mech["tech_buzz_nouns"], [])
            self.assertEqual(sub["importance_without_mechanism"], [])

            # Hard invariant: never emit any composite AI/slop/detector score key anywhere
            self.assertEqual(
                set(report.keys()),
                {
                    "source",
                    "word_count",
                    "sentence_count",
                    "paragraph_count",
                    "cadence",
                    "lexical_diversity",
                    "substance_and_posture",
                    "mechanics_and_tells",
                },
            )
            forbidden_substrings = (
                "score",
                "detector",
                "probability",
                "slop_index",
                "ai_likelihood",
                "human_rating",
            )

            def collect_keys(obj: object) -> list[str]:
                keys: list[str] = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        keys.append(str(k))
                        keys.extend(collect_keys(v))
                elif isinstance(obj, list):
                    for elem in obj:
                        keys.extend(collect_keys(elem))
                return keys

            all_keys = collect_keys(report)
            for key in all_keys:
                for banned in forbidden_substrings:
                    self.assertNotIn(banned, key.lower())

            # Multi-file JSON mode returns a list of 2 report objects
            multi_proc = _run_cli(LINT_CLI, str(f1), str(f2), "--json")
            self.assertEqual(multi_proc.returncode, 0, multi_proc.stderr)
            multi_data = json.loads(multi_proc.stdout)
            self.assertIsInstance(multi_data, list)
            self.assertEqual(len(multi_data), 2)
            self.assertEqual(multi_data[0]["source"], str(f1))
            self.assertEqual(multi_data[1]["source"], str(f2))

            # Stdin mode (human-readable and --json --raw)
            stdin_human = _run_cli(LINT_CLI, stdin_text=second_clean_fixture)
            self.assertEqual(stdin_human.returncode, 0, stdin_human.stderr)
            self.assertIn("Prose Lint: <stdin>", stdin_human.stdout)
            self.assertIn("Findings: none", stdin_human.stdout)

            stdin_raw_json = _run_cli(
                LINT_CLI, "-", "--json", "--raw", stdin_text="[link](https://example.com) text."
            )
            self.assertEqual(stdin_raw_json.returncode, 0, stdin_raw_json.stderr)
            raw_rep = json.loads(stdin_raw_json.stdout)
            self.assertEqual(raw_rep["source"], "<stdin>")
            self.assertGreaterEqual(raw_rep["word_count"], 3)

            # Missing file returns exit code 2
            missing_proc = _run_cli(LINT_CLI, str(Path(tmpdir) / "does-not-exist.md"))
            self.assertEqual(missing_proc.returncode, 2)
            self.assertIn("not found", missing_proc.stderr.lower())

        # Verify executable bit, stdlib-only imports, and zero literal em dashes in source files
        self.assertTrue(os.access(LINT_CLI, os.X_OK))
        for src_path in (STRIP_CLI, LINT_CLI, Path(__file__).resolve()):
            raw_src = src_path.read_text(encoding="utf-8")
            self.assertNotIn(
                EM_DASH,
                raw_src,
                f"Literal em dash character found in {src_path.name}; use unicode escape instead.",
            )

        tree = ast.parse(LINT_CLI.read_text(encoding="utf-8"))
        allowed_roots = set(sys.stdlib_module_names) | {"scripts", "strip_markdown"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name.split(".")[0], allowed_roots)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertIn(node.module.split(".")[0], allowed_roots)


if __name__ == "__main__":
    unittest.main()
