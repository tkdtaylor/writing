# Test Spec 021: `prose_lint.py` Adversarial Edge-Case Fixes and `mixed_dialects` Detector

- **Task:** `docs/tasks/backlog/021-prose-lint-edge-cases-and-mixed-dialects.md`
- **Verification target:** L5 (`make check` + `prose_lint.py --profile technical README.md` + `mixed_dialects` verification)

## Requirements and Test Cases

### `REQ-021-01`: `--profile technical` `overlong_steps` excludes bold-labeled conceptual enumerations

- **`TC-021-01`**: `scripts/prose_lint.py` `_detect_overlong_steps` skips numbered items that open with a bold conceptual title label (`1. **Truth and scope.** ...`, `1. **BLUF:** ...`, `1. **Scope** - ...`) so `prose_lint.py --profile technical README.md` (and `SKILL.md`, `CONTRIBUTING.md`, `references/technical-and-docs.md`, `samples/technical-doc.after.md`) return `overlong_steps == []`, while bare procedural steps exceeding `20` words (`1. Open the regional staging console...` or `1. **Click** the regional staging console button...`) still flag in `overlong_steps`.

### `REQ-021-02`: `_TWELVE_HOUR_TIME_RE` trailing-period fix and `_META_AND_STRAWMAN_TELLS_RE` gap closure

- **`TC-021-02`**: `_TWELVE_HOUR_TIME_RE` matches `"3:30 PM"` on `"We shipped 10/18/2026 at 3:30 PM."` without swallowing the sentence-ending period while still matching `"3:30 p.m."` when abbreviation periods are present; and `_META_AND_STRAWMAN_TELLS_RE` flags `"I'm not saying we should rewrite it."` (without requiring `that`), `"This isn't about speed, it's about reliability."`, and period- or semicolon-separated stacked negations (`"No fluff. No filler. No jargon."`).

### `REQ-021-03`: Deterministic `mixed_dialects` (`en-US` vs `en-GB`) detector in `prose_lint.py`

- **`TC-021-03`**: `scripts/prose_lint.py` adds `mixed_dialects` to `mechanics_and_tells` and `format_human_report`, deterministically flagging mixed US/UK prose (`"The organisation optimized color rendering while we analysed the behavior in our centre."`) while returning `[]` on consistent `en-US` prose, consistent `en-GB` prose, `en-GB` prose containing literal code/CLI/UI identifiers (`` `--color` ``, `` `organization_id` ``, `"Color Picker"`), and every clean Markdown file in the repository; `docs/spec/{data-model,behaviors}.md` and `ALL_TELL_LIST_KEYS` across `tests/` stay synchronized with zero composite score fields.
