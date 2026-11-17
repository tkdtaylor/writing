# Test Spec 010: Memo Calibration Samples, Evals, and Documentation Sync

- **Task:** `docs/tasks/backlog/010-memo-samples-evals-and-docs-sync.md`
- **Test file:** `tests/test_task_010_memo_samples_and_sync.py`

## Requirements

- **REQ-010-01:** `samples/one-pager.before.md` and `samples/one-pager.after.md` exist and are documented in `samples/README.md`, where `one-pager.before.md` exhibits slide-speak and flourish tells (`em_dashes`, `participial_tail_puffery`, `copula_avoidance`, `rhetorical_qa_pivots`, `contrastive_pivots`, `importance_without_mechanism`) and `one-pager.after.md` follows the 5-section One-Pager blueprint (`<= 550` words) with zero mechanical/flourish tells and higher `anchors_per_100w` in `prose_lint.py`.
- **REQ-010-02:** `evals/evals.json` adds behavioral test cases covering One-Pager vs Six-Pager door-type selection, Six-Pager sacrifice-bearing Tenets + two-way Appendix rules, and anti-flourish editing without false-positive stripping of concrete mechanisms or real parentheticals; `evals/trigger-evals.json` adds realistic one-pager/six-pager and anti-flourish trigger queries.
- **REQ-010-03:** `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md` are synchronized with `references/one-pager-and-six-pager.md`, `samples/one-pager.{before,after}.md`, the `10,000`-word combined runtime budget, and the new `prose_lint.py` flourish checks, and `make check` (`lint + test + fitness`) passes cleanly across the entire repository.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-010-01` | `REQ-010-01` | `samples/one-pager.before.md` vs `samples/one-pager.after.md` via `prose_lint.py` | `.before.md` triggers flourish & mechanical detectors; `.after.md` (`<= 550` words) has `[]` across all tell lists, `anchors_per_100w` higher than `.before.md`, and includes BLUF call, baseline, non-goals, options, and kill switch |
| `TC-010-02` | `REQ-010-02` | `evals/evals.json` and `evals/trigger-evals.json` | `evals/evals.json` has `>= 18` valid cases including one-pager, six-pager/tenets/appendix, and anti-flourish cases; `evals/trigger-evals.json` has `>= 26` balanced queries including one-pager/six-pager triggers |
| `TC-010-03` | `REQ-010-03` | `README.md`, `AGENTS.md`, `CHANGELOG.md`, `validate_skill.py`, and `make fitness` | All files reference `one-pager-and-six-pager.md` and `one-pager`, `validate_skill.py` exits `0`, and all authored Markdown files pass zero-tell prose hygiene |
