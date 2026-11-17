"""Unit and integration tests for Task 009: advanced flourish detectors and spec sync.

Covers TC-009-01 through TC-009-03 from
docs/tasks/test-specs/009-advanced-flourish-detectors-in-prose-lint-test-spec.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from scripts import prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
LINT_CLI = ROOT / "scripts" / "prose_lint.py"
EM_DASH = "\u2014"

NEW_MECH_KEYS = (
    "participial_tail_puffery",
    "copula_avoidance",
    "rhetorical_qa_pivots",
    "performative_fragments",
    "nominalizations_per_100w",
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


class TestTask009FlourishLintAndSpecSync(unittest.TestCase):
    """Verification suite for REQ-009-01..REQ-009-03 (TC-009-01..TC-009-03)."""

    def test_tc_009_01_new_flourish_detectors_and_technical_exemptions(self) -> None:
        """TC-009-01 (REQ-009-01): fires new flourish detectors on puffery and exempts concrete technical prose."""
        flourish_fixture = (
            "The control plane unifies regional telemetry, ensuring long-term scalability "
            "and highlighting architectural maturity.\n\n"
            "The schema registry standardizes event contracts, thereby fostering cross-team alignment.\n\n"
            "This module serves as a cornerstone for governance and stands as a testament to craftsmanship. "
            "The gateway boasts a 99.99% uptime target and boasts over 50 integrations.\n\n"
            "The result? Deployments finish ahead of schedule. "
            "The catch? Legacy consumers still poll every minute. "
            "Sound familiar? Most platform migrations stall right here. "
            "Why does this matter? Idle polling burns database connections.\n\n"
            "We ship verified schemas. Full stop. Simple as that. "
            "Nothing more, nothing less. That changes everything. "
            "And maybe that\u2019s the point.\n\n"
            "The implementation of the router accelerates the optimization of queue workers "
            "during an assessment of regional capacity.\n"
        )

        clean_technical_fixture = (
            " Envoy acts as a reverse proxy in front of Gunicorn, and Redis functions as a mutex "
            "for distributed lease renewals.\n\n"
            "The webhook worker validates incoming payloads, retrying 3 times within 200 ms. "
            "The ingress filter parses headers, ensuring SHA-256 digests match before database writes. "
            "The verifier checks timestamps, ensuring `X-Signature-256` digests match within 300 seconds.\n\n"
            "Does the ingress proxy retry HTTP 502 responses? Check the upstream timeout counter in Prometheus.\n\n"
            "Cut anti-slop patterns such as `, highlighting architectural maturity.`, "
            "`serves as a cornerstone`, `The result? Faster builds.`, `Full stop.`, "
            "and `the implementation of` during editing.\n"
        )

        flourish_rep = prose_lint.analyze_text(flourish_fixture, source="flourish.md")
        mech = flourish_rep["mechanics_and_tells"]

        self.assertGreaterEqual(len(mech["participial_tail_puffery"]), 2)
        self.assertGreaterEqual(len(mech["copula_avoidance"]), 4)
        self.assertGreaterEqual(len(mech["rhetorical_qa_pivots"]), 4)
        self.assertGreaterEqual(len(mech["performative_fragments"]), 5)
        self.assertGreater(mech["nominalizations_per_100w"], 0.0)

        qa_matches = {item["match"] for item in mech["rhetorical_qa_pivots"]}
        self.assertIn("the result?", qa_matches)
        self.assertIn("the catch?", qa_matches)
        self.assertIn("sound familiar?", qa_matches)
        self.assertIn("why does this matter?", qa_matches)

        frag_matches = {item["match"] for item in mech["performative_fragments"]}
        self.assertIn("full stop.", frag_matches)
        self.assertIn("simple as that.", frag_matches)
        self.assertIn("nothing more, nothing less.", frag_matches)
        self.assertIn("that changes everything.", frag_matches)
        self.assertIn("and maybe that's the point.", frag_matches)

        # Human report must surface all four new finding labels and nominalizations rate
        human_out = prose_lint.format_human_report(flourish_rep)
        self.assertIn("nominalizations=", human_out)
        self.assertIn("[participial_tail_puffery]", human_out)
        self.assertIn("[copula_avoidance]", human_out)
        self.assertIn("[rhetorical_qa_pivot]", human_out)
        self.assertIn("[performative_fragment]", human_out)

        # CLI --json verification on flourish fixture
        cli_proc = _run_lint_cli("--json", stdin_text=flourish_fixture)
        self.assertEqual(cli_proc.returncode, 0, cli_proc.stderr)
        cli_json = json.loads(cli_proc.stdout)
        for key in NEW_MECH_KEYS:
            self.assertIn(key, cli_json["mechanics_and_tells"])

        # Concrete technical prose + inline-code tell examples must produce zero false positives
        clean_rep = prose_lint.analyze_text(clean_technical_fixture, source="clean_tech.md")
        clean_mech = clean_rep["mechanics_and_tells"]
        self.assertEqual(clean_mech["participial_tail_puffery"], [])
        self.assertEqual(clean_mech["copula_avoidance"], [])
        self.assertEqual(clean_mech["rhetorical_qa_pivots"], [])
        self.assertEqual(clean_mech["performative_fragments"], [])
        self.assertEqual(clean_mech["nominalizations_per_100w"], 0.0)

    def test_tc_009_02_upgraded_detectors_and_repo_false_positive_restraint(self) -> None:
        """TC-009-02 (REQ-009-02): upgrades contrastive_pivots, importance_without_mechanism, verbs, and framing."""
        modern_tells_fixture = (
            "This isn\u2019t a tooling issue. It\u2019s a culture problem.\n\n"
            "The service is not simply a wrapper. Instead, it is a regional control plane.\n\n"
            "The architecture behaves less like a cache and more like a durable log, "
            "rather than merely buffering writes.\n\n"
            "Not a script. Not a prototype. A production daemon.\n\n"
            "The new router ships faster without sacrificing reliability. "
            "The gateway scales globally without compromising security. "
            "This distinction matters for platform leaders.\n\n"
            "Teams unleash automation, harness telemetry, reimagine workflows, ignite adoption, "
            "and illuminate bottlenecks.\n\n"
            "Here\u2019s the kicker: queues back up. Here is the catch for operators. "
            "Let\u2019s unpack the failure mode and let\u2019s break this down step by step. "
            "Despite these challenges, teams ship daily. At the end of the day, latency wins. "
            "So, to answer your question, enable backpressure.\n\n"
            "Together, these changes stabilize deployments.\n"
        )

        anchored_restraint_fixture = (
            "Drain one shard at a time rather than restarting the entire Redis cluster.\n\n"
            "Connection pooling cuts p99 latency by 40% without sacrificing TLS certificate verification. "
            "This distinction matters because synchronous disk flushes add 12 ms per commit.\n\n"
            "Every coding-agent harness loads SKILL.md identically across harnesses in a cross-harness setup. "
            "Any harness that reads Markdown can run the local test harness.\n\n"
            "When batched together, these two SQL queries finish in 3 ms. "
            "Do not edit local user settings. Instead, commit shared rules to AGENTS.md. "
            "This token is not valid. It is rejected with HTTP 401.\n"
        )

        rep = prose_lint.analyze_text(modern_tells_fixture, source="modern_tells.md")
        mech = rep["mechanics_and_tells"]
        sub = rep["substance_and_posture"]

        # Contrastive pivots: split 2-sentence mirrors (2), less like/more like (1), rather than merely (1), Not X. Not Y. (1)
        self.assertGreaterEqual(len(mech["contrastive_pivots"]), 5)
        pivot_matches = " | ".join(item["match"] for item in mech["contrastive_pivots"])
        self.assertIn("this isn't a tooling issue. it's a culture problem.", pivot_matches)
        self.assertIn("instead, it is", pivot_matches)
        self.assertIn("less like a cache and more like", pivot_matches)
        self.assertIn("rather than merely", pivot_matches)
        self.assertIn("not a script. not a prototype.", pivot_matches)

        # Importance without mechanism: without sacrificing, without compromising, distinction matters
        imp_triggers = {item["trigger"] for item in sub["importance_without_mechanism"]}
        self.assertIn("without sacrificing", imp_triggers)
        self.assertIn("without compromising", imp_triggers)
        self.assertIn("distinction matters", imp_triggers)

        # Inflated style verbs: unleash, harness, reimagine, ignite, illuminate
        verb_matches = {item["match"] for item in mech["inflated_style_verbs"]}
        for expected_verb in ("unleash", "harness", "reimagine", "ignite", "illuminate"):
            self.assertIn(expected_verb, verb_matches)

        # Framing theater: kicker, catch, unpack, break this down, despite these challenges, at the end of the day, so to answer, together these
        framing_matches = " | ".join(item["match"] for item in mech["framing_theater"])
        for expected_phrase in (
            "here's the kicker",
            "here is the catch",
            "let's unpack",
            "let's break this down",
            "despite these challenges",
            "at the end of the day",
            "so, to answer your question",
            "together, these",
        ):
            self.assertIn(expected_phrase, framing_matches)

        # No composite score keys permitted anywhere in output
        def _collect_keys(obj: object) -> list[str]:
            found: list[str] = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    found.append(str(k))
                    found.extend(_collect_keys(v))
            elif isinstance(obj, list):
                for elem in obj:
                    found.extend(_collect_keys(elem))
            return found

        for key_name in _collect_keys(rep):
            for banned in ("score", "detector", "probability", "slop_index", "ai_likelihood"):
                self.assertNotIn(banned, key_name.lower())

        # Restraint fixture must stay completely clean
        clean_rep = prose_lint.analyze_text(anchored_restraint_fixture, source="restraint.md")
        clean_mech = clean_rep["mechanics_and_tells"]
        self.assertEqual(clean_mech["contrastive_pivots"], [])
        self.assertEqual(clean_rep["substance_and_posture"]["importance_without_mechanism"], [])
        self.assertEqual(clean_mech["inflated_style_verbs"], [])
        self.assertEqual(clean_mech["framing_theater"], [])

        # Existing authored clean repo files must have zero false positives
        clean_repo_files = [
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "AGENTS.md",
            ROOT / "SKILL.md",
            ROOT / "evals" / "JUDGE.md",
            *sorted((ROOT / "references").glob("*.md")),
            *sorted((ROOT / "samples").glob("*.after.md")),
        ]
        zero_list_keys = (
            "em_dashes",
            "emoji_bullets",
            "bold_restatement_bullets",
            "ai_tell_words",
            "inflated_style_verbs",
            "tech_buzz_nouns",
            "framing_theater",
            "contrastive_pivots",
            "participial_tail_puffery",
            "copula_avoidance",
            "rhetorical_qa_pivots",
            "performative_fragments",
        )
        for path in clean_repo_files:
            file_rep = prose_lint.analyze_text(
                path.read_text(encoding="utf-8"),
                source=path.relative_to(ROOT).as_posix(),
            )
            for tkey in zero_list_keys:
                self.assertEqual(
                    file_rep["mechanics_and_tells"][tkey],
                    [],
                    f"{path.name} triggered unexpected {tkey}: {file_rep['mechanics_and_tells'][tkey]}",
                )
            self.assertEqual(
                file_rep["substance_and_posture"]["importance_without_mechanism"],
                [],
                f"{path.name} triggered unexpected importance_without_mechanism",
            )

    def test_tc_009_03_combined_budget_10000_and_spec_sync(self) -> None:
        """TC-009-03 (REQ-009-03): COMBINED_RUNTIME_BUDGET == 10000 and docs/spec/*.md stay synchronized."""
        self.assertEqual(validate_skill.SKILL_MAX_WORDS, 1500)
        self.assertEqual(validate_skill.REFERENCE_MAX_WORDS, 1500)
        self.assertEqual(validate_skill.COMBINED_RUNTIME_BUDGET, 10000)

        # Synthetic package at ~9,100 words (> 8,500, <= 10,000) must pass, while > 10,000 fails
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "references").mkdir(parents=True)
            (base / "commands").mkdir(parents=True)
            (base / "scripts").mkdir(parents=True)
            (base / "scripts" / "strip_markdown.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            (base / "scripts" / "prose_lint.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")

            ref_links: list[str] = []
            for idx in range(1, 7):
                rname = f"ref-{idx}.md"
                (base / "references" / rname).write_text(
                    f"# Reference {idx}\n\n" + " ".join(["term"] * 1450) + ".\n",
                    encoding="utf-8",
                )
                ref_links.append(f"[references/{rname}](references/{rname})")

            for mode in ("draft", "edit", "review", "lint"):
                (base / "commands" / f"write-{mode}.md").write_text(
                    f'---\ndescription: "Run {mode}"\n---\n\nUse `mode={mode}`.\n',
                    encoding="utf-8",
                )

            (base / "SKILL.md").write_text(
                "---\nname: writing\ndescription: \"Skill router\"\n---\n\n"
                "# Writing\n\n"
                "- `mode=draft` (`/write-draft`)\n"
                "- `mode=edit` (`/write-edit`)\n"
                "- `mode=review` (`/write-review`)\n"
                "- `mode=lint` (`/write-lint`): run `scripts/strip_markdown.py` and `scripts/prose_lint.py`.\n\n"
                "Load " + ", ".join(ref_links) + ".\n",
                encoding="utf-8",
            )

            res_9k = validate_skill.validate_repo(base)
            self.assertTrue(res_9k["passed"], f"Expected ~9k combined words to pass: {res_9k['errors']}")
            self.assertGreater(res_9k["word_counts"]["combined_runtime"], 8500)
            self.assertLessEqual(res_9k["word_counts"]["combined_runtime"], 10000)

        # Verify docs/spec/configuration.md, data-model.md, architecture.md, and behaviors.md
        config_text = (ROOT / "docs" / "spec" / "configuration.md").read_text(encoding="utf-8")
        self.assertIn("<= 10,000", config_text)
        self.assertIn("<= 1,500", config_text)
        self.assertNotIn("<= 8,500", config_text)

        data_model_text = (ROOT / "docs" / "spec" / "data-model.md").read_text(encoding="utf-8")
        for key in NEW_MECH_KEYS:
            self.assertIn(f'"{key}"', data_model_text)
        json_blocks = re.findall(r"```json\n(.*?)\n```", data_model_text, flags=re.DOTALL)
        self.assertGreaterEqual(len(json_blocks), 2)
        lint_schema_example = json.loads(json_blocks[1])
        self.assertEqual(
            set(lint_schema_example["mechanics_and_tells"].keys()),
            set(prose_lint.analyze_text("Clean test sentence.")["mechanics_and_tells"].keys()),
        )

        arch_text = (ROOT / "docs" / "spec" / "architecture.md").read_text(encoding="utf-8")
        self.assertIn("references/one-pager-and-six-pager.md", arch_text)

        behaviors_text = (ROOT / "docs" / "spec" / "behaviors.md").read_text(encoding="utf-8")
        self.assertIn("references/one-pager-and-six-pager.md", behaviors_text)
        self.assertIn("<=10,000", behaviors_text)
        self.assertNotIn("<=8,500", behaviors_text)

        # Ensure zero literal em dashes in modified scripts, tests, and spec files
        checked_paths = [
            LINT_CLI,
            ROOT / "scripts" / "validate_skill.py",
            ROOT / "docs" / "spec" / "configuration.md",
            ROOT / "docs" / "spec" / "data-model.md",
            ROOT / "docs" / "spec" / "architecture.md",
            ROOT / "docs" / "spec" / "behaviors.md",
            Path(__file__).resolve(),
        ]
        for p in checked_paths:
            self.assertNotIn(EM_DASH, p.read_text(encoding="utf-8"), f"Literal em dash in {p}")

        # Live repository validation passes cleanly
        live_val = validate_skill.validate_repo(ROOT)
        self.assertTrue(live_val["passed"], f"Live validate_skill failed: {live_val['errors']}")


if __name__ == "__main__":
    unittest.main()
