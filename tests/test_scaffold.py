"""Repository scaffold invariants for the writing skill project."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestRepoScaffold(unittest.TestCase):
    def test_open_source_and_briefing_files_exist(self) -> None:
        required = [
            "LICENSE",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "Makefile",
            "docs/spec/SPEC.md",
            "docs/architecture/overview.md",
            "docs/architecture/diagrams.md",
            "docs/plans/roadmap.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).exists(), f"Missing scaffold file: {rel}")
        self.assertTrue((ROOT / "GEMINI.md").is_symlink(), "GEMINI.md must be a symlink to AGENTS.md")
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text(encoding="utf-8"))

    def test_skill_manifest_tracks_managed_files(self) -> None:
        manifest_path = ROOT / ".claude" / "skill-manifest.json"
        self.assertTrue(manifest_path.is_file())
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = data.get("create-project", {}).get("files", {})
        self.assertGreaterEqual(len(files), 35)
        for rel in files:
            self.assertTrue((ROOT / rel).is_file(), f"Tracked file missing: {rel}")


if __name__ == "__main__":
    unittest.main()
