# Task 021: `prose_lint.py` Adversarial Edge-Case Fixes and `mixed_dialects` Detector

- **Priority:** P0
- **Model tier:** `deep` (`pro`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/021-prose-lint-edge-cases-and-mixed-dialects-test-spec.md`

## Objective

Fix the `--profile technical` `overlong_steps` false positive on bold-labeled conceptual enumerations (including `README.md`), close the `_TWELVE_HOUR_TIME_RE` trailing-period bug and three `_META_AND_STRAWMAN_TELLS_RE` pattern gaps, and add a deterministic zero-dependency `mixed_dialects` (`en-US` vs `en-GB`) detector to `scripts/prose_lint.py`.

## Deliverables (exclusive file scope)

- `scripts/prose_lint.py`
- `docs/spec/data-model.md`
- `docs/spec/behaviors.md`
- `tests/test_task_004_prose_lint.py`
- `tests/test_task_010_memo_samples_and_sync.py`
- `tests/test_task_014_clean_packaging.py`
- `tests/test_task_015_cli_safety_and_models.py`
- `tests/test_task_016_doc_and_diagram_sync.py`
- `tests/test_task_020_v13_evals_and_docs.py`
- `tests/test_task_021_adversarial_edge_cases.py`

Do not modify files owned by Task 022 (`CHANGELOG.md`, `README.md`, `AGENTS.md`, `docs/plans/roadmap.md`) or `coverage-tracker.md`. Use `\u2014` and `\u2013` escapes in Python code, and keep every sentence in `docs/spec/*.md` `<= 35` words (`overloaded_sentences == []`).

## Implementation details

1. **Exclude bold-lead conceptual enumerations from `_detect_overlong_steps` (`REQ-021-01`):**
   - Add `_BOLD_CONCEPT_ENUM_RE = re.compile(r"^\s*\d+[.)]\s+\*\*[^*\n]+?(?:[.:?!]\*\*|\*\*\s*(?:[.:?!)-]|$))")`.
   - In `_detect_overlong_steps`, check the raw (or code-unmasked) line `raw_lines[line_idx]`: if `_BOLD_CONCEPT_ENUM_RE.match(raw_line)` matches, skip it (`continue`), because items like `1. **Truth, claim strength, and attribution preservation.** ...` or `1. **BLUF:** ...` are titled conceptual enumerations rather than imperative procedural steps.
   - Verify that `prose_lint.py --profile technical README.md`, `SKILL.md`, `CONTRIBUTING.md`, `references/technical-and-docs.md`, and `samples/technical-doc.after.md` all return `overlong_steps == []`, while bare procedural steps `> 20` words (including steps starting with an unpunctuated bold action verb like `1. **Click** the regional console button...`) still trigger `overlong_steps`.
2. **Fix `_TWELVE_HOUR_TIME_RE` and `_META_AND_STRAWMAN_TELLS_RE` (`REQ-021-02`):**
   - Update `_TWELVE_HOUR_TIME_RE` to `r"(?<![\d.])\b\d{1,2}(?::\d{2})?\s*(?:[ap]\.m\.(?![A-Za-z0-9_])|[ap]m\b)"` (`re.IGNORECASE`) so `"We shipped 10/18/2026 at 3:30 PM."` matches `"3:30 PM"` (no trailing dot) while `"at 3:30 p.m. and"` still matches `"3:30 p.m."` (`test_task_013:207`).
   - Update `_META_AND_STRAWMAN_TELLS_RE` to:
     - Replace `\bi'm\s+not\s+saying\s+that\b` with `\bi(?:'m|\s+am)\s+not\s+saying\b`.
     - Add `\bthis\s+(?:isn't|is\s+not)\s+(?:really\s+|mainly\s+|just\s+)?about\b`.
     - Update stacked negations to `\bno\s+[a-z][a-z -]{1,24}(?:[,;]\s*|\.\s+)no\s+[a-z][a-z -]{1,24}(?:[,;]\s*(?:and\s+)?|\.\s+)no\s+[a-z][a-z-]*` (`re.IGNORECASE`) so both comma-separated and period-separated (`"No fluff. No filler. No jargon."`) 3-part negations are caught.
3. **Add deterministic `mixed_dialects` detector (`REQ-021-03`):**
   - Scan inline-code-masked, URL-masked, double-quote-masked non-code prose lines using identifier-safe word boundaries (`(?<![A-Za-z0-9_-])\b...\b(?![A-Za-z0-9_-])`) so `--color`, `organization_id`, and `"Color Picker"` never trigger false hits.
   - Use unambiguous US vs UK/Commonwealth word sets (excluding cross-dialect technical words like `program`, `disk`, `meter`, `license`, and `analyses`):
     - `-or` / `-our` (`color`/`colour`, `behavior`/`behaviour`, `favor`/`favour`, `flavor`/`flavour`, `honor`/`honour`, `humor`/`humour`, `labor`/`labour`, `neighbor`/`neighbour`, `rumor`/`rumour`, `vigor`/`vigour`, plus plurals/derivatives)
     - `-er` / `-re` (`center`/`centre`, `fiber`/`fibre`, `liter`/`litre`, `kilometer`/`kilometre`, `caliber`/`calibre`, `theater`/`theatre`, plus plurals/derivatives)
     - `-yze` / `-yse` (`analyze`/`analyse`, `analyzed`/`analysed`, `analyzing`/`analysing`, `analyzer`/`analyser`, `catalyze`/`catalyse`, `paralyze`/`paralyse`)
     - `-ize` & `-ization` / `-ise` & `-isation` (`organize`/`organise`, `organization`/`organisation`, `optimize`/`optimise`, `optimization`/`optimisation`, `prioritize`/`prioritise`, `standardize`/`standardise`, `normalize`/`normalise`, `minimize`/`minimise`, `maximize`/`maximise`, `summarize`/`summarise`, `customize`/`customise`, `recognize`/`recognise`, `authorize`/`authorise`, `initialize`/`initialise`, `utilize`/`utilise`, `localize`/`localise`, `serialize`/`serialise`, `synchronize`/`synchronise`, `visualize`/`visualise`, plus `-ed`/`-ing`/`-s`/`-ations` inflections)
     - Lexical pairs: `gray`/`grey`, `skeptical`/`sceptical`, `artifact`/`artefact`, `artifacts`/`artefacts`, `defense`/`defence`, `catalog`/`catalogue`, `traveled`/`travelled`, `canceled`/`cancelled`, `labeled`/`labelled`, `modeling`/`modelling`, `fulfill`/`fulfil`, `fulfillment`/`fulfilment`, `enrollment`/`enrolment`.
   - When BOTH `us_hits` and `uk_hits` are non-empty across the document, determine `dominant_dialect = "en-US" if len(us_hits) >= len(uk_hits) else "en-GB"` and emit line-numbered dicts for the minority-side occurrences (`{"line": line_no, "match": word, "dialect": minority_dialect, "dominant_dialect": dominant_dialect, "us_samples": ..., "uk_samples": ..., "excerpt": ...}`).
   - Render `[mixed_dialects]` in `format_human_report`, update `docs/spec/data-model.md`, `docs/spec/behaviors.md`, `expected_mech_keys` in `tests/test_task_004_prose_lint.py`, and `ALL_TELL_LIST_KEYS` in `test_task_010`, `014`, `015`, `016`, and `020`.

## Verification plan

- Write `tests/test_task_021_adversarial_edge_cases.py` covering `TC-021-01`..`TC-021-03` (including sweeping all clean repo Markdown files).
- Move this task file to `docs/tasks/completed/021-prose-lint-edge-cases-and-mixed-dialects.md` via `git mv`.
- Run `make check` and confirm exit `0`.
