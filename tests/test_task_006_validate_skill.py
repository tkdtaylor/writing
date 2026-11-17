"""Unit and CLI integration tests for Task 006: scripts/validate_skill.py.

Covers TC-006-01 through TC-006-04 from
docs/tasks/test-specs/006-package-validator-test-spec.md.
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
from typing import Any

from scripts import validate_skill

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_CLI = ROOT / "scripts" / "validate_skill.py"
EM_DASH = "\u2014"
ROCKET_EMOJI = "\U0001f680"


def _run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def _create_valid_skill_tree(base: Path) -> Path:
    """Populate a minimal, valid skill package tree inside base."""
    (base / "references").mkdir(parents=True, exist_ok=True)
    (base / "commands").mkdir(parents=True, exist_ok=True)
    (base / "scripts").mkdir(parents=True, exist_ok=True)
    (base / "docs" / "spec").mkdir(parents=True, exist_ok=True)

    (base / "scripts" / "strip_markdown.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
    (base / "scripts" / "prose_lint.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )

    (base / "references" / "draft-and-brief.md").write_text(
        "# Draft and Brief\n\nRestate the pictured reader and job before drafting.\n",
        encoding="utf-8",
    )
    (base / "references" / "technical-and-docs.md").write_text(
        "# Technical Docs\n\nSeparate tutorials, how-to guides, reference, and explanation.\n",
        encoding="utf-8",
    )

    for mode in ("draft", "edit", "review", "lint"):
        (base / "commands" / f"write-{mode}.md").write_text(
            "---\n"
            f'description: "Run {mode} workflow mode"\n'
            "---\n\n"
            f"Invoke [SKILL.md](../SKILL.md) with `mode={mode} $ARGUMENTS`.\n",
            encoding="utf-8",
        )

    (base / "SKILL.md").write_text(
        "---\n"
        "name: writing\n"
        'description: "Draft, edit, review, and lint clear human prose across technical and business genres."\n'
        "---\n\n"
        "# Writing\n\n"
        "Route each request deterministically before applying style rules:\n\n"
        "- `mode=draft` ([commands/write-draft.md](commands/write-draft.md)): load [references/draft-and-brief.md](references/draft-and-brief.md) and [references/technical-and-docs.md](references/technical-and-docs.md).\n"
        "- `mode=edit` ([commands/write-edit.md](commands/write-edit.md)): load [references/draft-and-brief.md](references/draft-and-brief.md).\n"
        "- `mode=review` ([commands/write-review.md](commands/write-review.md)): load [references/technical-and-docs.md](references/technical-and-docs.md).\n"
        "- `mode=lint` ([commands/write-lint.md](commands/write-lint.md)): run [scripts/strip_markdown.py](scripts/strip_markdown.py) and [scripts/prose_lint.py](scripts/prose_lint.py).\n",
        encoding="utf-8",
    )

    (base / "README.md").write_text(
        "# writing\n\nSee [SKILL.md](SKILL.md) and [docs/spec/SPEC.md](docs/spec/SPEC.md#overview).\n",
        encoding="utf-8",
    )
    (base / "docs" / "spec" / "SPEC.md").write_text(
        "# Specification\n\n## Overview\n\nCurrent package specification.\n",
        encoding="utf-8",
    )
    return base


def _make_valid_evals_payload(skill_name: str = "writing") -> dict[str, Any]:
    categories = [
        "factual_fidelity",
        "medium_fit",
        "false_positive_restraint",
        "voice_sample_boundary",
        "mode_boundary",
        "prompt_injection_isolation",
    ]
    modes = ["draft", "edit", "review", "lint", "edit", "review"]
    cases = []
    for idx, (cat, mode) in enumerate(zip(categories, modes), start=1):
        cases.append(
            {
                "id": idx,
                "eval_name": f"case-{idx}-{cat}",
                "category": cat,
                "mode": mode,
                "prompt": f"Sample prompt {idx} for {cat}.",
                "expected_output": f"Expected behavior for {cat}.",
                "files": [],
                "assertions": [f"Verifies {cat} in {mode} mode."],
            }
        )
    return {"skill_name": skill_name, "evals": cases}


class TestTask006ValidateSkill(unittest.TestCase):
    """Verification suite for REQ-006-01..REQ-006-04 (TC-006-01..TC-006-04)."""

    def test_tc_006_01_stdlib_cli_frontmatter_and_word_budgets(self) -> None:
        """TC-006-01 (REQ-006-01): stdlib-only CLI, frontmatter checks, and word budgets."""
        self.assertTrue(VALIDATOR_CLI.is_file(), "scripts/validate_skill.py must exist")
        self.assertTrue(
            os.access(VALIDATOR_CLI, os.X_OK),
            "scripts/validate_skill.py must be executable (0755)",
        )

        source = VALIDATOR_CLI.read_text(encoding="utf-8")
        self.assertNotIn(
            EM_DASH,
            source,
            "validate_skill.py must use \\u2014 escapes rather than literal em dashes",
        )
        tree = ast.parse(source, filename=str(VALIDATOR_CLI))
        allowed_local = {"scripts", "strip_markdown"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    self.assertTrue(
                        top in sys.stdlib_module_names or top in allowed_local,
                        f"Non-stdlib import disallowed: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                self.assertTrue(
                    top in sys.stdlib_module_names or top in allowed_local,
                    f"Non-stdlib from-import disallowed: {node.module}",
                )

        # CLI usage errors return exit code 2
        missing_root_proc = _run_validator("--root", "/nonexistent/skill/root/path")
        self.assertEqual(missing_root_proc.returncode, 2)
        bad_flag_proc = _run_validator("--unsupported-flag")
        self.assertEqual(bad_flag_proc.returncode, 2)

        # Valid skill tree passes (exit 0)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            res = validate_skill.validate_repo(root)
            self.assertTrue(res["passed"], f"Expected pass, got errors: {res['errors']}")
            self.assertEqual(res["errors"], [])

            cli_ok = _run_validator("--root", str(root), "--json")
            self.assertEqual(cli_ok.returncode, 0, cli_ok.stderr)
            parsed_json = json.loads(cli_ok.stdout)
            self.assertTrue(parsed_json["passed"])

        # Missing frontmatter or empty description fails (exit 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "SKILL.md").write_text(
                "---\nname: writing\ndescription: \"\"\n---\n\n# Body\n",
                encoding="utf-8",
            )
            res_empty_desc = validate_skill.validate_repo(root)
            self.assertFalse(res_empty_desc["passed"])
            self.assertTrue(
                any("description" in err for err in res_empty_desc["errors"])
            )

        # Over-budget SKILL.md (> 1500 words) fails with exit 1
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            skill_txt = (root / "SKILL.md").read_text(encoding="utf-8")
            padded = skill_txt + "\n" + " ".join(["word"] * 1510) + ".\n"
            (root / "SKILL.md").write_text(padded, encoding="utf-8")

            res_over = validate_skill.validate_repo(root)
            self.assertFalse(res_over["passed"])
            self.assertTrue(
                any("SKILL.md" in e and "1500" in e for e in res_over["errors"]),
                f"Expected SKILL.md budget error, got: {res_over['errors']}",
            )
            cli_fail = _run_validator("--root", str(root))
            self.assertEqual(cli_fail.returncode, 1)

        # Over-budget reference file (> 1500 words) fails with exit 1
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            ref_path = root / "references" / "draft-and-brief.md"
            ref_path.write_text(
                "# Draft\n\n" + " ".join(["token"] * 1505) + ".\n",
                encoding="utf-8",
            )
            res_ref = validate_skill.validate_repo(root)
            self.assertFalse(res_ref["passed"])
            self.assertTrue(
                any(
                    "references/draft-and-brief.md" in e and "1500" in e
                    for e in res_ref["errors"]
                ),
                f"Expected reference budget error, got: {res_ref['errors']}",
            )
            self.assertEqual(_run_validator("--root", str(root)).returncode, 1)

        # Combined runtime prose (> 10000 words across individually valid files) fails
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            extra_links: list[str] = []
            for idx in range(1, 8):
                name = f"extra-{idx}.md"
                (root / "references" / name).write_text(
                    f"# Extra {idx}\n\n" + " ".join(["detail"] * 1450) + ".\n",
                    encoding="utf-8",
                )
                extra_links.append(f"[references/{name}](references/{name})")
            skill_txt = (root / "SKILL.md").read_text(encoding="utf-8")
            (root / "SKILL.md").write_text(
                skill_txt + "\nSee also " + ", ".join(extra_links) + ".\n",
                encoding="utf-8",
            )
            res_combined = validate_skill.validate_repo(root)
            self.assertFalse(res_combined["passed"])
            self.assertTrue(
                any("10000" in e for e in res_combined["errors"]),
                f"Expected combined 10000-word error, got: {res_combined['errors']}",
            )

    def test_tc_006_02_routing_reachability_links_and_mode_symmetry(self) -> None:
        """TC-006-02 (REQ-006-02): orphan references, broken links, and mode= token symmetry."""
        # 1. Unreferenced references/orphan.md
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "references" / "orphan.md").write_text(
                "# Orphan Guide\n\nNot linked from SKILL.md.\n", encoding="utf-8"
            )
            res = validate_skill.validate_repo(root)
            self.assertFalse(res["passed"])
            self.assertTrue(
                any("references/orphan.md" in e for e in res["errors"]),
                f"Expected orphan reference failure, got: {res['errors']}",
            )

        # 2. Unreferenced command file and missing runtime script reference
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "commands" / "orphan-cmd.md").write_text(
                "# Orphan Command\n\nUnused wrapper.\n", encoding="utf-8"
            )
            skill_txt = (root / "SKILL.md").read_text(encoding="utf-8")
            (root / "SKILL.md").write_text(
                skill_txt.replace(
                    "and [scripts/prose_lint.py](scripts/prose_lint.py)", ""
                ),
                encoding="utf-8",
            )
            res = validate_skill.validate_repo(root)
            self.assertFalse(res["passed"])
            self.assertTrue(any("commands/orphan-cmd.md" in e for e in res["errors"]))
            self.assertTrue(any("prose_lint.py" in e for e in res["errors"]))

        # 3. Mismatched mode=foo in commands/write-draft.md
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "commands" / "write-draft.md").write_text(
                "---\n"
                'description: "Broken mode token"\n'
                "---\n\n"
                "Invoke [SKILL.md](../SKILL.md) with `mode=foo $ARGUMENTS`.\n",
                encoding="utf-8",
            )
            res = validate_skill.validate_repo(root)
            self.assertFalse(res["passed"])
            self.assertTrue(
                any("mode=foo" in e or "write-draft.md" in e for e in res["errors"]),
                f"Expected mode=foo mismatch error, got: {res['errors']}",
            )

        # 4. Broken relative Markdown link vs ignored external/anchor/code links
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "README.md").write_text(
                "# writing\n\n"
                "Valid external [site](https://example.com/docs), [mail](mailto:test@example.com), "
                "[anchor](#overview), inline code `[fake](missing-inline.md)`, and comment "
                "<!-- [comment](missing-comment.md) -->.\n\n"
                "```markdown\n"
                "[fenced](missing-fenced.md)\n"
                "```\n",
                encoding="utf-8",
            )
            res_clean = validate_skill.validate_repo(root)
            self.assertTrue(
                res_clean["passed"],
                f"Code/external/anchor links must not fail: {res_clean['errors']}",
            )

            (root / "README.md").write_text(
                "# writing\n\nBroken link to [missing guide](docs/missing-guide.md#sec).\n",
                encoding="utf-8",
            )
            res_broken = validate_skill.validate_repo(root)
            self.assertFalse(res_broken["passed"])
            self.assertTrue(
                any("missing-guide.md" in e for e in res_broken["errors"]),
                f"Expected broken relative link error, got: {res_broken['errors']}",
            )

    def test_tc_006_03_eval_and_trigger_json_schemas(self) -> None:
        """TC-006-03 (REQ-006-03): evals/evals.json and evals/trigger-evals.json schema validation."""
        # 1. Valid evals.json and trigger-evals.json pass
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "evals").mkdir(parents=True, exist_ok=True)
            (root / "evals" / "evals.json").write_text(
                json.dumps(_make_valid_evals_payload(), indent=2),
                encoding="utf-8",
            )
            (root / "evals" / "trigger-evals.json").write_text(
                json.dumps(
                    [
                        {"query": "Rewrite this memo with BLUF clarity", "should_trigger": True},
                        {"query": "Implement a binary search tree in Rust", "should_trigger": False},
                    ],
                    indent=2,
                ),
                encoding="utf-8",
            )
            res_ok = validate_skill.validate_repo(root)
            self.assertTrue(
                res_ok["passed"], f"Valid eval files failed: {res_ok['errors']}"
            )

        # 2. Missing required eval fields, duplicate IDs, and missing category/mode coverage fail
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "evals").mkdir(parents=True, exist_ok=True)
            bad_payload = _make_valid_evals_payload(skill_name="wrong-name")
            # Drop prompt_injection_isolation and lint coverage, duplicate ID, and drop assertions
            bad_payload["evals"] = bad_payload["evals"][:3]
            bad_payload["evals"][1]["id"] = 1
            del bad_payload["evals"][2]["assertions"]
            (root / "evals" / "evals.json").write_text(
                json.dumps(bad_payload), encoding="utf-8"
            )
            (root / "evals" / "trigger-evals.json").write_text(
                json.dumps([{"query": "Only positive trigger", "should_trigger": True}]),
                encoding="utf-8",
            )

            res_bad = validate_skill.validate_repo(root)
            self.assertFalse(res_bad["passed"])
            joined = "\n".join(res_bad["errors"])
            self.assertIn("skill_name", joined)
            self.assertIn("duplicate eval id", joined)
            self.assertIn("assertions", joined)
            self.assertIn("missing mode coverage", joined)
            self.assertIn("missing category coverage", joined)
            self.assertIn("should_trigger=false", joined)
            self.assertEqual(_run_validator("--root", str(root)).returncode, 1)

        # 3. Malformed JSON syntax fails cleanly with exit 1 (not traceback)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "evals").mkdir(parents=True, exist_ok=True)
            (root / "evals" / "evals.json").write_text("{not valid json", encoding="utf-8")
            cli_proc = _run_validator("--root", str(root))
            self.assertEqual(cli_proc.returncode, 1)
            self.assertIn("invalid JSON", cli_proc.stdout)

    def test_tc_006_04_live_repo_and_prose_hygiene_enforcement(self) -> None:
        """TC-006-04 (REQ-006-04): live repo passes exit 0; prose em dashes, emoji bullets, and hard wraps fail."""
        # 1. Live repository root must pass cleanly (exit 0)
        live_result = validate_skill.validate_repo(ROOT)
        self.assertTrue(
            live_result["passed"],
            f"Live repository failed validation: {live_result['errors']}",
        )
        self.assertEqual(live_result["errors"], [])
        self.assertLessEqual(live_result["word_counts"]["SKILL.md"], 1500)
        self.assertLessEqual(live_result["word_counts"]["combined_runtime"], 10000)
        for ref_name, ref_words in live_result["word_counts"]["references"].items():
            self.assertLessEqual(ref_words, 1500, f"{ref_name} exceeded 1500 words")

        live_cli = _run_validator()
        self.assertEqual(
            live_cli.returncode,
            0,
            f"CLI failed on live repo:\nstdout={live_cli.stdout}\nstderr={live_cli.stderr}",
        )

        # 2. Exempt paths (.claude/, .agents/, CODE_OF_CONDUCT.md, samples/*.before.md, docs/tasks/)
        #    and fenced code blocks do NOT fail prose hygiene
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            noisy_prose = (
                f"# Noisy Fixture {EM_DASH} Allowed Here\n\n"
                f"- {ROCKET_EMOJI} Emoji bullet in exempt fixture\n\n"
                "This line wraps right around column seventy-two in an exempted fixture\n"
                "so the validator confirms negative fixtures do not trigger errors.\n"
            )
            for rel_exempt in (
                ".claude/agents/helper.md",
                ".agents/skills/helper/SKILL.md",
                "CODE_OF_CONDUCT.md",
                "samples/demo.before.md",
                "docs/tasks/backlog/099-demo.md",
            ):
                target = root / rel_exempt
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(noisy_prose, encoding="utf-8")

            # Fenced code block containing em dash inside an authored file is allowed
            (root / "samples" / "demo.after.md").write_text(
                "# Clean Rewrite\n\n"
                "Single-line prose stays clean and direct.\n\n"
                "```python\n"
                f'RAW = "{EM_DASH}"\n'
                "```\n",
                encoding="utf-8",
            )
            res_exempt = validate_skill.validate_repo(root)
            self.assertTrue(
                res_exempt["passed"],
                f"Exempt paths or fenced blocks triggered false positive: {res_exempt['errors']}",
            )

        # 3. Prose em dash in authored Markdown fails (exit 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "README.md").write_text(
                f"# writing\n\nThis prose sentence contains an em dash {EM_DASH} outside code.\n",
                encoding="utf-8",
            )
            res_em = validate_skill.validate_repo(root)
            self.assertFalse(res_em["passed"])
            self.assertTrue(any("U+2014" in e for e in res_em["errors"]))
            self.assertEqual(_run_validator("--root", str(root)).returncode, 1)

        # 4. Emoji bullet line in authored Markdown fails (exit 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "evals").mkdir(parents=True, exist_ok=True)
            (root / "evals" / "JUDGE.md").write_text(
                f"# Judge Rubric\n\n- {ROCKET_EMOJI} Avoid decorative emoji bullets.\n",
                encoding="utf-8",
            )
            res_emoji = validate_skill.validate_repo(root)
            self.assertFalse(res_emoji["passed"])
            self.assertTrue(any("emoji bullet" in e for e in res_emoji["errors"]))

        # 5. Hard-wrapped multi-line paragraph in authored Markdown fails (exit 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = _create_valid_skill_tree(Path(tmp))
            (root / "README.md").write_text(
                "# writing\n\n"
                "This paragraph wraps around seventy-five characters on the first line so\n"
                "that the second line continues the exact same sentence without a break.\n",
                encoding="utf-8",
            )
            res_wrap = validate_skill.validate_repo(root)
            self.assertFalse(res_wrap["passed"])
            self.assertTrue(any("hard-wrapped" in e for e in res_wrap["errors"]))
            self.assertEqual(_run_validator("--root", str(root)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
