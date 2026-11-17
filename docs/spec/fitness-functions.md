# Fitness Functions

Executable architectural invariants run via `make fitness`. Active rules are wired as `fitness-*` prerequisites in `Makefile`; planned rules (`Task 007`) are wired once Tasks `005` and `006` land.

| ID | Rule | Target / Command | Status |
|----|------|------------------|--------|
| `F-001` | Each task `NNN-*` exists in at most one of `backlog/`, `active/`, `completed/` | `make fitness-task-state` (`./scripts/check-task-state.sh`) | Active |
| `F-002` | All Mermaid fenced blocks avoid GitHub parser hazards | `make fitness-mermaid` (`python3 scripts/check-mermaid.py`) | Active |
| `F-003` | `.agents/` adapters match canonical `.claude/` agents and commands | `make fitness-agy-sync` (`python3 scripts/sync-agy-skills.py --check`) | Active |
| `F-004` | Skill word budgets, routing reachability, relative links, mode symmetry, and eval schemas hold | `make fitness-skill-package` (`python3 scripts/validate_skill.py`) | Planned (Task 007) |
| `F-005` | Repository prose files contain zero prose em dashes, emoji bullets, or hard-wrapped paragraphs | `make fitness-prose-hygiene` (verified in `validate_skill.py`) | Planned (Task 007) |
| `F-006` | Calibration `.after.md` samples eliminate `.before.md` mechanical tells in `prose_lint.py` | `make fitness-samples` (`python3 -m unittest discover -s tests`) | Planned (Task 007) |
