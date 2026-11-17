# Test Spec 004: Zero-Dependency `strip_markdown.py` and `prose_lint.py` CLIs

- **Task:** `docs/tasks/backlog/004-prose-lint-and-stripper-cli.md`
- **Test file:** `tests/test_task_004_prose_lint.py`

## Requirements

- **REQ-004-01:** `scripts/strip_markdown.py` uses Python 3 stdlib only, strips YAML frontmatter, fenced code blocks, HTML comments, Markdown tables, image tags, and link URL targets while preserving anchor text, separates headings from body paragraphs, detects hard-wrapped consecutive prose lines, and supports both plain-text and `--json` CLI output (file or stdin).
- **REQ-004-02:** `scripts/prose_lint.py` uses Python 3 stdlib only and computes `cadence` (`mean_sentence_words`, `body_sentence_cv` over sentences `>=8` words, `paragraph_word_cv`, `cadence_masking`, `overloaded_sentences`, `ari_grade`, `flesch_kincaid_grade`) and `lexical_diversity` (`mattr_50`, `repeated_trigram_rate`, `repeated_trigrams`).
- **REQ-004-03:** `scripts/prose_lint.py` computes `substance_and_posture` (`anchors_per_100w`, `hedges_per_100w`, `boosters_per_100w`, `importance_without_mechanism`, `hedge_booster_collisions`) and `mechanics_and_tells` (`em_dashes`, `connector_colons`, `bold_restatement_bullets`, `emoji_bullets`, `hard_wrapped_lines`, `false_scales`, `ai_tell_words`, `inflated_style_verbs`, `tech_buzz_nouns`, `framing_theater`, `contrastive_pivots`, `stacked_questions`, `passive_voice_per_100w`, `adverbs_per_100w`).
- **REQ-004-04:** `scripts/prose_lint.py` never emits a composite "AI score" key, ignores em dashes and tell words inside fenced code blocks, supports human-readable and `--json` CLI modes across single or multiple files plus stdin, and exits `0` on valid inputs and `2` on missing files.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-004-01` | `REQ-004-01` | Markdown fixture with frontmatter, code fence, table, links, and 80-col wrapped paragraph | `strip_markdown.py --json` strips code/table/frontmatter/URLs, keeps link anchor text, lists headings separately, and reports `hard_wrapped_lines` |
| `TC-004-02` | `REQ-004-02` | Uniform vs varied sentence-length prose fixtures + repeated phrase fixture | `prose_lint.py --json` reports higher `body_sentence_cv` on varied prose, flags `cadence_masking` when short bullets mask flat body sentences, and detects `repeated_trigrams` and `mattr_50` |
| `TC-004-03` | `REQ-004-03` | Slop-heavy Markdown fixture vs concrete anchored fixture | Detects `em_dashes`, `connector_colons`, `bold_restatement_bullets`, `emoji_bullets`, `false_scales`, `ai_tell_words`, `inflated_style_verbs`, `tech_buzz_nouns`, `framing_theater`, `contrastive_pivots`, `importance_without_mechanism`, and `hedge_booster_collisions` |
| `TC-004-04` | `REQ-004-04` | Code-fenced `\u2014` fixture + CLI subprocess calls (stdin, multi-file, missing file) | Code-fenced tells are ignored; JSON output has no composite score key; CLI exits `0` on valid input and `2` on nonexistent path |
