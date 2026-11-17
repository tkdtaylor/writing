# Task 004: Zero-Dependency `strip_markdown.py` and `prose_lint.py` CLIs

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/004-prose-lint-and-stripper-cli-test-spec.md`

## Objective

Implement `scripts/strip_markdown.py` and `scripts/prose_lint.py` using only the Python 3.10+ standard library, fulfilling behavior `B-007`, `docs/spec/data-model.md`, and `docs/spec/interfaces.md`.

## Deliverables (exclusive file scope)

- `scripts/strip_markdown.py` (executable, mode `0755`)
- `scripts/prose_lint.py` (executable, mode `0755`)
- `tests/test_task_004_prose_lint.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks. Avoid literal `\u2014` characters in source files (use `\u2014` escape sequences in Python strings/regexes so style hooks stay clean).

## Implementation details

1. **`scripts/strip_markdown.py`:**
   - Provide an importable `strip_markdown(text: str, source: str = "<stdin>") -> dict` function plus CLI (`python3 scripts/strip_markdown.py [FILE] [--json]`).
   - Strip YAML frontmatter (`--- ... ---` at top of file), fenced code blocks (backticks and tildes), HTML comments, Markdown pipe tables, reference link definitions, image syntax (`![alt](url)`), inline HTML tags, and link URL targets (`[anchor](url)` -> `anchor`), plus inline emphasis/backtick wrappers where appropriate so word counts reflect reader-visible prose.
   - Separate ATX/Setext headings into `headings: list[str]` so short headings do not skew body sentence cadence.
   - Detect consecutive non-list, non-heading, non-quote, non-code prose lines that appear hard-wrapped (e.g., two or more adjacent prose lines where line `N` is 55-90 chars without terminal sentence punctuation or two trailing spaces and line `N+1` continues a lowercase/ordinary prose flow), recording 1-indexed line numbers in `hard_wrapped_lines`.
   - Exit `0` on success and `2` on missing file or bad CLI arguments.
2. **`scripts/prose_lint.py`:**
   - Provide an importable `analyze_text(text: str, source: str = "<stdin>", raw: bool = False) -> dict` function plus CLI (`python3 scripts/prose_lint.py [FILE ...] [--json] [--raw]`).
   - Mask fenced code blocks and YAML frontmatter before scanning raw lines for mechanical tells so code examples never trigger false positives.
   - Compute exact JSON schema fields from `docs/spec/data-model.md`:
     - `cadence`: `mean_sentence_words`, `body_sentence_cv` (coefficient of variation across sentences with `>= 8` words), `paragraph_word_cv`, `cadence_masking` (True when all-sentence CV exceeds `body_sentence_cv` by `>= 0.15` and `body_sentence_cv < 0.35`, showing short bullets/fragments are masking flat body sentences), `overloaded_sentences` (`> 35` words, with line, word count, excerpt), `ari_grade`, and `flesch_kincaid_grade`.
     - `lexical_diversity`: `mattr_50` (50-word moving-average type-token ratio, falling back to plain TTR when `< 50` words) and `repeated_trigram_rate` + `repeated_trigrams` (non-stopword-only or repeated content 3-grams appearing `>= 3` times, or `>= 2` times in texts `< 400` words).
     - `substance_and_posture`: `anchors_per_100w` (numbers/percentages/versions/units, quoted phrases, mid-sentence capitalized proper nouns/acronyms), `hedges_per_100w`, `boosters_per_100w`, `importance_without_mechanism` (sentences matching importance boosters like `pivotal`, `transformative`, `crucial`, `vital`, `paramount`, `underscores`, `testament` without mechanism markers like `because`, `by`, `through`, `when`, `reduces`, `increases`, `ms`, `%`, digits), and `hedge_booster_collisions` (sentences containing both a hedge and a booster).
     - `mechanics_and_tells`: line-numbered hits for `em_dashes` (`\u2014`), `connector_colons` (mid-sentence `: ` followed by a full independent clause that is not introducing a list, quote, or code/heading), `bold_restatement_bullets` (`- **Term:** Term ...` where the lead word repeats), `emoji_bullets`, `hard_wrapped_lines`, `false_scales` (`from X to Y` where X and Y are abstract nouns rather than numeric/temporal/spatial endpoints, flagged as review candidates), `ai_tell_words` (`delve`, `tapestry`, `realm`, `testament`, `meticulous`, `nestled`, `multifaceted`, `commendable`, `utilize`, `seamless`, `robust`, `pivotal`, `comprehensive`, `holistic`), `inflated_style_verbs` (`bolster`, `catalyze`, `grapple`, `spearhead`, `amplify`, `exemplify`, `underscore`, `foster`, `elevate`, `streamline`, `supercharge`), `tech_buzz_nouns` (`substrate`, `wedge`, `nexus`, `primitive`, `scaffolding`, `paradigm`, `flywheel`, `north star`), `framing_theater` (`it's worth noting`, `it is important to note`, `in today's`, `let's dive in`, `here's the twist`, `let that sink in`, `read that again`, `the key insight`, `at its core`, `here is where it gets interesting`, `in conclusion`), `contrastive_pivots` (`not just X, it's Y`, `not only X, but also Y`), `stacked_questions` (3+ consecutive question sentences), `passive_voice_per_100w`, and `adverbs_per_100w` (with a stoplist for non-adverb `-ly` words like `only`, `early`, `family`, `likely`, `supply`, `apply`, `reply`, `daily`).
   - **Hard invariant:** Never emit any composite "AI score" or detector probability key.
   - Human-readable mode prints a compact, actionable summary of metrics and top line-numbered findings. Exit `0` on valid runs and `2` on missing files or bad flags.

## Verification plan

- Write `tests/test_task_004_prose_lint.py` covering `TC-004-01` through `TC-004-04`.
- Run `make check` and confirm all tests pass cleanly.
