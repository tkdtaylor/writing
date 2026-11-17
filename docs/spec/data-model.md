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
    "passive_voice_per_100w": 1.2,
    "adverbs_per_100w": 1.8,
    "nominalizations_per_100w": 0.0
  }
}
```

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
