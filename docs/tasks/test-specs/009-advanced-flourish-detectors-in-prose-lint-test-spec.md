# Test Spec 009: Advanced Flourish Detectors in `prose_lint.py` and Spec Sync

- **Task:** `docs/tasks/backlog/009-advanced-flourish-detectors-in-prose-lint.md`
- **Test file:** `tests/test_task_009_flourish_lint.py`

## Requirements

- **REQ-009-01:** `scripts/prose_lint.py` adds high-precision detectors under `mechanics_and_tells` for `participial_tail_puffery` (comma-introduced trailing `-ing` significance clauses lacking mechanism/numeric anchors, while exempting concrete operational tails), `copula_avoidance` (`serves/stands/functions/acts as a testament|cornerstone|catalyst|pillar|backbone|bridge|hub...`, `boasts a/over/\d`, while exempting literal technical roles like `acts as a reverse proxy`), `rhetorical_qa_pivots` (`The result?`, `The catch?`, `The kicker?`, `Sound familiar?`, `Why does this matter?` followed by declarative answers), `performative_fragments` (`Full stop.`, `Simple as that.`, `Nothing more, nothing less.`, `That changes everything.`, `And maybe that's the point.`), and `nominalizations_per_100w` (`the/a/an <noun-ization> of` rate per 100 words).
- **REQ-009-02:** `scripts/prose_lint.py` upgrades `contrastive_pivots` (two-sentence `This isn't a X. It's a Y.` / `Instead, it is`, `less like/about X and more like/about Y`, `rather than merely/simply`, tripled `Not X. Not Y.`), `importance_without_mechanism` (unanchored `without sacrificing` / `without compromising` and `distinction matters`), `inflated_style_verbs` (`unleash`, `harness`, `reimagine`, `ignite`, `illuminate`), and `framing_theater` (`here's the kicker/catch`, `let's unpack/break this down`, sentence-initial `together, these`, `despite these challenges`, `at the end of the day`), while keeping zero composite score fields and zero false positives on clean repo prose.
- **REQ-009-03:** `scripts/validate_skill.py` and `docs/spec/configuration.md` update the combined runtime budget across `SKILL.md` + `references/*.md` to `<= 10,000` words (keeping per-file `<= 1,500` words strict) to support the expanded reference catalog, and `docs/spec/behaviors.md`, `docs/spec/architecture.md`, and `docs/spec/data-model.md` reflect the new reference file and `prose_lint.py` schema fields.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-009-01` | `REQ-009-01` | Flourish fixture vs clean technical fixture in `prose_lint.py` | Fires `participial_tail_puffery`, `copula_avoidance`, `rhetorical_qa_pivots`, `performative_fragments`, and `nominalizations_per_100w > 0` on flourish prose; returns `[]` / `0.0` on concrete technical prose (`acts as a reverse proxy`, `, retrying 3 times within 200 ms`) |
| `TC-009-02` | `REQ-009-02` | Modern AI-tell fixture (split pivots, `less like X and more like Y`, `rather than merely`, `without sacrificing`, `Together, these`) | Fires `contrastive_pivots`, `importance_without_mechanism`, `inflated_style_verbs`, and `framing_theater` while leaving ordinary `rather than` and anchored mechanisms unflagged |
| `TC-009-03` | `REQ-009-03` | `validate_skill.py` + `docs/spec/*.md` + live repo | `COMBINED_RUNTIME_BUDGET == 10000`, `docs/spec/data-model.md` lists all new `mechanics_and_tells` keys, `docs/spec/architecture.md` lists `one-pager-and-six-pager.md`, and `make test` passes |
