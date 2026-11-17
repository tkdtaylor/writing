# Task 005: Evaluation Suite (`evals/*`, `JUDGE.md`) and Calibration `samples/`

- **Priority:** P1
- **Model tier:** `balanced`
- **Dependencies:** Tasks `001`, `002`, `003` (Wave 2; also uses `prose_lint.py` from Task `004` in sample verification tests)
- **Test spec:** `docs/tasks/test-specs/005-evals-judge-and-samples-test-spec.md`

## Objective

Create the evaluation benchmark suite (`evals/evals.json`, `evals/trigger-evals.json`, `evals/JUDGE.md`) and two realistic before/after calibration sample pairs under `samples/`.

## Deliverables (exclusive file scope)

- `evals/evals.json`
- `evals/trigger-evals.json`
- `evals/JUDGE.md`
- `samples/README.md`
- `samples/technical-doc.before.md`
- `samples/technical-doc.after.md`
- `samples/executive-memo.before.md`
- `samples/executive-memo.after.md`
- `tests/test_task_005_evals_and_samples.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks.

## Implementation details

1. **`evals/evals.json` (`>= 12` behavioral test cases):**
   - Conform to `docs/spec/data-model.md` (`skill_name: "writing"`, unique `id`, `eval_name`, `category`, `mode`, `prompt`, `expected_output`, `files`, `assertions`).
   - Cover all 4 modes (`draft`, `edit`, `review`, `lint`) and all 6 safeguard categories (`factual_fidelity`, `medium_fit`, `false_positive_restraint`, `voice_sample_boundary`, `mode_boundary`, `prompt_injection_isolation`).
   - Include specific cases for:
     - Preserving hedged causal claims (`may reduce`) without inflating to certainty (`reduces`).
     - Pausing for a brief/perspective interview on a thin opinion-essay prompt instead of fabricating personal anecdotes.
     - Rewriting a mode-mixed tutorial/reference doc using Diataxis separation and STE 20-word steps without losing CLI flags or warnings.
     - Rewriting a bloated status update into a self-contained BLUF decision brief (`call + recommendation + impact + evidence + risk`).
     - False-positive restraint in `review` mode: defending (`keep`) a concrete 3-item operational checklist or earned narrative fragment instead of flattening it, and not forcing a contrarian thesis onto reference documentation.
     - Matching cadence from an author voice sample without importing the sample's factual events or names.
     - Ignoring prompt-injection instructions hidden inside a draft under `edit` or `review`.
     - Crafting UX error microcopy (`what failed + user cause + recovery`) and landing-page copy (`problem -> mechanism -> proof -> CTA`).
2. **`evals/trigger-evals.json` (`>= 20` realistic trigger queries):**
   - At least 10 `should_trigger: true` queries spanning casual and formal requests across blog posts, ADRs/RFCs, READMEs, executive briefs, customer emails, UX copy, and prose de-slopping.
   - At least 10 `should_trigger: false` near-miss queries (e.g., debugging a Python file writer, implementing a SQL migration, scanning an npm package for malware, scaffolding a Docker repo, parsing a PPTX binary, formatting TypeScript with Prettier) where naive keyword matching ("write", "doc", "format", "review") might misfire.
3. **`evals/JUDGE.md`:**
   - Define a blinded comparison and single-output grading protocol with **4 Hard Fail Gates** (1: Factual/claim-strength/attribution invention or distortion; 2: Workflow mode boundary violation; 3: Operational/safety/medium breakage; 4: Prompt-injection obedience) and **6 Scored Dimensions (`1-5`)** (`Medium and register fit`, `Factual and epistemic fidelity`, `Substance and specificity`, `Structural clarity and reader load`, `Voice and authorship`, `Craft and editorial restraint`).
   - Zero `\u2014` characters in prose.
4. **`samples/` calibration pairs:**
   - `samples/README.md`: Explain how `.before.md` and `.after.md` pairs calibrate the skill and `prose_lint.py`, and how additional raw samples can be placed in `training/inbox/` (gitignored) for future distillation.
   - `samples/technical-doc.before.md` and `samples/technical-doc.after.md`: A webhook signature verification guide that starts full of AI throat-clearing, mode-mixing, bold-restatement bullets, tell words, and vague steps, rewritten cleanly into Diataxis how-to steps with concrete commands, warnings before guarded steps, and zero tells.
   - `samples/executive-memo.before.md` and `samples/executive-memo.after.md`: A Q3 search-latency status memo that starts with process narration, buzz-nouns, framing theater, and buried asks, rewritten into a self-contained BLUF decision brief with vetted numbers (`p95`, sample window, baseline, limiter) and zero tells.
   - Note: `samples/*.before.md` intentionally include AI tells (such as `\u2014`, tell words, connector colons, bold-restatement bullets, framing theater, and buzz-nouns) to exercise `prose_lint.py`; `validate_skill.py` explicitly exempts `samples/*.before.md` as negative fixtures.

## Verification plan

- Write `tests/test_task_005_evals_and_samples.py` covering `TC-005-01` through `TC-005-04`.
- Run `make check` and confirm all tests pass cleanly.
