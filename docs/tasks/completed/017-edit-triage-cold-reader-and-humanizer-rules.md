# Task 017: Edit Input Triage, Cold-Reader Verification, and Humanizer Anti-Slop Rules

- **Priority:** P0
- **Model tier:** `balanced` (`inherit` / Gemini 4 Carbon High)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/017-edit-triage-cold-reader-and-humanizer-rules-test-spec.md`

## Objective

Enrich `SKILL.md`, `references/edit-and-anti-slop.md`, and `references/review-rubric.md` with 3-way edit input triage, the `Leave-it-alone` test, declined-claim `[TK: ...]` evidence unlocks, Wikipedia `WP:AI` / `blader/humanizer` anti-slop catalog entries (dash-bypass `--` / `U+2013`, chatbot residue, cutoff hedges, meta-narration, echoed headings, phantom strawmen, stacked negation lists), and zero-context `Cold-reader` verification (`doc-coauthoring` Stage 3).

## Deliverables (exclusive file scope)

- `SKILL.md`
- `references/edit-and-anti-slop.md`
- `references/review-rubric.md`
- `tests/test_task_017_edit_triage_and_cold_reader.py`

Do not modify files owned by Tasks 018, 019, or 020 (`references/{technical-and-docs,business-and-executive,longform-and-persuasion}.md`, `scripts/*`, `docs/spec/*`, `evals/*`, `README.md`, `CHANGELOG.md`, or `coverage-tracker.md`).

## Implementation details

1. **`SKILL.md` (`REQ-017-01`, keep `<= 1,480` words and every sentence `<= 35` words):**
   - Add `postmortems` and `release notes` to frontmatter `description` while preserving the `Don't use for...` clause and all existing triggers.
   - Under `mode=edit`, note 3-way input triage (`slop/notes`, `real voice`, `point edit`) before rewriting.
   - Under `mode=review`, note the optional zero-context cold-reader check for high-stakes standalone documents.
   - In Step 3 (`Style Precedence and Baseline Mechanics`), note sentence-case headings (`## Verify webhook signatures` over Title Case) and explicitly ban spaced double-hyphen (`` ` -- ` ``) and spaced en-dash (`U+2013`) em-dash substitutes alongside `U+2014`.
2. **`references/edit-and-anti-slop.md` (`REQ-017-02`, keep `<= 1,350` words and every sentence `<= 35` words):**
   - In Section 1 (`Pre-edit inventory and input triage`), add 3-way input diagnosis:
     - `Slop or rough notes`: generic boilerplate or raw fragments; broad structural latitude while keeping facts exact.
     - `Real author voice present`: rough draft with genuine opinion or distinctive phrasing; lock sentences that already work and preserve casual lexical choices (`ship`, `stuff`) instead of upgrading to corporate synonyms.
     - `Point edit`: targeted request (`fix this headline`, `tighten paragraph two`); edit only the requested passage and leave surrounding text untouched.
   - In Step 1 (`Truth and scope`) of Section 2, add **Declined claims name their unlock**: when cutting or softening an unsupported claim (`"cuts churn 40%"`, `"enterprise-grade"`), pair the supportable rewrite with the exact evidence needed to unlock the stronger version (`[TK: 90-day cohort export / SOC 2 Type II report]`).
   - Under Section 2's stop rule, add the **Leave-it-alone test**: revert any sentence change that is merely different rather than measurably clearer.
   - Expand Section 4 (`Mechanical and lexical anti-slop catalog`, wrapping EVERY literal example tell phrase inside inline backticks `` `...` `` so `prose_lint.py` never triggers on the guide itself!):
     - Add spaced double-hyphens (`` ` -- ` ``) and spaced en-dashes (`U+2013`) to the em-dash bullet.
     - Add a bullet for **Chatbot residue and knowledge-cutoff hedges**: strip leaked conversational wrappers (`` `Great question` ``, `` `I hope this helps` ``, `` `Happy to help` ``, `` `Certainly,` ``, `` `Let me know if you'd like me to expand` ``) and cutoff/source guesses (`` `as of my last update` ``, `` `while specific details are limited` ``, `` `based on available information` ``).
     - Add a bullet for **Meta-document narration, echoed headings, phantom strawmen, and stacked negation lists**: cut self-describing layout lines (`` `this section is organized by` ``, `` `the table below compares` ``), delete first sentences that merely repeat the heading above them, cut stock `` `Despite these challenges... continues to thrive / the future looks bright` `` closers, drop unprompted defensive setups (`` `This isn't about` ``, `` `I'm not saying` ``, `` `Don't get me wrong` ``, `` `A tempting approach would be` ``), and rewrite stacked negation chains (`` `No setup call, no templates, no spreadsheets` ``) into concrete positive actions.
3. **`references/review-rubric.md` (`REQ-017-03`, keep `<= 1,000` words and every sentence `<= 35` words):**
   - Add `## 5. Zero-context cold-reader pass` for high-stakes standalone documents (`RFCs`, `Six-Pagers`, technical specs, and onboarding guides):
     - Predict `3` to `5` realistic questions a target reader needs the document to answer.
     - When subagents are available, dispatch a fresh read-only subagent with **only** the document text and those questions (zero chat history) to ask: what each answer is, what unstated background the document assumes, and where passages read as ambiguous or contradictory. When subagents are unavailable, simulate the cold-reader questions explicitly or give the author the exact fresh-session test prompt.
     - Fold any comprehension gaps into `Passage-level findings` (`revise` or `ask-author`) while keeping `mode=review` strictly read-only.

## Verification plan

- Write `tests/test_task_017_edit_triage_and_cold_reader.py` verifying `TC-017-01`..`TC-017-03` (including `validate_skill.validate_repo` word budgets and `prose_lint.analyze_text` zero tells + zero `overloaded_sentences` across all 3 touched files).
- Move this task file to `docs/tasks/completed/017-edit-triage-cold-reader-and-humanizer-rules.md` via `git mv`.
- Run `make check` and confirm exit `0`.
