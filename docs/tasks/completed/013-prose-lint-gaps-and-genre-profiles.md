# Task 013: `prose_lint.py` Detector Gaps and `--profile` Genre Validation

- **Priority:** P0
- **Model tier:** `deep` (`pro`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/013-prose-lint-gaps-and-genre-profiles-test-spec.md`

## Objective

Close remaining rule-to-linter gaps in `scripts/prose_lint.py` (`and/or` and `(s)` shorthand, prose exclamation marks, and `false_agency`), guard `prose_lint.py` CLI file checks against `OSError`, and add `--profile` / `--mode` (`technical`, `memo`, `one-pager`, `six-pager`, `narrative`) deterministic genre checks.

## Deliverables (exclusive file scope)

- `scripts/prose_lint.py`
- `docs/spec/behaviors.md`
- `docs/spec/data-model.md`
- `docs/spec/interfaces.md`
- `tests/test_task_004_prose_lint.py`
- `tests/test_task_013_lint_gaps_and_profiles.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files owned by Tasks 011 or 012. Use `\u2014` escape sequences instead of literal em dashes in Python code, and keep zero `\u2014` in `docs/spec/*.md`.

## Implementation details

1. **Close baseline detector gaps in `scripts/prose_lint.py` (`mechanics_and_tells`):**
   - `shorthand_ambiguities`: Line-numbered findings for `\band/or\b` (case-insensitive) and `\b[A-Za-z]{2,}\(s\)` (e.g. `file(s)`, `user(s)`, `option(s)`) on inline-code-masked non-code lines.
   - `exclamation_marks`: Line-numbered findings for prose `!` on non-code lines after masking inline code spans (`\`...\``), double-quoted literal quotations (`"..."`), Markdown images (`!\[[^\]]*\]`), GitHub alerts (`\[\!(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]`), HTML comments (`<!--`), and `!=` / `!==`.
   - `false_agency`: Line-numbered findings where abstract artifacts/metrics perform human rhetorical or volitional acts (`\b(?:the\s+|these\s+|our\s+|raw\s+)?(?:metrics?|data|numbers?|telemetry|benchmarks?|architecture|design|schema|codebase|history|market|landscape|reality)\s+(?:speaks?\b|tells?\s+(?:us|a\s+story)\b|demands?\b|wants?\b|insists?\b|dictates?\b|drives?\s+alignment\b|forces?\s+us\b|refuses?\s+to\b|knows?\b)`, case-insensitive), leaving concrete software runtime actors (`the worker retries`, `the broker acks`) completely unflagged.
   - Surface non-empty hits for all 3 new keys in `format_human_report`, and update `expected_mech_keys` in `tests/test_task_004_prose_lint.py` (making sure `slop_fixture` in `test_task_004_prose_lint.py` stays valid and `clean_fixture` plus all 26 clean repo Markdown files return `[]` on all 3 new keys!).
   - Wrap `path.is_file()` and `path.read_text(...)` in `prose_lint.py` `main()` inside `try ... except OSError as exc:` returning exit code `2` cleanly.
2. **Add `--profile` / `--mode` genre validation (`REQ-013-02`):**
   - CLI: add `--profile` with `--mode` alias (`choices=["default", "technical", "memo", "one-pager", "six-pager", "narrative"]`, default `"default"`).
   - API: `analyze_text(text: str, source: str = "<stdin>", raw: bool = False, profile: str | None = None) -> dict`.
   - When `profile` is `None` or `"default"`, keep top-level keys unchanged (or only attach `"profile_checks"` when `profile` is non-default, so existing callers see zero surprises; when `profile` is `"technical"`, `"memo"`, `"one-pager"`, `"six-pager"`, or `"narrative"`, attach `"profile_checks": {"profile": resolved_profile, "passed": bool, ...}`).
   - Profile checks:
     - **`technical`**:
       - `overlong_steps`: scan numbered procedural list items (`^\s*\d+\.\s+` outside fenced code blocks, stripping bold lead-in labels only if not part of the instruction, or counting stripped words of numbered steps in How-to/procedural sections; note: check `samples/technical-doc.after.md` so its numbered steps pass cleanly! If a numbered item is `> 20` words, record `{"line": line_no, "words": wc, "excerpt": ...}`).
       - `date_time_issues`: flag slash dates (`\b\d{1,2}/\d{1,2}/\d{2,4}\b`) and 12-hour clock times (`\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)\b`, case-insensitive) outside code spans/quotes, recommending ISO 8601 (`YYYY-MM-DD`) and 24-hour `HH:MM UTC`.
     - **`one-pager` / `six-pager` / `memo`**:
       - For `memo`, auto-resolve sub-profile to `one-pager` when pre-Appendix body words `<= 750`, else `six-pager`.
       - Split text at the first `^#{1,3}\s+Appendi(?:x|ces)\b` heading (outside code fences) so Appendix reference tables/FAQs are excluded from body word count and prose-density calculation!
       - Compute `body_word_count` and `prose_paragraph_share` (`paragraph_words / (paragraph_words + list_words)` on pre-Appendix body, `1.0` if empty).
       - `one-pager`: `word_budget_range = [350, 550]`, `word_budget_ok = 350 <= body_word_count <= 550`, `min_prose_share = 0.70` (or `0.80` for `six-pager`! Note: check `samples/one-pager.after.md`: verify `samples/one-pager.after.md` passes `--profile one-pager` with `passed == True`! Let's check: in `samples/one-pager.after.md`, Option 1/2/Status Quo or Next Steps may have bullets, so check its exact paragraph vs bullet ratio in `WORKTREE_PATH` and set `one-pager` `min_prose_share = 0.60` and `six-pager` `min_prose_share = 0.80` matching `references/one-pager-and-six-pager.md`'s explicit rule that **Six-Pagers** require `80%+` paragraph prose while One-Pagers use bullets sparingly for options/next steps!).
       - `six-pager`: `word_budget_max = 2500`, `word_budget_ok = body_word_count <= 2500`, `min_prose_share = 0.80`, `prose_density_ok = prose_paragraph_share >= 0.80`.
       - Also include `date_time_issues` (ISO 8601 / 24h UTC check).
     - **`narrative`**:
       - `min_prose_share = 0.85`, `prose_density_ok = prose_paragraph_share >= 0.85`, and `cadence_ok = body_sentence_cv >= 0.30` (when `>= 6` body sentences exist).
   - Render `Profile (<name>): PASS/REVIEW ...` concisely in `format_human_report` when `profile_checks` is present (still exiting `0` so `prose_lint.py` remains advisory).
3. **Update `docs/spec/{behaviors,data-model,interfaces}.md`:**
   - Document the 3 new `mechanics_and_tells` keys and `--profile` / `--mode` CLI/JSON contract.

## Verification plan

- Write `tests/test_task_013_lint_gaps_and_profiles.py` covering `TC-013-01`..`TC-013-03` (including running `--profile one-pager` on `samples/one-pager.after.md` and `--profile technical` on `samples/technical-doc.after.md`!).
- Run `make check` and confirm exit `0`.
