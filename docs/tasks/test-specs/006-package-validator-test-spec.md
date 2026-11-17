# Test Spec 006: Skill Package and Prose Hygiene Validator (`validate_skill.py`)

- **Task:** `docs/tasks/backlog/006-package-validator.md`
- **Test file:** `tests/test_task_006_validate_skill.py`

## Requirements

- **REQ-006-01:** `scripts/validate_skill.py` uses Python 3 stdlib only, accepts `--root DIR` and `--json`, exits `0` when all checks pass and `1` when any check fails, and validates `SKILL.md` frontmatter (`name`, `description`) plus word budgets (`SKILL.md <= 1500` words, each `references/*.md <= 1500` words, combined runtime `<= 8500` words).
- **REQ-006-02:** `scripts/validate_skill.py` checks routing reachability (every `references/*.md`, `commands/*.md`, and skill runtime script `strip_markdown.py` / `prose_lint.py` is referenced in `SKILL.md`), `mode=` token symmetry between `commands/write-*.md` and `SKILL.md`, and broken relative Markdown links across `SKILL.md`, `references/`, `commands/`, `README.md`, `AGENTS.md`, `CLAUDE.md`, and `docs/`.
- **REQ-006-03:** `scripts/validate_skill.py` validates `evals/evals.json` and `evals/trigger-evals.json` when present (structure, required keys, category/mode coverage).
- **REQ-006-04:** `scripts/validate_skill.py` enforces repository prose hygiene across authored Markdown files (`SKILL.md`, `commands/*.md`, `references/*.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/spec/*.md`, `docs/architecture/*.md`, `docs/plans/*.md`, `samples/*.after.md`, `evals/JUDGE.md`), flagging any prose `\u2014`, emoji bullets, or hard-wrapped paragraphs while exempting `.claude/`, `.agents/`, `CODE_OF_CONDUCT.md`, and `samples/*.before.md`.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-006-01` | `REQ-006-01` | Temp skill tree with valid vs over-budget `SKILL.md` / `references/*.md` | `validate_skill` passes valid tree and fails (`exit 1`) when `SKILL.md` or a reference exceeds 1,500 words |
| `TC-006-02` | `REQ-006-02` | Temp skill tree with unreferenced `references/orphan.md`, broken link, or mismatched `mode=foo` | `validate_skill` detects unrouted reference, broken Markdown link, and mismatched command `mode=` token |
| `TC-006-03` | `REQ-006-03` | Temp skill tree with malformed `evals/evals.json` | `validate_skill` reports schema failure when required eval fields or categories are missing |
| `TC-006-04` | `REQ-006-04` | Live repository root + temp tree containing prose `\u2014` or hard-wrapped lines | `validate_skill.py` passes (`exit 0`) on the live repository and fails (`exit 1`) when prose `\u2014` or hard-wrapped paragraphs are injected |
