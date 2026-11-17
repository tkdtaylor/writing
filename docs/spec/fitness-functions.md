# Fitness Functions

Executable architectural invariants run via `make fitness`. Every rule below is wired as an active `fitness-*` prerequisite in `Makefile` and runs automatically under `make check`.

| ID | Rule | Target / Command | Status |
|----|------|------------------|--------|
| `F-001` | Each task `NNN-*` exists in at most one of `backlog/`, `active/`, `completed/` | `make fitness-task-state` (`./scripts/check-task-state.sh`) | Active |
| `F-002` | All Mermaid fenced blocks avoid GitHub parser hazards | `make fitness-mermaid` (`python3 scripts/check-mermaid.py`) | Active |
| `F-003` | `.agents/` adapters match canonical `.claude/` agents and commands | `make fitness-agy-sync` (`python3 scripts/sync-agy-skills.py --check`) | Active |
| `F-004` | Skill word budgets, routing reachability, relative links, mode symmetry, and eval schemas hold | `make fitness-skill-package` (`python3 scripts/validate_skill.py`) | Active |
| `F-005` | Repository prose files contain zero prose em dashes, emoji bullets, or hard-wrapped paragraphs | `make fitness-prose-hygiene` (`python3 scripts/validate_skill.py`) | Active |
| `F-006` | Calibration `.after.md` samples eliminate `.before.md` mechanical tells in `prose_lint.py` | `make fitness-samples` (`python3 -m unittest tests.test_task_005_evals_and_samples`) | Active |
