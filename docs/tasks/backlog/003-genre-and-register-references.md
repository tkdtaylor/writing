# Task 003: Genre and Register References (`technical`, `business`, `longform`)

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/003-genre-and-register-references-test-spec.md`

## Objective

Author the three genre and register reference guides (`<= 1,500` words each) under `references/`, implementing behavior `B-003` from `docs/spec/behaviors.md`.

## Deliverables (exclusive file scope)

- `references/technical-and-docs.md`
- `references/business-and-executive.md`
- `references/longform-and-persuasion.md`
- `tests/test_task_003_genre_refs.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks.

## Implementation details

1. **`references/technical-and-docs.md`:**
   - **4-layer technical writing standard:**
     - *Layer 1 (Diataxis mode purity):* `Tutorial` (learning by doing, visible result each step, minimal theory), `How-to` (goal-oriented steps for a competent user), `Reference` (complete, dry, artifact-mirrored facts), `Explanation` (design rationale, constraints, tradeoffs; opinion lives here only). One mode per doc or clearly separated section; split and link rather than mixing.
     - *Layer 2 (Developer style):* Address the reader as `you` in present tense; put conditions before instructions (`If X, run Y`) and the common path first; cut `simply`, `easily`, `just`, and `please` in procedures; descriptive link text; sentence-case headings carrying the point; numbered lists for ordered steps, bullets otherwise.
     - *Layer 3 (ASD-STE100 procedural clarity):* One instruction per sentence; keep procedural steps `<= 20` words and explanatory sentences crisp; place warnings and prerequisites *before* the step they guard; use one consistent term per concept.
     - *Layer 4 (Global English disambiguation):* Place `only` and `not` next to what they modify; unpack dense noun strings; never use bare `this` or `which` to refer to an entire preceding clause (always supply the noun: `this timeout`, `which causes...` -> split sentence); spell out ambiguous slashes (`and/or`).
   - **Concrete technical blueprints:**
     - *READMEs:* One-sentence plain description of what it does and for whom -> working install and copy-paste quickstart with expected output -> core usage -> links out to Diataxis docs.
     - *RFCs and ADRs:* Problem grounded in concrete incidents or metrics -> explicit non-goals and constraints -> options compared with honest costs (no strawmen) plus the strongest real objection answered -> recommended design -> blast radius, migration, and verification.
     - *PR and change briefings:* Keep under 40 lines using `Why` (starts with user/system goal), `What changed`, `Scope`, `Tradeoffs` (only rejected options a reviewer would ask about), `Blast radius`, and `Verification`; link long logs externally.
2. **`references/business-and-executive.md`:**
   - **BLUF memos and analytical reports:** Lead with the conclusion, recommendation, or required decision in the first paragraph; organize body sections by governing takeaways rather than chronological discovery.
   - **Self-contained decision briefs:** Make every decision decidable from the brief alone (spend words on the decision, keep backstory under 100 words). Report consumer/user impact over internal process narration ("checkout succeeds on retry", not "refactored retry handler"). Format each decision item with `Call + Recommendation + User/business impact + Evidence + Risk`, ordered riskiest first, stating baseline cost alongside option costs.
   - **Epistemic labels and metric vetting:** Tag mixed-certainty claims (`measured`, `inferred`, `open`). Every reported performance or business metric must state its unit, sample/run context, comparison baseline, and limiting constraint (or mark it inconclusive).
   - **Async updates and emails/messages:** Put the ask, deadline, or status in line one; write complete spoken standalone bullets rather than cryptic fragments; match social register without sycophantic padding.
3. **`references/longform-and-persuasion.md`:**
   - **Essays, blog posts, and newsletters:** Sentence one has one job (earn sentence two without defining the topic or announcing intent); each paragraph earns the next via explicit logical or narrative hooks (cover-the-page transition test); give the strongest real counterargument its own fair paragraph; stop where the thought ends without a victory-lap summary.
   - **Marketing, launch, and landing copy:** Lead with the specific reader problem or job-to-be-done -> show the concrete mechanism or before/after workflow instead of empty superlatives -> back claims with checkable proof -> close with one proportionate call to action.
   - **UX microcopy:** Error messages state *what failed + cause in user terms + exact recovery action*; button and modal actions use specific `Verb + Noun` (`Revoke API key`, never `OK`/`Yes`); empty states explain value plus the primary action to populate.
   - **Speeches, slides, and progressive visuals:** Write oral prose for breath and ear; keep slides to one point per slide with subtitles stating the takeaway rather than reading labels aloud. Cap diagrams at `<= 6` boxes and `<= 8` words per box in reader vocabulary (no internal variable names), never duplicate facts verbatim across prose and diagram, and teach 3+ part systems via progressive diagram build-up (adding one new component per step).
   - **Creative and narrative prose:** Prefer concrete scene, action, and sensory detail over naming the emotion the reader should feel; protect intentional fragments, dialogue cadence, and earned figurative language from mechanical over-editing.

## Verification plan

- Write `tests/test_task_003_genre_refs.py` covering `TC-003-01` through `TC-003-04`.
- Run `make check` and confirm all tests pass and prose hygiene holds.
