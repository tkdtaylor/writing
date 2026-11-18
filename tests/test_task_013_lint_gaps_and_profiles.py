"""Unit and CLI integration tests for Task 013: prose_lint.py gaps and genre profiles.

Covers TC-013-01 through TC-013-03 from
docs/tasks/test-specs/013-prose-lint-gaps-and-genre-profiles-test-spec.md.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
LINT_CLI = ROOT / "scripts" / "prose_lint.py"
EM_DASH = "\u2014"

FORBIDDEN_SCORE_SUBSTRINGS = (
    "score",
    "detector",
    "probability",
    "slop_index",
    "ai_likelihood",
    "human_rating",
)


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


def _collect_keys(obj: object) -> list[str]:
    keys: list[str] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            keys.append(str(key))
            keys.extend(_collect_keys(val))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(_collect_keys(item))
    return keys


def _repeat_sentence(words_per_sentence: int, count: int) -> str:
    base = [
        "The",
        "service",
        "validates",
        "incoming",
        "webhook",
        "headers",
        "before",
        "storing",
        "signed",
        "records",
        "inside",
        "durable",
        "regional",
        "queues",
        "during",
        "peak",
        "checkout",
        "traffic",
        "windows",
        "daily",
    ]
    sentence = " ".join(base[:words_per_sentence]) + "."
    return "\n\n".join(sentence for _ in range(count))


class TestTask013LintGapsAndProfiles(unittest.TestCase):
    """Verification suite for REQ-013-01..REQ-013-03 (TC-013-01..TC-013-03)."""

    def test_tc_013_01_new_tell_detectors_and_cli_oserror_guard(self) -> None:
        """TC-013-01: shorthand_ambiguities, exclamation_marks, false_agency, and OSError CLI exit 2."""
        violation_fixture = (
            "Configure the flag and/or restart the affected file(s) and user(s).\n\n"
            "Do not ship unverified migrations today!\n\n"
            "The metrics speak clearly, while the data tells us to ship and the architecture demands alignment.\n\n"
            "Meanwhile, the worker retries failed deliveries and the broker acks each batch.\n"
        )

        exempt_fixture = (
            "Use `and/or` and `file(s)` only inside literal syntax examples.\n\n"
            "> [!NOTE]\n"
            "> [!TIP]\n"
            "> [!IMPORTANT]\n"
            "> [!WARNING]\n"
            "> [!CAUTION]\n\n"
            "Render ![img] and ![diagram](https://example.com/diagram.png) in docs.\n\n"
            "Check `status != 200` and `a !== b` and `echo \"hello!\"` in tests.\n\n"
            "The response returned \"Great!\" and never raised a != b error.\n\n"
            "<!-- internal note! ignored by prose lint -->\n\n"
            "```bash\n"
            "echo \"fenced code!\"\n"
            "```\n\n"
            "The worker retries failed webhooks and the broker acks valid frames.\n"
        )

        rep = prose_lint.analyze_text(violation_fixture, source="violations.md")
        mech = rep["mechanics_and_tells"]

        # shorthand_ambiguities fires on and/or, file(s), user(s)
        shorthand_matches = {item["match"] for item in mech["shorthand_ambiguities"]}
        self.assertEqual(shorthand_matches, {"and/or", "file(s)", "user(s)"})
        self.assertTrue(all(item["line"] == 1 for item in mech["shorthand_ambiguities"]))

        # exclamation_marks fires on line 3 prose '!'
        self.assertEqual(len(mech["exclamation_marks"]), 1)
        self.assertEqual(mech["exclamation_marks"][0]["line"], 3)
        self.assertEqual(mech["exclamation_marks"][0]["count"], 1)

        # false_agency fires on metrics speak / the data tells us / the architecture demands
        agency_matches = {item["match"] for item in mech["false_agency"]}
        self.assertIn("the metrics speak", agency_matches)
        self.assertIn("the data tells us", agency_matches)
        self.assertIn("the architecture demands", agency_matches)
        self.assertEqual(len(agency_matches), 3)

        # Concrete software runtime actors remain unflagged
        agency_joined = " ".join(agency_matches)
        self.assertNotIn("worker", agency_joined)
        self.assertNotIn("broker", agency_joined)

        # format_human_report surfaces all 3 new tell categories
        human_out = prose_lint.format_human_report(rep)
        self.assertIn("[shorthand_ambiguity]", human_out)
        self.assertIn("[exclamation_mark]", human_out)
        self.assertIn("[false_agency]", human_out)

        # Exempt fixture produces zero false positives across all 3 detectors
        clean_rep = prose_lint.analyze_text(exempt_fixture, source="exempt.md")
        clean_mech = clean_rep["mechanics_and_tells"]
        self.assertEqual(clean_mech["shorthand_ambiguities"], [])
        self.assertEqual(clean_mech["exclamation_marks"], [])
        self.assertEqual(clean_mech["false_agency"], [])

        # Mocked PermissionError on Path.is_file returns exit code 2 cleanly
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "locked.md"
            target.write_text("Clean prose.\n", encoding="utf-8")
            stderr_buf = io.StringIO()
            with (
                mock.patch.object(
                    Path, "is_file", side_effect=PermissionError("permission denied")
                ),
                mock.patch.object(sys, "stderr", stderr_buf),
            ):
                rc = prose_lint.main([str(target)])
            self.assertEqual(rc, 2)
            self.assertIn("cannot read", stderr_buf.getvalue().lower())

    def test_tc_013_02_genre_profiles_and_sample_validation(self) -> None:
        """TC-013-02: --profile / --mode enforces technical, one-pager, six-pager, memo, and narrative checks."""
        # 1. Default mode omits profile_checks; invalid profile fails cleanly
        default_rep = prose_lint.analyze_text("Check exit code 0 on Linux.")
        self.assertNotIn("profile_checks", default_rep)
        with self.assertRaises(ValueError):
            prose_lint.analyze_text("Check exit code 0.", profile="unknown")

        bad_cli = _run_lint_cli("--profile", "unknown", stdin_text="Check exit code 0.")
        self.assertEqual(bad_cli.returncode, 2)

        # 2. Technical profile: samples/technical-doc.after.md passes cleanly
        tech_sample = (ROOT / "samples" / "technical-doc.after.md").read_text(
            encoding="utf-8"
        )
        tech_sample_rep = prose_lint.analyze_text(
            tech_sample,
            source="samples/technical-doc.after.md",
            profile="technical",
        )
        self.assertTrue(tech_sample_rep["profile_checks"]["passed"])
        self.assertEqual(tech_sample_rep["profile_checks"]["overlong_steps"], [])
        self.assertEqual(tech_sample_rep["profile_checks"]["date_time_issues"], [])

        # Technical violations: >20-word step + slash date + 12h clock time (ignoring quotes/code)
        bad_tech_md = (
            "# Deploy Guide\n\n"
            "1. Open the regional staging console, inspect every active worker lease, verify "
            "all pending migration rows, and confirm zero errors before promoting traffic.\n"
            "2. Run `deploy.sh` and check HTTP 200.\n\n"
            "Schedule the window on 10/12/2026 at 3:30 p.m. and ignore `01/02/2026` or \"9:00 AM\".\n"
        )
        bad_tech_rep = prose_lint.analyze_text(
            bad_tech_md, source="bad_tech.md", profile="technical"
        )
        bad_tech_pc = bad_tech_rep["profile_checks"]
        self.assertFalse(bad_tech_pc["passed"])
        self.assertEqual(len(bad_tech_pc["overlong_steps"]), 1)
        self.assertGreater(bad_tech_pc["overlong_steps"][0]["words"], 20)
        date_matches = [item["match"] for item in bad_tech_pc["date_time_issues"]]
        self.assertEqual(date_matches, ["10/12/2026", "3:30 p.m."])
        human_tech = prose_lint.format_human_report(bad_tech_rep)
        self.assertIn("Profile (technical): REVIEW", human_tech)
        self.assertIn("[overlong_step]", human_tech)
        self.assertIn("[date_time_issue]", human_tech)

        # 3. One-pager profile via CLI --mode alias on samples/one-pager.after.md
        op_cli = _run_lint_cli(
            "samples/one-pager.after.md", "--mode", "one-pager", "--json"
        )
        self.assertEqual(op_cli.returncode, 0, op_cli.stderr)
        op_rep = json.loads(op_cli.stdout)
        op_pc = op_rep["profile_checks"]
        self.assertEqual(op_pc["profile"], "one-pager")
        self.assertTrue(op_pc["passed"])
        self.assertTrue(op_pc["word_budget_ok"])
        self.assertTrue(op_pc["prose_density_ok"])
        self.assertGreaterEqual(op_pc["prose_paragraph_share"], 0.80)
        self.assertEqual(op_pc["date_time_issues"], [])

        op_human_cli = _run_lint_cli("samples/one-pager.after.md", "--profile", "one-pager")
        self.assertEqual(op_human_cli.returncode, 0, op_human_cli.stderr)
        self.assertIn("Profile (one-pager): PASS", op_human_cli.stdout)
        self.assertIn("Findings: none", op_human_cli.stdout)

        # Bullet-heavy / short one-pager fails budget and prose density
        bullet_one_pager = "\n".join(
            f"- Option {i} cuts queue latency for regional traffic." for i in range(1, 15)
        )
        bullet_op_rep = prose_lint.analyze_text(
            bullet_one_pager, source="slides.md", profile="one-pager"
        )
        self.assertFalse(bullet_op_rep["profile_checks"]["passed"])
        self.assertFalse(bullet_op_rep["profile_checks"]["word_budget_ok"])
        self.assertFalse(bullet_op_rep["profile_checks"]["prose_density_ok"])
        self.assertLess(bullet_op_rep["profile_checks"]["prose_paragraph_share"], 0.80)

        # 4. Six-pager profile: strips ## Appendix / ## Appendices onward from body count
        six_body = _repeat_sentence(18, 50)  # 900 words of complete prose paragraphs
        giant_appendix = (
            "\n\n## Appendix A: Benchmark Logs\n\n"
            + _repeat_sentence(20, 120)  # +2400 words in Appendix
        )
        six_with_appendix = "# Six-Pager Proposal\n\n" + six_body + giant_appendix
        six_rep = prose_lint.analyze_text(
            six_with_appendix, source="six_pager.md", profile="six-pager"
        )
        six_pc = six_rep["profile_checks"]
        self.assertTrue(six_pc["passed"])
        self.assertTrue(six_pc["appendix_stripped"])
        self.assertEqual(six_pc["body_word_count"], 900)
        self.assertTrue(six_pc["word_budget_ok"])
        self.assertEqual(six_pc["prose_paragraph_share"], 1.0)
        self.assertTrue(six_pc["prose_density_ok"])

        # Pre-Appendix body > 2500 words fails even without an Appendix
        overlong_six = "# Six-Pager\n\n" + _repeat_sentence(20, 130)  # 2600w
        overlong_six_rep = prose_lint.analyze_text(
            overlong_six, source="long_six.md", profile="six-pager"
        )
        self.assertFalse(overlong_six_rep["profile_checks"]["passed"])
        self.assertFalse(overlong_six_rep["profile_checks"]["word_budget_ok"])
        self.assertGreater(overlong_six_rep["profile_checks"]["body_word_count"], 2500)

        # Fenced ## Appendix inside a code block must NOT truncate body count
        fenced_appendix_doc = (
            "# Six-Pager\n\n"
            + _repeat_sentence(20, 130)
            + "\n\n```markdown\n## Appendix Example\n```\n"
        )
        fenced_rep = prose_lint.analyze_text(
            fenced_appendix_doc, source="fenced_app.md", profile="six-pager"
        )
        self.assertFalse(fenced_rep["profile_checks"]["appendix_stripped"])
        self.assertGreater(fenced_rep["profile_checks"]["body_word_count"], 2500)

        # 5. Memo profile auto-resolution (<=750w -> one-pager, >750w -> six-pager)
        op_sample_text = (ROOT / "samples" / "one-pager.after.md").read_text(
            encoding="utf-8"
        )
        memo_short_rep = prose_lint.analyze_text(
            op_sample_text, source="memo_short.md", profile="memo"
        )
        self.assertEqual(memo_short_rep["profile_checks"]["profile"], "one-pager")
        self.assertEqual(memo_short_rep["profile_checks"]["requested_profile"], "memo")
        self.assertTrue(memo_short_rep["profile_checks"]["passed"])

        memo_long_rep = prose_lint.analyze_text(
            six_with_appendix, source="memo_long.md", profile="memo"
        )
        self.assertEqual(memo_long_rep["profile_checks"]["profile"], "six-pager")
        self.assertEqual(memo_long_rep["profile_checks"]["requested_profile"], "memo")
        self.assertTrue(memo_long_rep["profile_checks"]["passed"])
        self.assertIn("Profile (memo -> six-pager): PASS", prose_lint.format_human_report(memo_long_rep))

        # 6. Narrative profile: >= 85% prose share and body_sentence_cv >= 0.30 (>= 6 body sentences)
        varied_narrative = (
            "The primary database stalled during the morning deploy.\n\n"
            "When connection pools fill up behind a single long-running schema lock across "
            "three regional shards, application workers queue incoming checkout requests "
            "until upstream load balancers drop the TCP sockets.\n\n"
            "Operators drained one shard first to verify recovery.\n\n"
            "Within ninety seconds, queue depth fell from four thousand waiting tasks to "
            "under thirty active jobs while checkout error rates returned to normal baseline.\n\n"
            "We moved schema migrations into an isolated pre-deploy job.\n\n"
            "Every release pipeline now verifies lock timeouts against staging replicas "
            "before touching customer-facing production tables.\n"
        )
        nar_pass = prose_lint.analyze_text(
            varied_narrative, source="essay.md", profile="narrative"
        )
        self.assertTrue(nar_pass["profile_checks"]["passed"])
        self.assertTrue(nar_pass["profile_checks"]["prose_density_ok"])
        self.assertTrue(nar_pass["profile_checks"]["cadence_ok"])
        self.assertGreaterEqual(nar_pass["profile_checks"]["body_sentence_cv"], 0.30)

        flat_narrative = _repeat_sentence(15, 7)
        nar_fail_cv = prose_lint.analyze_text(
            flat_narrative, source="flat.md", profile="narrative"
        )
        self.assertFalse(nar_fail_cv["profile_checks"]["passed"])
        self.assertFalse(nar_fail_cv["profile_checks"]["cadence_ok"])
        self.assertLess(nar_fail_cv["profile_checks"]["body_sentence_cv"], 0.30)

        # Ensure zero composite score keys appear in any profile output
        for rep_obj in (
            tech_sample_rep,
            bad_tech_rep,
            op_rep,
            six_rep,
            memo_long_rep,
            nar_pass,
        ):
            for key_name in _collect_keys(rep_obj):
                for banned in FORBIDDEN_SCORE_SUBSTRINGS:
                    self.assertNotIn(banned, key_name.lower())

    def test_tc_013_03_specs_sync_and_clean_repo_markdown_restraint(self) -> None:
        """TC-013-03: docs/spec/*.md synchronized and all clean repo Markdown files return [] on new tells."""
        behaviors_text = (ROOT / "docs" / "spec" / "behaviors.md").read_text(
            encoding="utf-8"
        )
        data_model_text = (ROOT / "docs" / "spec" / "data-model.md").read_text(
            encoding="utf-8"
        )
        interfaces_text = (ROOT / "docs" / "spec" / "interfaces.md").read_text(
            encoding="utf-8"
        )

        for key in ("shorthand_ambiguities", "exclamation_marks", "false_agency"):
            self.assertIn(f'"{key}"', data_model_text)

        self.assertIn("--profile", behaviors_text)
        self.assertIn("--mode", behaviors_text)
        self.assertIn("profile_checks", data_model_text)
        self.assertIn("--profile", interfaces_text)
        self.assertIn("--mode", interfaces_text)
        self.assertIn("OSError", interfaces_text)

        # Zero literal em dashes in modified script, spec docs, and this test file
        for path in (
            LINT_CLI,
            ROOT / "docs" / "spec" / "behaviors.md",
            ROOT / "docs" / "spec" / "data-model.md",
            ROOT / "docs" / "spec" / "interfaces.md",
            Path(__file__).resolve(),
        ):
            self.assertNotIn(
                EM_DASH,
                path.read_text(encoding="utf-8"),
                f"Prohibited literal em dash in {path}",
            )

        # Zero false positives across all clean authored repo Markdown files
        authored_files = validate_skill._collect_prose_hygiene_files(ROOT)
        self.assertGreaterEqual(len(authored_files), 26)
        new_keys = ("shorthand_ambiguities", "exclamation_marks", "false_agency")
        for md_path in authored_files:
            rel = md_path.relative_to(ROOT).as_posix()
            report = prose_lint.analyze_text(
                md_path.read_text(encoding="utf-8"), source=rel
            )
            mech = report["mechanics_and_tells"]
            for key in new_keys:
                self.assertEqual(
                    mech[key],
                    [],
                    f"{rel} triggered unexpected {key}: {mech[key]}",
                )


if __name__ == "__main__":
    unittest.main()
