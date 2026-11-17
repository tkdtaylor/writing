# Test Spec Coverage Tracker

Status legend: `⏳` pending, `🟡` code merged on task branch, `✅` verified by `spec-verifier` + suite check.

| Task ID | Feature | Spec file | Tests written | Status | Verified by |
|---------|---------|-----------|---------------|--------|-------------|
| 001 | Core `SKILL.md` router and `/write-*` slash commands | `001-core-skill-and-commands-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L3 (`make check` 20/20 pass, `2228a0e`) |
| 002 | Workflow mode references (`draft`, `edit`, `review`) | `002-workflow-mode-references-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L3 (`make check` 20/20 pass, `fe5a006`) |
| 003 | Genre and register references (`technical`, `business`, `longform`) | `003-genre-and-register-references-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L3 (`make check` 20/20 pass, `9c63cb9`) |
| 004 | Zero-dependency `strip_markdown.py` and `prose_lint.py` CLIs | `004-prose-lint-and-stripper-cli-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`prose_lint.py AGENTS.md` + `make check`, `4198c5a`) |
| 005 | Evaluation suite (`evals/*`, `JUDGE.md`) and calibration `samples/` | `005-evals-judge-and-samples-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`prose_lint.py` sample delta check, `5f1cb67`) |
| 006 | Skill package and prose hygiene validator (`validate_skill.py`) | `006-package-validator-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`validate_skill.py` PASS on live repo, `50e4f3c`) |
| 007 | Fitness gate wiring, full open-source `README.md`, and release prep | `007-fitness-gates-and-release-docs-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`make check` 31/31 + `F-001`..`F-006`, `3fa238d`) |
| 008 | One-pager, six-pager, and anti-flourish skill guides | `008-one-pager-six-pager-and-anti-flourish-guides-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`prose_lint.py` 0 tells + `validate_skill.py`, `c966696`) |
| 009 | Advanced flourish detectors in `prose_lint.py` and spec sync | `009-advanced-flourish-detectors-in-prose-lint-test-spec.md` | ✅ | ✅ | `spec-verifier` APPROVE + L5 (`make check` 38/38 + 0 clean-repo FPs, `dcc26b0`) |
| 010 | Memo calibration samples, evals, and documentation sync | `010-memo-samples-evals-and-docs-sync-test-spec.md` | ⏳ | ⏳ | N/A |
