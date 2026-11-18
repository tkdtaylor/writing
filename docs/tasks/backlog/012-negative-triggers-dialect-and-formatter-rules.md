# Task 012: Negative Triggers, Dialect Consistency, and Formatter Precedence

- **Priority:** P0
- **Model tier:** `balanced` (`inherit`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/012-negative-triggers-dialect-and-formatter-rules-test-spec.md`

## Objective

Sharpen `SKILL.md` trigger accuracy with explicit `Don't use for...` negative routing boundaries, add English dialect consistency and literal UI/API/CLI preservation rules to `SKILL.md` and `references/technical-and-docs.md`, and clarify how continuous single-line paragraphs interact with target-project formatters (`mdformat`, `prettier --prose-wrap always`).

## Deliverables (exclusive file scope)

- `SKILL.md`
- `references/technical-and-docs.md`
- `docs/spec/configuration.md`
- `tests/test_task_012_triggers_dialect_formatters.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files owned by Tasks 011 or 013. Preserve all existing `TC-001`, `TC-003`, and `TC-008` assertions and keep `SKILL.md <= 1,500` words and `references/technical-and-docs.md <= 1,500` words.

## Implementation details

1. **Negative triggers in `SKILL.md` frontmatter (`REQ-012-01`):**
   - Append a concise `Don't use for...` sentence at the end of `description:` in `SKILL.md`: `"Don't use for writing or debugging application code, SQL or schema migrations, container or CI/CD setup, security or vulnerability scanning, or running code and Markdown auto-formatters."`
2. **Dialect consistency and literal UI/API/CLI exemption (`REQ-012-02`):**
   - In `references/technical-and-docs.md` Layer 4 (`Global English disambiguation`) and `SKILL.md` Step 3 (`Prefer plain words and one term per concept` or a dedicated bullet), add the rule: stay consistent within one English dialect (`en-US` vs `en-GB` or `en-AU` spelling, punctuation, and date conventions) across a document or repository rather than mixing dialects mid-piece, and **never** localize or respell literal UI labels, API field names, config keys, CLI flags, or code identifiers (for example, keep `--color` or `organization_id` exact even inside `en-GB` prose).
3. **Hard-wrapped paragraphs vs project formatters (`REQ-012-03`):**
   - In `SKILL.md` Step 3 (`Format Markdown cleanly`) and `docs/spec/configuration.md` (`House-style and voice overrides`), clarify that continuous single-line paragraphs are the baseline default when no formatter governs the target repository; when a target repository configures a prose formatter (`prettier --prose-wrap always`, `mdformat`, or `.editorconfig` / `markdownlint` line-length rules), that workspace formatter takes precedence under Step 3 item 2.
4. **Prose hygiene:**
   - Zero literal `\u2014` characters, zero emoji bullets, continuous single-line paragraphs, blank line before lists, zero `prose_lint.py` tells (`[]` across all tell keys and `0` overloaded `>35`w sentences if possible).

## Verification plan

- Write `tests/test_task_012_triggers_dialect_formatters.py` covering `TC-012-01`..`TC-012-03`.
- Run `make check` and `python3 scripts/prose_lint.py SKILL.md references/technical-and-docs.md` and confirm exit `0`.
