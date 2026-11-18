# Test Spec 012: Negative Triggers, Dialect Consistency, and Formatter Precedence

- **Task:** `docs/tasks/backlog/012-negative-triggers-dialect-and-formatter-rules.md`
- **Test file:** `tests/test_task_012_triggers_dialect_formatters.py`

## Requirements

- **REQ-012-01:** `SKILL.md` frontmatter `description` includes an explicit `Don't use for...` negative-trigger boundary excluding code implementation or debugging, SQL or schema migrations, container or DevOps setup, security or malware scanning, and mechanical code auto-formatting, while keeping `SKILL.md <= 1,500` words.
- **REQ-012-02:** `SKILL.md` and `references/technical-and-docs.md` (`<= 1,500` words) specify English dialect consistency (`en-US` vs `en-GB`/`en-AU` within a document or repository) and explicitly forbid altering literal UI labels, API field names, config keys, CLI flags, or code identifiers when localizing prose.
- **REQ-012-03:** `SKILL.md` Step 3 and `docs/spec/configuration.md` clarify that continuous single-line paragraphs apply when no formatter governs the target repo, while configured project formatters (`prettier --prose-wrap always`, `mdformat`, `.editorconfig` line limits) take precedence under workspace rules.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-012-01` | `REQ-012-01` | `SKILL.md` YAML frontmatter | `description` contains `Don't use for` and names code/debugging, SQL/migrations, security scanning, and formatting exclusions; `SKILL.md <= 1500` words |
| `TC-012-02` | `REQ-012-02` | `SKILL.md` and `references/technical-and-docs.md` | Both specify single-dialect consistency (`en-US` / `en-GB`) and literal UI label / API field / CLI flag preservation; `technical-and-docs.md <= 1500` words |
| `TC-012-03` | `REQ-012-03` | `SKILL.md`, `docs/spec/configuration.md`, and `validate_skill.py` | Both document project formatter precedence (`mdformat`, `prettier --prose-wrap always`), zero prose `\u2014`, and `validate_skill.py` passes (`exit 0`) |
