.PHONY: lint format test fitness fitness-task-state fitness-mermaid fitness-agy-sync check

lint:
	@python3 -m py_compile scripts/check-mermaid.py scripts/sync-agy-skills.py
	@for f in scripts/*.py tests/*.py; do [ -f "$$f" ] && python3 -m py_compile "$$f" || true; done
	@echo "Python syntax check passed."

format:
	@echo "No auto-formatter required (pure Markdown + Python 3 stdlib)."

test:
	@python3 -m unittest discover -s tests -p "test_*.py" -v

fitness-task-state:
	@./scripts/check-task-state.sh
	@echo "F-001 (task-state invariant) passed."

fitness-mermaid:
	@python3 scripts/check-mermaid.py
	@echo "F-002 (Mermaid diagram hygiene) passed."

fitness-agy-sync:
	@python3 scripts/sync-agy-skills.py --check
	@echo "F-003 (Antigravity adapter sync) passed."

fitness: fitness-task-state fitness-mermaid fitness-agy-sync
	@echo "All fitness checks passed."

check: lint test fitness
	@echo "All checks passed."
