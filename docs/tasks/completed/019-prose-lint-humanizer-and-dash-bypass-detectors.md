# Task 019: `prose_lint.py` Dash-Bypass, Chatbot-Artifact, and Meta/Strawman Detectors

- **Priority:** P0
- **Model tier:** `deep` (`pro`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/019-prose-lint-humanizer-and-dash-bypass-detectors-test-spec.md`

## Objective

Extend `scripts/prose_lint.py` to detect spaced `--` and spaced en-dash (`\u2013`) em-dash substitutes inside `em_dashes`, add `chatbot_artifacts` and `meta_and_strawman_tells` to `mechanics_and_tells` (with zero composite AI score and zero false positives across all clean repository Markdown files), and synchronize `docs/spec/{data-model,behaviors}.md` and `tests/test_task_004_prose_lint.py`.

## Deliverables (exclusive file scope)

- `scripts/prose_lint.py`
- `docs/spec/data-model.md`
- `docs/spec/behaviors.md`
- `tests/test_task_004_prose_lint.py`
- `tests/test_task_019_humanizer_detectors.py`

Do not modify files owned by Tasks 017, 018, or 020 (`SKILL.md`, `references/*.md`, `evals/*`, `README.md`, `CHANGELOG.md`, `tests/test_task_010*.py`, `tests/test_task_014*.py`, `tests/test_task_015*.py`, `tests/test_task_016*.py`, or `coverage-tracker.md`). Use `\u2014` and `\u2013` escape sequences in Python code (never literal em dashes).

## Implementation details

1. **Extend `em_dashes` in `scripts/prose_lint.py` (`REQ-019-01`):**
   - Alongside literal `\u2014`, scan inline-code-masked non-code, non-table, non-frontmatter prose lines for:
     - Spaced double-hyphen clause separators: `(?<=[A-Za-z0-9,)"'])\s+--\s+(?=[A-Za-z0-9"'(])`
     - Spaced en-dash clause separators: `\s+\u2013\s+`
   - Ensure CLI `--flag` tokens (`--profile`, `--install-to`), Markdown table separator rows (`|---|---|`), YAML frontmatter `---`, HTML comments `<!-- -->`, and inline code spans (`` `git checkout -- path` ``, `` `word -- word` ``) are NEVER flagged!
2. **Add `chatbot_artifacts` and `meta_and_strawman_tells` to `mechanics_and_tells` (`REQ-019-02`):**
   - Scan inline-code-masked and double-quote-masked (`"..."`) non-code prose lines (so literal quoted examples and inline-code tell examples never false-positive!):
   - `chatbot_artifacts`:
     - Leaked chat wrappers: `\b(?:great|excellent|wonderful)\s+question\b`, `\bi\s+hope\s+this\s+helps\b`, `\bhappy\s+to\s+help\b`, `\blet\s+me\s+know\s+if\s+you(?:'d\s+like|\s+want|\s+need)\b`, `\bwould\s+you\s+like\s+me\s+to\b`, `\bfeel\s+free\s+to\s+ask\b`, `^\s*(?:certainly|of\s+course|sure\s+thing)[,!.]`
     - Cutoff and source-hedging disclaimers: `\bas\s+of\s+my\s+(?:last\s+)?(?:knowledge|training)\s+(?:update|cutoff)\b`, `\bup\s+to\s+my\s+(?:last\s+)?(?:training|knowledge)\b`, `\bwhile\s+specific\s+details\s+are\s+(?:limited|scarce)\b`, `\bnot\s+(?:widely|extensively)\s+documented\s+in\s+(?:readily\s+)?available\s+sources\b`
   - `meta_and_strawman_tells`:
     - Self-describing layout narration: `\bthis\s+(?:section|document|guide|page)\s+is\s+organized\s+by\b`, `\bthe\s+table\s+below\s+(?:compares|lists|summarizes|shows)\b`, `\bthe\s+figures\s+below\s+(?:are|were)\s+(?:compiled|drawn)\s+from\b`
     - Stock outlook closers: `\bdespite\s+these\s+challenges,\s+[^.?!]{1,80}\bcontinues\s+to\s+thrive\b`, `\bthe\s+future\s+looks\s+(?:bright|promising)\b`, `\bexciting\s+times\s+lie\s+ahead\b`
     - Phantom strawmen ("arguing with no one"): `\bdon't\s+get\s+me\s+wrong\b`, `\bi'm\s+not\s+saying\s+that\b`, `\b(?:a\s+tempting|an\s+obvious)\s+approach\s+would\s+be\s+to\b`, `\bone\s+might\s+be\s+tempted\s+to\b`
     - Stacked negation lists: `\bno\s+[a-z][a-z -]{1,24},\s+no\s+[a-z][a-z -]{1,24},\s+(?:and\s+)?no\s+[a-z]` (case-insensitive)
   - Surface non-empty hits for `chatbot_artifacts` and `meta_and_strawman_tells` in `format_human_report` with `[chatbot_artifacts]` and `[meta_and_strawman_tells]` labels. Never emit any composite AI score field.
3. **Sync `docs/spec/{data-model,behaviors}.md` and `tests/test_task_004_prose_lint.py` (`REQ-019-03`):**
   - Add `"chatbot_artifacts": [],` and `"meta_and_strawman_tells": [],` to the JSON example in `docs/spec/data-model.md` (remember `test_task_009_flourish_lint.py` parses that exact JSON block and asserts exact key set equality!).
   - Document spaced `--` / en-dash detection, `chatbot_artifacts`, and `meta_and_strawman_tells` in `docs/spec/behaviors.md` (`B-007`), keeping every sentence `<= 35` words (`overloaded_sentences == []`) and zero `\u2014`!
   - Update `expected_mech_keys` in `tests/test_task_004_prose_lint.py`.
   - Sweep all clean repository Markdown files (`SKILL.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `commands/*.md`, `references/*.md`, `samples/*.after.md`, `docs/spec/*.md`, `docs/architecture/*.md`, `evals/JUDGE.md`) to confirm **zero false positives**!

## Verification plan

- Write `tests/test_task_019_humanizer_detectors.py` verifying `TC-019-01`..`TC-019-03`.
- Move this task file to `docs/tasks/completed/019-prose-lint-humanizer-and-dash-bypass-detectors.md` via `git mv`.
- Run `make check` and confirm exit `0`.
