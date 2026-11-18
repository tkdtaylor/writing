"""Unit and integration tests for Task 015: CLI Safety Hardening and Agent Model Tier Mapping.

Covers TC-015-01 through TC-015-03 from
docs/tasks/test-specs/015-cli-safety-and-agent-model-tiers-test-spec.md.
"""
from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import package_skill, prose_lint, validate_skill

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_CLI = ROOT / "scripts" / "package_skill.py"
SYNC_AGY_CLI = ROOT / "scripts" / "sync-agy-skills.py"
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
)

EXPECTED_CLAUDE_AGENT_MODELS = {
    "architect": "opus",
    "security-auditor": "opus",
    "code-reviewer": "sonnet",
    "qa": "sonnet",
    "spec-verifier": "sonnet",
    "task-planner": "sonnet",
    "task-executor": "sonnet",
    "docs-writer": "inherit",
}

EXPECTED_CLAUDE_AGENT_TIERS = {
    "architect": "deep",
    "security-auditor": "deep",
    "code-reviewer": "balanced",
    "qa": "balanced",
    "spec-verifier": "balanced",
    "task-planner": "balanced",
    "task-executor": "fast",
    "docs-writer": "fast",
}


def _run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )


def _extract_section(markdown_text: str, heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)"
    )
    match = pattern.search(markdown_text)
    if not match:
        raise AssertionError(f"Missing section heading: ### {heading}")
    return match.group(1)


class TestTask015CliSafetyAndModels(unittest.TestCase):
    """Verification suite for REQ-015-01..REQ-015-03 (TC-015-01..TC-015-03)."""

    def test_tc_015_01_package_skill_target_and_symlink_safety(self) -> None:
        """TC-015-01 (REQ-015-01): package_skill rejects unsafe install/clean targets and unlinks symlinks."""
        payload_files, errors = package_skill.collect_payload_manifest(ROOT)
        self.assertEqual(errors, [])

        # 1. Reject /, Path.home(), ROOT, and ROOT.parent via install_payload and CLI --install-to
        unsafe_targets = [
            Path("/"),
            Path.home(),
            ROOT,
            ROOT.parent,
        ]
        for unsafe_dir in unsafe_targets:
            with self.subTest(unsafe_target=str(unsafe_dir)):
                with self.assertRaises(OSError):
                    package_skill.install_payload(
                        ROOT, payload_files, unsafe_dir, clean=False
                    )
                proc = _run_cmd(
                    [
                        sys.executable,
                        str(PACKAGE_CLI),
                        "--install-to",
                        str(unsafe_dir),
                    ]
                )
                self.assertEqual(
                    proc.returncode,
                    2,
                    f"Expected exit code 2 for --install-to {unsafe_dir}, got {proc.returncode}",
                )
                self.assertIn("error:", proc.stderr)

        # Verify Path.home() rejection explicitly even when home is outside ROOT's ancestry
        with tempfile.TemporaryDirectory() as tmp_home:
            fake_home = Path(tmp_home) / "isolated-home"
            fake_home.mkdir()
            with patch.object(Path, "home", return_value=fake_home):
                with self.assertRaises(OSError):
                    package_skill.install_payload(
                        ROOT, payload_files, fake_home, clean=False
                    )
                stderr_buf = io.StringIO()
                with redirect_stderr(stderr_buf):
                    rc_home = package_skill.main(["--install-to", str(fake_home)])
                self.assertEqual(rc_home, 2)
                self.assertIn("error:", stderr_buf.getvalue())

        # 2. Reject --clean on collection directories {skills, commands, agents, plugins}
        with tempfile.TemporaryDirectory() as tmp_col:
            tmp_col_path = Path(tmp_col)
            for collection_name in ("skills", "commands", "agents", "plugins"):
                col_dir = tmp_col_path / collection_name
                sibling_file = col_dir / "other-skill" / "SKILL.md"
                sibling_file.parent.mkdir(parents=True, exist_ok=True)
                sibling_file.write_text("keep sibling skill\n", encoding="utf-8")

                with self.subTest(collection_dir=collection_name):
                    with self.assertRaises(OSError):
                        package_skill.install_payload(
                            ROOT, payload_files, col_dir, clean=True
                        )
                    proc_clean = _run_cmd(
                        [
                            sys.executable,
                            str(PACKAGE_CLI),
                            "--install-to",
                            str(col_dir),
                            "--clean",
                        ]
                    )
                    self.assertEqual(proc_clean.returncode, 2)
                    self.assertIn("error:", proc_clean.stderr)
                    self.assertTrue(
                        sibling_file.is_file(),
                        f"Sibling skill under {collection_name}/ must remain intact",
                    )
                    self.assertEqual(
                        sibling_file.read_text(encoding="utf-8"),
                        "keep sibling skill\n",
                    )

            # Normal skill folder names must still work cleanly with --clean
            for valid_rel in ("writing", "dirty-writing", "skills/writing"):
                valid_target = tmp_col_path / valid_rel
                valid_target.mkdir(parents=True, exist_ok=True)
                (valid_target / "stale.txt").write_text("stale\n", encoding="utf-8")

                proc_ok = _run_cmd(
                    [
                        sys.executable,
                        str(PACKAGE_CLI),
                        "--install-to",
                        str(valid_target),
                        "--clean",
                    ]
                )
                self.assertEqual(
                    proc_ok.returncode, 0, proc_ok.stdout + proc_ok.stderr
                )
                self.assertFalse((valid_target / "stale.txt").exists())
                self.assertTrue((valid_target / "SKILL.md").is_file())

        # 3. Pre-existing symlinks at destination files and subdirectories are unlinked
        # before writing so external targets keep their exact content and permissions.
        for use_clean in (False, True):
            with (
                self.subTest(symlink_clean_mode=use_clean),
                tempfile.TemporaryDirectory() as tmp_sym,
            ):
                sym_base = Path(tmp_sym)
                external_dir = sym_base / "external-secrets"
                external_dir.mkdir()

                ext_skill = external_dir / "external_skill.md"
                ext_skill.write_text("EXTERNAL_SKILL_SENTINEL\n", encoding="utf-8")
                os.chmod(ext_skill, 0o600)

                ext_script = external_dir / "external_lint.py"
                ext_script.write_text("# EXTERNAL_SCRIPT_SENTINEL\n", encoding="utf-8")
                os.chmod(ext_script, 0o600)

                ext_refs = external_dir / "external_refs"
                ext_refs.mkdir()
                ext_ref_doc = ext_refs / "draft-and-brief.md"
                ext_ref_doc.write_text("EXTERNAL_REF_SENTINEL\n", encoding="utf-8")
                os.chmod(ext_ref_doc, 0o600)

                install_dir = sym_base / "writing"
                (install_dir / "scripts").mkdir(parents=True)
                (install_dir / "SKILL.md").symlink_to(ext_skill)
                (install_dir / "scripts" / "prose_lint.py").symlink_to(ext_script)
                (install_dir / "references").symlink_to(
                    ext_refs, target_is_directory=True
                )

                cli_args = [
                    sys.executable,
                    str(PACKAGE_CLI),
                    "--install-to",
                    str(install_dir),
                ]
                if use_clean:
                    cli_args.append("--clean")

                sym_proc = _run_cmd(cli_args)
                self.assertEqual(
                    sym_proc.returncode, 0, sym_proc.stdout + sym_proc.stderr
                )

                # Installed paths must be real files/directories, not symlinks
                self.assertFalse((install_dir / "SKILL.md").is_symlink())
                self.assertFalse(
                    (install_dir / "scripts" / "prose_lint.py").is_symlink()
                )
                self.assertFalse((install_dir / "references").is_symlink())
                self.assertEqual(
                    (install_dir / "SKILL.md").read_bytes(),
                    (ROOT / "SKILL.md").read_bytes(),
                )
                self.assertEqual(
                    (install_dir / "scripts" / "prose_lint.py").read_bytes(),
                    (ROOT / "scripts" / "prose_lint.py").read_bytes(),
                )

                # External files must be completely untouched in content and mode
                self.assertEqual(
                    ext_skill.read_text(encoding="utf-8"),
                    "EXTERNAL_SKILL_SENTINEL\n",
                )
                self.assertEqual(stat.S_IMODE(ext_skill.stat().st_mode), 0o600)

                self.assertEqual(
                    ext_script.read_text(encoding="utf-8"),
                    "# EXTERNAL_SCRIPT_SENTINEL\n",
                )
                self.assertEqual(stat.S_IMODE(ext_script.stat().st_mode), 0o600)

                self.assertEqual(
                    ext_ref_doc.read_text(encoding="utf-8"),
                    "EXTERNAL_REF_SENTINEL\n",
                )
                self.assertEqual(stat.S_IMODE(ext_ref_doc.stat().st_mode), 0o600)

    def test_tc_015_02_validate_skill_inner_oserror_and_interfaces_spec(self) -> None:
        """TC-015-02 (REQ-015-02): validate_skill.main catches mid-scan OSError with exit 2 and interfaces.md matches."""
        stderr_perm = io.StringIO()
        with (
            patch.object(
                validate_skill,
                "validate_repo",
                side_effect=PermissionError(13, "Permission denied"),
            ),
            redirect_stderr(stderr_perm),
        ):
            rc_perm = validate_skill.main(["--root", str(ROOT)])

        self.assertEqual(rc_perm, 2)
        self.assertIn("error:", stderr_perm.getvalue())
        self.assertIn("Permission denied", stderr_perm.getvalue())

        stderr_mid = io.StringIO()
        with (
            patch.object(
                validate_skill,
                "_check_prose_hygiene",
                side_effect=OSError(5, "Input/output error"),
            ),
            redirect_stderr(stderr_mid),
        ):
            rc_mid = validate_skill.main(["--root", str(ROOT)])

        self.assertEqual(rc_mid, 2)
        self.assertIn("error:", stderr_mid.getvalue())
        self.assertIn("Input/output error", stderr_mid.getvalue())

        interfaces_path = ROOT / "docs" / "spec" / "interfaces.md"
        interfaces_text = interfaces_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, interfaces_text)

        for script_heading in (
            "`scripts/strip_markdown.py`",
            "`scripts/prose_lint.py`",
            "`scripts/validate_skill.py`",
            "`scripts/package_skill.py`",
        ):
            section = _extract_section(interfaces_text, script_heading)
            self.assertIn(
                "OSError",
                section,
                f"{script_heading} section in interfaces.md must document OSError exit code 2",
            )
            self.assertIn("`2`", section)

        lint_rep = prose_lint.analyze_text(
            interfaces_text, source="docs/spec/interfaces.md"
        )
        for tell_key in ALL_TELL_LIST_KEYS:
            self.assertEqual(
                lint_rep["mechanics_and_tells"][tell_key],
                [],
                f"interfaces.md triggered {tell_key}: {lint_rep['mechanics_and_tells'][tell_key]}",
            )

    def test_tc_015_03_agent_model_tiers_manifest_and_claude_md(self) -> None:
        """TC-015-03 (REQ-015-03): agent model tiers, Antigravity adapters, skill-manifest hashes, and CLAUDE.md align."""
        claude_agents_dir = ROOT / ".claude" / "agents"
        found_agents = {p.stem: p for p in sorted(claude_agents_dir.glob("*.md"))}
        self.assertEqual(set(found_agents.keys()), set(EXPECTED_CLAUDE_AGENT_MODELS.keys()))

        for agent_name, expected_model in EXPECTED_CLAUDE_AGENT_MODELS.items():
            agent_path = found_agents[agent_name]
            text = agent_path.read_text(encoding="utf-8")
            fm, _, has_fm = validate_skill.parse_frontmatter(text)
            self.assertTrue(has_fm, f"{agent_name}.md missing frontmatter")
            self.assertEqual(
                fm.get("model"),
                expected_model,
                f".claude/agents/{agent_name}.md expected model: {expected_model}, got {fm.get('model')}",
            )
            expected_tier = EXPECTED_CLAUDE_AGENT_TIERS[agent_name]
            self.assertRegex(
                text,
                rf"(?m)^# model-tier:\s*{re.escape(expected_tier)}\b",
                f".claude/agents/{agent_name}.md must preserve '# model-tier: {expected_tier}' comment",
            )

        # Antigravity sync check and mapped subagent models
        sync_proc = _run_cmd([sys.executable, str(SYNC_AGY_CLI), "--check"])
        self.assertEqual(
            sync_proc.returncode,
            0,
            f"sync-agy-skills.py --check failed:\n{sync_proc.stdout}\n{sync_proc.stderr}",
        )

        agy_agents_dir = ROOT / ".agents" / "agents"
        for agent_name, claude_model in EXPECTED_CLAUDE_AGENT_MODELS.items():
            agy_path = agy_agents_dir / f"{agent_name}.md"
            self.assertTrue(agy_path.is_file(), f"Missing {agy_path}")
            agy_fm, _, agy_has_fm = validate_skill.parse_frontmatter(
                agy_path.read_text(encoding="utf-8")
            )
            self.assertTrue(agy_has_fm)
            expected_agy_model = "pro" if claude_model == "opus" else "inherit"
            self.assertEqual(
                agy_fm.get("model"),
                expected_agy_model,
                f".agents/agents/{agent_name}.md expected model: {expected_agy_model}",
            )

        # Verify every installed_hash in .claude/skill-manifest.json matches SHA-256 on disk
        manifest_path = ROOT / ".claude" / "skill-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        tracked_files = manifest["create-project"]["files"]
        for agent_name in EXPECTED_CLAUDE_AGENT_MODELS:
            self.assertIn(f".claude/agents/{agent_name}.md", tracked_files)

        for rel_path, meta in tracked_files.items():
            disk_path = ROOT / rel_path
            self.assertTrue(disk_path.is_file(), f"Manifest file missing: {rel_path}")
            actual_sha = hashlib.sha256(disk_path.read_bytes()).hexdigest()
            self.assertEqual(
                meta.get("installed_hash"),
                actual_sha,
                f"SHA-256 mismatch in skill-manifest.json for {rel_path}",
            )
            self.assertRegex(meta.get("template_hash", ""), r"^[0-9a-f]{64}$")

        # Verify CLAUDE.md describes opus/sonnet/inherit tiers cleanly without tells or em dashes
        claude_md_path = ROOT / "CLAUDE.md"
        claude_md_text = claude_md_path.read_text(encoding="utf-8")
        self.assertNotIn(EM_DASH, claude_md_text)
        self.assertNotIn("all default to `model: inherit`", claude_md_text)
        for token in ("`opus`", "`sonnet`", "`inherit`"):
            self.assertIn(token, claude_md_text, f"CLAUDE.md missing {token}")

        claude_rep = prose_lint.analyze_text(claude_md_text, source="CLAUDE.md")
        for tell_key in ALL_TELL_LIST_KEYS:
            self.assertEqual(
                claude_rep["mechanics_and_tells"][tell_key],
                [],
                f"CLAUDE.md triggered {tell_key}: {claude_rep['mechanics_and_tells'][tell_key]}",
            )
        self.assertEqual(
            claude_rep["substance_and_posture"]["importance_without_mechanism"], []
        )
        self.assertEqual(claude_rep["cadence"]["overloaded_sentences"], [])

        # Self-hygiene check on this test module
        self.assertNotIn(EM_DASH, Path(__file__).resolve().read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
