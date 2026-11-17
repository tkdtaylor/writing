# Task 010: Memo Calibration Samples, Evals, and Documentation Sync

- **Priority:** P1
- **Model tier:** `balanced`
- **Dependencies:** Tasks `008`, `009` (Wave 2)
- **Test spec:** `docs/tasks/test-specs/010-memo-samples-evals-and-docs-sync-test-spec.md`

## Objective

Add a realistic `one-pager` before/after calibration sample pair exercising the new narrative-memo and anti-flourish rules, expand `evals/evals.json` and `evals/trigger-evals.json` with one-pager/six-pager and anti-flourish cases, and synchronize `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/plans/roadmap.md`, and integration tests.

## Deliverables (exclusive file scope)

- `samples/one-pager.before.md`
- `samples/one-pager.after.md`
- `samples/README.md`
- `evals/evals.json`
- `evals/trigger-evals.json`
- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/plans/roadmap.md`
- `tests/test_task_007_integration.py`
- `tests/test_task_010_memo_samples_and_sync.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` on the task branch.

## Implementation details

1. **`samples/one-pager.before.md` and `samples/one-pager.after.md` (+ `samples/README.md`):**
   - `one-pager.before.md`: A bloated AI-drafted engineering/product one-pager proposal (e.g. self-serve sandbox environment or webhook replay queue) exhibiting slide-speak bullets, prose em dashes, trailing `-ing` puffery (`, highlighting...`, `, ensuring seamless scalability`), copula avoidance (`serves as a cornerstone`), a `The result?` rhetorical Q&A pivot, a two-sentence negative parallelism (`This isn't a tooling issue. It's...`), and unanchored `without sacrificing` claims.
   - `one-pager.after.md`: Rewritten (`350` to `550` words) following `references/one-pager-and-six-pager.md`'s 5-section One-Pager blueprint (`BLUF / Decision Call`, `Problem and Baseline`, `Scope and Explicit Non-Goals`, `Viable Options and Tradeoffs` including Status Quo, `Risks, Kill Switch, and Owned Next Steps`), achieving `Findings: none` (`[]` across every tell list) and higher `anchors_per_100w` in `prose_lint.py`.
   - Document the new pair in `samples/README.md` (and consider updating `tests/test_task_005_evals_and_samples.py` only if needed, or verify in `test_task_010_memo_samples_and_sync.py`).
2. **`evals/evals.json` and `evals/trigger-evals.json`:**
   - Add `>= 3` new behavioral eval cases to `evals/evals.json` (total `>= 18`):
     - Choosing One-Pager vs Six-Pager based on Type 2 vs Type 1 decision reversibility and refusing to pad thin notes to 6 pages.
     - Drafting or reviewing a Six-Pager with sacrifice-bearing Tenets, input vs output metrics, steelmanned alternatives, and the two-way Appendix contract.
     - Editing flourish-heavy prose (`serves as`, `, highlighting...`, `The result?`, `less like X and more like Y`, `without sacrificing`) while preserving earned parentheses and concrete operational `-ing` clauses (`false_positive_restraint` / `medium_fit`).
   - Add `>= 4` new trigger queries (`2` positive for one-pager/six-pager/anti-flourish, `2` near-miss negative, total `>= 28`) to `evals/trigger-evals.json`.
3. **Synchronize `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/plans/roadmap.md`, and `tests/test_task_007_integration.py`:**
   - Add `references/one-pager-and-six-pager.md` and `samples/one-pager.{before,after}.md` to repo structure trees and genre tables in `README.md` and `AGENTS.md`.
   - Highlight One-Pager / Six-Pager / PR-FAQ support and the expanded anti-flourish detectors in `README.md` and `CHANGELOG.md`.
   - Update `tests/test_task_007_integration.py` so `combined_runtime` checks `<= 10000`, `one-pager-and-six-pager.md` is checked alongside the other genre guides, and the new flourish tell keys are asserted `== []` on `README.md`, `CHANGELOG.md`, and `docs/spec/fitness-functions.md`.

## Verification plan

- Write `tests/test_task_010_memo_samples_and_sync.py` covering `TC-010-01` through `TC-010-03`.
- Run `make check` (`lint + test + fitness`) and `python3 scripts/prose_lint.py SKILL.md references/*.md README.md samples/*.after.md`, verifying exit `0` and clean prose across all authored files.
