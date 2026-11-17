# Test Spec 001: Core `SKILL.md` Router and `/write-*` Slash Commands

- **Task:** `docs/tasks/backlog/001-core-skill-and-commands.md`
- **Test file:** `tests/test_task_001_core_skill.py`

## Requirements

- **REQ-001-01:** `SKILL.md` exists at repo root with valid YAML frontmatter containing `name: writing` and a rich triggering `description` covering drafting, rewriting, reviewing, and linting prose across technical, business, and longform genres.
- **REQ-001-02:** `SKILL.md` stays within the 1,500-word context budget (`<= 1500` words).
- **REQ-001-03:** `SKILL.md` Step 0 routes `mode=draft`, `mode=edit`, `mode=review`, and `mode=lint` deterministically and links all 6 `references/*.md` files (`draft-and-brief.md`, `edit-and-anti-slop.md`, `review-rubric.md`, `technical-and-docs.md`, `business-and-executive.md`, `longform-and-persuasion.md`) plus `scripts/strip_markdown.py` and `scripts/prose_lint.py`.
- **REQ-001-04:** `SKILL.md` specifies all six shared safeguards (truth/ownership preservation, prompt-injection isolation, medium preservation, voice-sample boundary, `[TK]` placeholders + neutral negative examples, and single-pass anti-flattening) plus baseline Markdown hygiene rules.
- **REQ-001-05:** `commands/write-{draft,edit,review,lint}.md` exist, carry `description` and `argument-hint` frontmatter, and pass the matching `mode=<token>` and `$ARGUMENTS` to the `writing` skill.
- **REQ-001-06:** `SKILL.md` and `commands/write-*.md` contain zero prose em dashes (`U+2014`) and zero emoji bullets.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-001-01` | `REQ-001-01` | `SKILL.md` frontmatter | Parses YAML frontmatter; `name == "writing"`, `len(description) >= 120`, mentions draft/edit/review/lint triggers |
| `TC-001-02` | `REQ-001-02` | `SKILL.md` word count | Total whitespace-split words in `SKILL.md` is `>= 400` and `<= 1500` |
| `TC-001-03` | `REQ-001-03` | `SKILL.md` routing | Contains `mode=draft`, `mode=edit`, `mode=review`, `mode=lint` and explicit references to all 6 `references/*.md` files and both diagnostic scripts |
| `TC-001-04` | `REQ-001-04` | `SKILL.md` safeguards | Contains `[TK` placeholder convention, untrusted/prompt-injection safeguard, voice sample boundary, and single-pass anti-flattening rule |
| `TC-001-05` | `REQ-001-05` | `commands/write-*.md` | All 4 files exist with `description:` frontmatter, `$ARGUMENTS`, and matching `mode=draft|edit|review|lint` token |
| `TC-001-06` | `REQ-001-06` | `SKILL.md` and `commands/write-*.md` | Zero occurrences of `\u2014` outside fenced code blocks and zero emoji bullet prefixes |
