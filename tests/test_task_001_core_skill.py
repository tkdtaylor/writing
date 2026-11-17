"""Verification tests for Task 001: Core SKILL.md router and /write-* slash commands."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "SKILL.md"
COMMANDS_DIR = ROOT / "commands"

EXPECTED_MODES = ("draft", "edit", "review", "lint")
EXPECTED_REFERENCES = (
    "references/draft-and-brief.md",
    "references/edit-and-anti-slop.md",
    "references/review-rubric.md",
    "references/technical-and-docs.md",
    "references/business-and-executive.md",
    "references/longform-and-persuasion.md",
)
EXPECTED_SCRIPTS = (
    "scripts/strip_markdown.py",
    "scripts/prose_lint.py",
)
EXPECTED_REGISTERS = (
    "Argument",
    "Explanation",
    "Guide",
    "Reference",
    "Decision/Update",
    "Persuasion/Copy",
    "Narrative/Oral",
)

EMOJI_BULLET_RE = re.compile(
    r"^\s*(?:[-*+]|\d+\.)\s+"
    r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2700-\u27BF\uFE0F]"
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse simple top-of-file YAML frontmatter into key-value pairs and body."""
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    raw_fm, body = match.group(1), match.group(2)
    parsed: dict[str, str] = {}
    current_key: str | None = None
    folded_lines: list[str] = []

    def flush() -> None:
        nonlocal current_key, folded_lines
        if current_key is not None and folded_lines:
            parsed[current_key] = " ".join(folded_lines).strip()
        current_key = None
        folded_lines = []

    for line in raw_fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_key is not None:
            folded_lines.append(line.strip())
            continue
        flush()
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in {">", ">-", "|", "|-"}:
                current_key = key
            else:
                parsed[key] = val.strip('"').strip("'")
    flush()
    return parsed, body


def strip_fenced_code_blocks(text: str) -> list[tuple[int, str]]:
    """Return (1-based line_number, line) tuples outside fenced code blocks."""
    out: list[tuple[int, str]] = []
    fence_marker: str | None = None
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_match:
            token = fence_match.group(1)
            if fence_marker is None:
                fence_marker = token[0] * len(token)
                continue
            if stripped.startswith(fence_marker[0] * len(fence_marker)):
                fence_marker = None
                continue
        if fence_marker is None:
            out.append((idx, line))
    return out


class TestTask001CoreSkillAndCommands(unittest.TestCase):
    """Covers TC-001-01 through TC-001-06 from 001-core-skill-and-commands-test-spec.md."""

    def test_tc_001_01_skill_frontmatter(self) -> None:
        """TC-001-01 (REQ-001-01): SKILL.md exists with valid frontmatter and trigger description."""
        self.assertTrue(SKILL_PATH.is_file(), "SKILL.md must exist at repository root")
        text = SKILL_PATH.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        self.assertEqual(fm.get("name"), "writing")
        description = fm.get("description", "")
        self.assertGreaterEqual(len(description), 120)
        desc_lower = description.lower()
        for trigger in ("draft", "edit", "review", "lint"):
            self.assertIn(trigger, desc_lower, f"Description missing mode trigger: {trigger}")
        for genre_term in ("readme", "rfc", "memo", "decision brief", "email", "essay", "microcopy"):
            self.assertIn(genre_term, desc_lower, f"Description missing genre trigger: {genre_term}")
        self.assertTrue(body.strip(), "SKILL.md body must not be empty")

    def test_tc_001_02_skill_word_budget(self) -> None:
        """TC-001-02 (REQ-001-02): SKILL.md stays within the 400..1500 whitespace-split word budget."""
        text = SKILL_PATH.read_text(encoding="utf-8")
        word_count = len(text.split())
        self.assertGreaterEqual(word_count, 400, f"SKILL.md too thin ({word_count} words)")
        self.assertLessEqual(word_count, 1500, f"SKILL.md exceeds 1,500-word budget ({word_count} words)")

    def test_tc_001_03_deterministic_mode_and_genre_routing(self) -> None:
        """TC-001-03 (REQ-001-03): SKILL.md routes all 4 modes, 7 registers, 6 references, and 2 CLI scripts."""
        text = SKILL_PATH.read_text(encoding="utf-8")
        for mode in EXPECTED_MODES:
            self.assertIn(f"mode={mode}", text, f"Missing mode={mode} route in SKILL.md")
            self.assertIn(f"commands/write-{mode}.md", text, f"Missing command reference for {mode} in SKILL.md")
        for ref in EXPECTED_REFERENCES:
            self.assertIn(ref, text, f"Missing reference link/path in SKILL.md: {ref}")
        for script in EXPECTED_SCRIPTS:
            self.assertIn(script, text, f"Missing diagnostic script in SKILL.md: {script}")
        for register in EXPECTED_REGISTERS:
            self.assertIn(register, text, f"Missing register in SKILL.md routing table: {register}")

    def test_tc_001_04_six_universal_safeguards_and_hygiene_rules(self) -> None:
        """TC-001-04 (REQ-001-04): SKILL.md specifies all 6 universal safeguards and baseline mechanics."""
        text = SKILL_PATH.read_text(encoding="utf-8")
        lower = text.lower()
        # 1. Truth, claim strength, ownership
        self.assertIn("`may`", text)
        self.assertIn("attribution", lower)
        # 2. Untrusted text / prompt injection
        self.assertIn("untrusted", lower)
        self.assertIn("prompt injection", lower)
        # 3. Operational and medium preservation
        self.assertIn("disclaimer", lower)
        self.assertIn("accessibility", lower)
        # 4. Voice sample boundary
        self.assertIn("voice sample", lower)
        # 5. [TK] placeholders and neutral negative examples
        self.assertIn("[TK:", text)
        self.assertIn("negative example", lower)
        # 6. Single-pass anti-flattening and mode boundaries
        self.assertIn("single-pass", lower)
        self.assertIn("read-only", lower)
        # Precedence and Markdown mechanics
        self.assertIn("AGENTS.md", text)
        self.assertIn("CLAUDE.md", text)
        self.assertIn("continuous single line", lower)
        self.assertIn("two trailing spaces", lower)
        self.assertIn("blank line", lower)

    def test_tc_001_05_slash_command_wrappers(self) -> None:
        """TC-001-05 (REQ-001-05): commands/write-{draft,edit,review,lint}.md exist and pass mode=<token> $ARGUMENTS."""
        for mode in EXPECTED_MODES:
            cmd_path = COMMANDS_DIR / f"write-{mode}.md"
            self.assertTrue(cmd_path.is_file(), f"Missing slash command file: {cmd_path}")
            text = cmd_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            self.assertTrue(fm.get("description"), f"Missing description frontmatter in {cmd_path.name}")
            self.assertTrue(fm.get("argument-hint"), f"Missing argument-hint frontmatter in {cmd_path.name}")
            self.assertIn("writing", body)
            self.assertIn("$ARGUMENTS", body, f"Missing $ARGUMENTS in {cmd_path.name}")
            self.assertIn(f"mode={mode}", body, f"Missing mode={mode} in {cmd_path.name}")
            self.assertIn(f"mode={mode} $ARGUMENTS", body, f"Missing exact mode={mode} $ARGUMENTS in {cmd_path.name}")
            modes_in_body = set(re.findall(r"\bmode=([a-z]+)\b", body))
            self.assertEqual(
                modes_in_body,
                {mode},
                f"{cmd_path.name} should only pass mode={mode}, found {modes_in_body}",
            )
            # Check relative links inside commands/*.md resolve cleanly
            for link_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
                if link_target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                rel_path = link_target.split("#", 1)[0]
                resolved = (cmd_path.parent / rel_path).resolve()
                self.assertTrue(resolved.exists(), f"Broken relative link {link_target} in {cmd_path.name}")

    def test_tc_001_06_zero_em_dashes_and_zero_emoji_bullets(self) -> None:
        """TC-001-06 (REQ-001-06): SKILL.md and commands/write-*.md have zero prose U+2014 and zero emoji bullets."""
        targets = [SKILL_PATH] + [COMMANDS_DIR / f"write-{m}.md" for m in EXPECTED_MODES]
        for path in targets:
            self.assertTrue(path.is_file(), f"Missing file for hygiene check: {path}")
            text = path.read_text(encoding="utf-8")
            _, body = parse_frontmatter(text)
            non_code_lines = strip_fenced_code_blocks(body)
            prev_line = ""
            for line_no, line in non_code_lines:
                self.assertNotIn(
                    "\u2014",
                    line,
                    f"Prose em dash (U+2014) found in {path.name}:{line_no}: {line}",
                )
                self.assertIsNone(
                    EMOJI_BULLET_RE.search(line),
                    f"Emoji bullet found in {path.name}:{line_no}: {line}",
                )
                # Verify blank line before first list item after a non-list prose line
                is_list_item = bool(re.match(r"^\s*(?:[-*+]|\d+\.)\s+", line))
                prev_is_list = bool(re.match(r"^\s*(?:[-*+]|\d+\.)\s+", prev_line))
                if is_list_item and prev_line.strip() and not prev_is_list:
                    self.fail(
                        f"Missing blank line before list item in {path.name}:{line_no}: {line}"
                    )
                # Verify continuous single-line paragraphs (no consecutive plain prose lines)
                is_plain = (
                    bool(line.strip())
                    and not is_list_item
                    and not line.lstrip().startswith(("#", "|", ">"))
                )
                prev_is_plain = (
                    bool(prev_line.strip())
                    and not prev_is_list
                    and not prev_line.lstrip().startswith(("#", "|", ">"))
                )
                if is_plain and prev_is_plain and not prev_line.endswith("  "):
                    self.fail(
                        f"Hard-wrapped multi-line paragraph in {path.name}:{line_no}: {line}"
                    )
                prev_line = line


if __name__ == "__main__":
    unittest.main()
