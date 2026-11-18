# Test Spec 019: `prose_lint.py` Dash-Bypass, Chatbot-Artifact, and Meta/Strawman Detectors

- **Task:** `docs/tasks/backlog/019-prose-lint-humanizer-and-dash-bypass-detectors.md`
- **Verification target:** L5 (`make check` + `prose_lint.py` zero-false-positive sweep across repo Markdown files)

## Requirements and Test Cases

### `REQ-019-01`: Spaced `--` and spaced en-dash (`U+2013`) em-dash bypass detection

- **`TC-019-01`**: `scripts/prose_lint.py` `mechanics_and_tells["em_dashes"]` flags prose spaced double-hyphens (`word -- word`) and spaced en-dashes (`word \u2013 word`) alongside literal `U+2014` on inline-code-masked non-code, non-table lines, while ignoring YAML frontmatter `---`, Markdown table separator rows, CLI `--flag` tokens, inline backtick spans (such as `` `git checkout -- path` ``), and numeric ranges without surrounding prose dash spacing.

### `REQ-019-02`: `chatbot_artifacts` and `meta_and_strawman_tells` detectors (zero composite score)

- **`TC-019-02`**: `scripts/prose_lint.py` adds line-numbered list keys `chatbot_artifacts` (leaked chat wrappers like `Great question`, `I hope this helps`, `Happy to help`, `Let me know if you'd like me to`, `Certainly,` and cutoff/source hedges like `as of my last training update`, `while specific details are limited`) and `meta_and_strawman_tells` (self-describing layout narration like `This section is organized by`, `The table below compares`; stock closers like `Despite these challenges, ... continues to thrive`, `The future looks bright`; phantom strawmen like `Don't get me wrong`, `A tempting approach would be to`; and stacked negation lists like `No setup call, no templates, no spreadsheets`) to `mechanics_and_tells` and `format_human_report`, while ignoring inline code spans and literal double-quoted strings and emitting zero composite AI detector score fields.

### `REQ-019-03`: Spec synchronization and zero false positives across clean repository prose

- **`TC-019-03`**: `docs/spec/data-model.md`, `docs/spec/behaviors.md`, and `tests/test_task_004_prose_lint.py` stay synchronized with the expanded `mechanics_and_tells` schema, and running `prose_lint.analyze_text` across `SKILL.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `commands/*.md`, `references/*.md`, `samples/*.after.md`, `docs/spec/*.md`, `docs/architecture/*.md`, and `evals/JUDGE.md` produces `[]` on `em_dashes`, `chatbot_artifacts`, and `meta_and_strawman_tells`.
