.PHONY: lint format test package fitness fitness-task-state fitness-mermaid fitness-agy-sync fitness-skill-package fitness-prose-hygiene fitness-samples fitness-clean-package check

lint:
	@python3 -m py_compile scripts/check-mermaid.py scripts/sync-agy-skills.py
	@for f in scripts/*.py tests/*.py; do if [ -f "$$f" ]; then python3 -m py_compile "$$f"; fi; done
	@echo "Python syntax check passed."

format:
	@echo "No auto-formatter required (pure Markdown + Python 3 stdlib)."

test:
	@python3 -m unittest discover -s tests -p "test_*.py" -v

package:
	@python3 scripts/package_skill.py --output-dir dist
	@echo "Packaged clean skill archives in dist/."

fitness-task-state:
	@./scripts/check-task-state.sh
	@echo "F-001 (task-state invariant) passed."

fitness-mermaid:
	@python3 scripts/check-mermaid.py
	@echo "F-002 (Mermaid diagram hygiene) passed."

fitness-agy-sync:
	@python3 scripts/sync-agy-skills.py --check
	@echo "F-003 (Antigravity adapter sync) passed."

fitness-skill-package:
	@python3 scripts/validate_skill.py
	@echo "F-004 (skill package validation) passed."

fitness-prose-hygiene:
	@python3 scripts/validate_skill.py
	@echo "F-005 (repository prose hygiene) passed."

fitness-samples:
	@python3 -m unittest tests.test_task_005_evals_and_samples
	@echo "F-006 (calibration sample regression) passed."

fitness-clean-package:
	@python3 scripts/package_skill.py --check
	@echo "F-007 (clean skill packaging) passed."

fitness: fitness-task-state fitness-mermaid fitness-agy-sync fitness-skill-package fitness-prose-hygiene fitness-samples fitness-clean-package
	@echo "All fitness checks passed."

check: lint test fitness
	@echo "All checks passed."
