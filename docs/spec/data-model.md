# Data Model

All diagnostic scripts and evaluation files exchange UTF-8 text or JSON using the structures below.

## 1. `strip_markdown.py --json` output

```json
{
  "source": "path-or-stdin",
  "text": "Clean reader-visible body prose separated by blank lines.",
  "paragraphs": ["Paragraph one.", "Paragraph two."],
  "headings": ["Heading one", "Heading two"],
  "hard_wrapped_lines": [14, 15],
  "word_count": 42
}
```

## 2. `prose_lint.py --json` output

No composite score field is permitted. Output keys:

```json
{
  "source": "path-or-stdin",
  "word_count": 320,
  "sentence_count": 18,
  "paragraph_count": 5,
  "cadence": {
    "mean_sentence_words": 17.8,
    "body_sentence_cv": 0.46,
    "paragraph_word_cv": 0.38,
    "cadence_masking": false,
    "overloaded_sentences": [{"line": 12, "words": 41, "excerpt": "..."}],
    "ari_grade": 10.4,
    "flesch_kincaid_grade": 9.8
  },
  "lexical_diversity": {
    "mattr_50": 0.74,
    "repeated_trigram_rate": 0.012,
    "repeated_trigrams": []
  },
  "substance_and_posture": {
    "anchors_per_100w": 4.1,
    "hedges_per_100w": 0.9,
    "boosters_per_100w": 0.3,
    "importance_without_mechanism": [],
    "hedge_booster_collisions": []
  },
  "mechanics_and_tells": {
    "em_dashes": [],
    "connector_colons": [],
    "bold_restatement_bullets": [],
    "emoji_bullets": [],
    "hard_wrapped_lines": [],
    "false_scales": [],
    "ai_tell_words": [],
    "inflated_style_verbs": [],
    "tech_buzz_nouns": [],
    "framing_theater": [],
    "contrastive_pivots": [],
    "participial_tail_puffery": [],
    "copula_avoidance": [],
    "rhetorical_qa_pivots": [],
    "performative_fragments": [],
    "stacked_questions": [],
    "shorthand_ambiguities": [],
    "exclamation_marks": [],
    "false_agency": [],
    "chatbot_artifacts": [],
    "meta_and_strawman_tells": [],
    "passive_voice_per_100w": 1.2,
    "adverbs_per_100w": 1.8,
    "nominalizations_per_100w": 0.0
  }
}
```

When `--profile` / `--mode` is set to a non-default genre (`technical`, `memo`, `one-pager`, `six-pager`, or `narrative`), the JSON report includes an additional `profile_checks` object (still with zero composite score fields):

```json
{
  "profile_checks": {
    "profile": "one-pager",
    "requested_profile": "memo",
    "passed": true,
    "body_word_count": 456,
    "appendix_stripped": false,
    "word_budget_range": [350, 550],
    "word_budget_ok": true,
    "prose_paragraph_share": 0.879,
    "min_prose_share": 0.8,
    "prose_density_ok": true,
    "date_time_issues": []
  }
}
```

Genre-specific fields inside `profile_checks`:

- `technical`: `overlong_steps` (`[{"line", "words", "excerpt"}]`) and `date_time_issues` (`[{"line", "match", "recommendation", "excerpt"}]`).
- `one-pager` / `six-pager` / `memo`: `body_word_count`, `appendix_stripped`, `word_budget_range` (`[350, 550]`, for `one-pager`) or `word_budget_max` (`2500`, for `six-pager`). Also emits `word_budget_ok`, `prose_paragraph_share`, `min_prose_share` (`0.8`), `prose_density_ok`, and `date_time_issues`.
- `narrative`: `prose_paragraph_share`, `min_prose_share` (`0.85`), `prose_density_ok`, `body_sentence_count`, `body_sentence_cv`, `min_body_sentence_cv` (`0.3`), and `cadence_ok`.

## 3. `evals/evals.json` schema (`skill-creator` compatible)

```json
{
  "skill_name": "writing",
  "evals": [
    {
      "id": 1,
      "eval_name": "descriptive-case-slug",
      "category": "factual_fidelity | medium_fit | false_positive_restraint | voice_sample_boundary | mode_boundary | prompt_injection_isolation",
      "mode": "draft | edit | review | lint",
      "prompt": "Realistic user request including source text or context",
      "expected_output": "Summary of expected behavior",
      "files": [],
      "assertions": [
        "Objectively checkable behavioral assertion"
      ]
    }
  ]
}
```

## 4. `evals/trigger-evals.json` schema

JSON array of `{"query": "<realistic user prompt>", "should_trigger": true | false}` entries covering both positive multi-genre writing requests and near-miss negative queries.
