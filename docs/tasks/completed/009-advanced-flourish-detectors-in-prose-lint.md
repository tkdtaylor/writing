# Task 009: Advanced Flourish Detectors in `prose_lint.py` and Spec Sync

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/009-advanced-flourish-detectors-in-prose-lint-test-spec.md`

## Objective

Extend `scripts/prose_lint.py` with high-precision detectors for contemporary LLM flourish and syntactic tells, update `scripts/validate_skill.py` combined runtime budget to `10,000` words, and synchronize `docs/spec/` and existing schema/budget tests.

## Deliverables (exclusive file scope)

- `scripts/prose_lint.py`
- `scripts/validate_skill.py`
- `docs/spec/behaviors.md`
- `docs/spec/architecture.md`
- `docs/spec/data-model.md`
- `docs/spec/configuration.md`
- `tests/test_task_004_prose_lint.py`
- `tests/test_task_006_validate_skill.py`
- `tests/test_task_009_flourish_lint.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files owned by Task 008 (`SKILL.md`, `references/*`). Use `\u2014` escape sequences instead of literal em dashes in all Python code and tests, and keep zeroprose `\u2014` in `docs/spec/*.md`.

## Implementation details

1. **New detectors in `scripts/prose_lint.py` (`mechanics_and_tells`):**
   - `participial_tail_puffery`: Scan `posture_sentences` for comma-introduced trailing clauses matching `,\s+(?:thereby\s+|thus\s+|ultimately\s+)?(?:highlighting|underscoring|emphasizing|ensuring|fostering|cultivating|showcasing|reflecting|symbolizing|exemplifying|paving\s+the\s+way\s+for|contributing\s+to)\b[^.!?]*[.!?]?$` where the trailing clause does **not** contain `_MECHANISM_MARKER_RE` (so concrete engineering tails like `, retrying 3 times within 200 ms` or `, ensuring SHA-256 digests match` pass cleanly, while `, ensuring long-term scalability and highlighting architectural maturity.` is flagged).
   - `copula_avoidance`: Flag puffed copula substitutions (`\b(?:serves?|served|stands?|stood|functions?|acts?|operates?)\s+as\s+a(?:n)?\s+(?:testament|reminder|cornerstone|catalyst|beacon|pillar|symbol|foundation|model|benchmark|backbone|bridge|window|gateway|hub)\b` and `\bboasts?\s+(?:a|an|over|more\s+than|nearly|\d)`) while leaving literal technical roles (`acts as a reverse proxy`, `functions as a mutex`) untouched.
   - `rhetorical_qa_pivots`: Walk adjacent sentence pairs `(s[i], s[i+1])`; flag when `s[i]` (`<= 8` words) ends with `?` matching self-posed theatrical hooks (`^(?:The\s+(?:result|catch|kicker|twist|upside|downside|payoff|problem|secret|truth|bottom\s+line|best\s+part|worst\s+part|fix|answer|takeaway)|Sound\s+familiar|Why\s+does\s+(?:this|that)\s+matter|What(?:'s|\s+is)\s+the\s+(?:catch|result|fix|point)|Here(?:'s|\s+is)\s+the\s+question)\?$`, case-insensitive) and `s[i+1]` is a non-question answer.
   - `performative_fragments`: Flag standalone theatrical mic-drop sentences matching `^(?:Full\s+stop|Period|Simple\s+as\s+that|Nothing\s+more,\s+nothing\s+less|That\s+changes\s+everything|And\s+maybe\s+that(?:'s|\s+is)\s+the\s+point|Read\s+that\s+again|Let\s+that\s+sink\s+in)[.!]$` (case-insensitive).
   - `nominalizations_per_100w`: Rate per 100 words of prepositional nominalization chains matching `\b(?:the|a|an)\s+[a-z]{4,}(?:tion|ment|ance|ence|ization)\s+of\b` (rounded to 2 decimals, `0.0` when clean).
2. **Upgraded existing detectors in `scripts/prose_lint.py`:**
   - `contrastive_pivots`: Add two-sentence negative parallelisms (`This isn't a X. It's a Y.` / `not simply X. Instead, it is Y.`), `less like/about X and/, more like/about Y`, `rather than merely/simply`, and tripled staccato negations (`Not X. Not Y.`).
   - `importance_without_mechanism`: Also flag sentences containing unanchored tradeoff-denial phrases (`without sacrificing`, `without compromising`) or `distinction matters` when `_MECHANISM_MARKER_RE` is absent.
   - `inflated_style_verbs`: Add `unleash`, `harness`, `reimagine`, `ignite`, `illuminate`.
   - `framing_theater`: Add `here's the kicker/catch/thing`, `let's break this down/unpack`, sentence-initial `together, these`, `despite these challenges`, `at the end of the day`, and `so, to answer your question`.
   - Surface non-empty `participial_tail_puffery`, `copula_avoidance`, `rhetorical_qa_pivots`, and `performative_fragments` in `format_human_report` as well!
   - Verify ZERO false positives across existing clean repo files (`README.md`, `CHANGELOG.md`, `AGENTS.md`, `samples/*.after.md`, `evals/JUDGE.md`).
3. **Update `scripts/validate_skill.py`, `docs/spec/*`, and existing schema/budget tests:**
   - Bump `COMBINED_RUNTIME_BUDGET` from `8500` to `10000` in `scripts/validate_skill.py` and `docs/spec/configuration.md` (keeping per-file `1500` unchanged).
   - Update `docs/spec/behaviors.md`, `docs/spec/architecture.md` (documenting `references/one-pager-and-six-pager.md`), and `docs/spec/data-model.md` (documenting the 5 new `mechanics_and_tells` fields).
   - Update `expected_mech_keys` in `tests/test_task_004_prose_lint.py` and the `8500` -> `10000` combined budget test in `tests/test_task_006_validate_skill.py` so existing unit tests stay accurate and green.

## Verification plan

- Write `tests/test_task_009_flourish_lint.py` covering `TC-009-01` through `TC-009-03`.
- Run `make check` and confirm all tests and fitness gates pass with exit code `0`.
