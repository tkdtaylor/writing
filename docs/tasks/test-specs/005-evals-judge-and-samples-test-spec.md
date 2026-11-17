# Test Spec 005: Evaluation Suite (`evals/*`, `JUDGE.md`) and Calibration `samples/`

- **Task:** `docs/tasks/backlog/005-evals-judge-and-samples.md`
- **Test file:** `tests/test_task_005_evals_and_samples.py`

## Requirements

- **REQ-005-01:** `evals/evals.json` conforms to the `skill-creator` + `docs/spec/data-model.md` schema (`skill_name == "writing"`, `>= 12` eval cases) covering all 4 modes (`draft`, `edit`, `review`, `lint`) and all 6 safeguard categories (`factual_fidelity`, `medium_fit`, `false_positive_restraint`, `voice_sample_boundary`, `mode_boundary`, `prompt_injection_isolation`), each with non-empty `assertions`.
- **REQ-005-02:** `evals/trigger-evals.json` contains `>= 20` realistic queries (`>= 10` `should_trigger: true` across diverse writing jobs and `>= 10` `should_trigger: false` near-miss coding/data/ops queries).
- **REQ-005-03:** `evals/JUDGE.md` specifies a blinded A/B and single-output grading rubric with 4 hard fail gates (truth/attribution fidelity, mode boundary compliance, operational/medium preservation, prompt-injection immunity) and 6 scored dimensions (`1-5`), obeying repo prose hygiene.
- **REQ-005-04:** `samples/` contains `README.md`, `technical-doc.before.md` + `technical-doc.after.md`, and `executive-memo.before.md` + `executive-memo.after.md`, where each `.after.md` preserves concrete domain anchors while reducing mechanical/lexical tells to zero on em dashes, emoji bullets, bold-label restatements, AI-tell words, and framing theater when checked by `scripts/prose_lint.py`.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-005-01` | `REQ-005-01` | `evals/evals.json` | Valid JSON, `skill_name == "writing"`, `len(evals) >= 12`, covers all 4 modes and all 6 categories, unique IDs, non-empty `assertions` |
| `TC-005-02` | `REQ-005-02` | `evals/trigger-evals.json` | Valid JSON list of `>= 20` objects with `>= 10` `should_trigger == True` and `>= 10` `should_trigger == False`, each query `>= 40` chars |
| `TC-005-03` | `REQ-005-03` | `evals/JUDGE.md` | Exists, documents 4 hard gates and 6 scored dimensions, zero `\u2014` outside fenced code blocks |
| `TC-005-04` | `REQ-005-04` | `samples/*.before.md` vs `samples/*.after.md` via `prose_lint` | `.before.md` exhibits multiple tells; `.after.md` has zero `em_dashes`, `emoji_bullets`, `bold_restatement_bullets`, `ai_tell_words`, and `framing_theater`, while keeping `anchors_per_100w > 0` |
