# Test Spec 003: Genre and Register References

- **Task:** `docs/tasks/backlog/003-genre-and-register-references.md`
- **Test file:** `tests/test_task_003_genre_refs.py`

## Requirements

- **REQ-003-01:** `references/technical-and-docs.md` exists (`<= 1500` words) and specifies the 4-layer technical writing standard (Diataxis mode purity across `Tutorial`, `How-to`, `Reference`, `Explanation`; developer style; ASD-STE100 `<=20`-word procedural instructions with warnings before guarded steps; Global English pronoun/modifier disambiguation banning bare clause-level `this`/`which`), plus blueprints for `README` files, `RFC`/`ADR` design docs, and `<40`-line `PR`/change briefings.
- **REQ-003-02:** `references/business-and-executive.md` exists (`<= 1500` words) and specifies BLUF memos/reports, self-contained decision briefs (`call`, `recommendation`, `impact`, `evidence`, `risk`, riskiest-first ordering, baseline + option costs, consumer impact over internal process narration), epistemic tags (`measured`, `inferred`, `open`), number/metric vetting (`unit`, `runs/sample`, `baseline`, `limiter`), status updates, and professional emails/messages.
- **REQ-003-03:** `references/longform-and-persuasion.md` exists (`<= 1500` words) and specifies essays/articles (first-sentence job, paragraph transitions, steelmanned objection, clean ending), marketing/landing copy (problem -> mechanism -> proof -> single CTA), UX microcopy (error = failed + user cause + recovery; verb+noun button labels; actionable empty states), speeches/slides & progressive diagrams (`<=6` boxes, `<=8` words/box, step-by-step build-up for 3+ components), and creative/narrative prose (scene vs summary, sensory detail, protecting intentional rhythm).
- **REQ-003-04:** All three genre reference files obey prose hygiene: zero `\u2014` characters outside fenced code blocks, zero emoji bullets, and continuous single-line paragraphs.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-003-01` | `REQ-003-01` | `references/technical-and-docs.md` | Exists, `450 <= word_count <= 1500`, covers Diataxis 4 modes, STE 20-word steps, Global English bare `this`/`which` rule, README, RFC/ADR, and PR briefing sections |
| `TC-003-02` | `REQ-003-02` | `references/business-and-executive.md` | Exists, `400 <= word_count <= 1500`, covers BLUF, decision brief fields, epistemic tags, metric vetting checklist, and emails |
| `TC-003-03` | `REQ-003-03` | `references/longform-and-persuasion.md` | Exists, `450 <= word_count <= 1500`, covers essays, landing copy, UX microcopy, progressive diagrams (`<=6` boxes / `<=8` words), speeches/slides, and narrative craft |
| `TC-003-04` | `REQ-003-04` | All 3 genre reference files | Zero `\u2014` characters outside fenced code blocks, zero emoji bullets, and continuous single-line paragraphs |
