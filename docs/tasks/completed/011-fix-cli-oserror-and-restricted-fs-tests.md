# Task 011: Fix CLI `OSError` / `PermissionError` Handling and Restricted-FS Tests

- **Priority:** P0
- **Model tier:** `fast` (`flash`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/011-fix-cli-oserror-and-restricted-fs-tests-test-spec.md`

## Objective

Fix the `PermissionError` / `OSError` crash when `scripts/validate_skill.py` (and `scripts/strip_markdown.py`) receives an inaccessible `--root` or file path on Python 3.13 / restricted filesystems, and replace the hardcoded `/nonexistent/skill/root/path` test fixture in `tests/test_task_006_validate_skill.py` with a `tempfile.TemporaryDirectory()`-scoped path.

## Deliverables (exclusive file scope)

- `scripts/validate_skill.py`
- `scripts/strip_markdown.py`
- `tests/test_task_006_validate_skill.py`
- `tests/test_task_011_cli_oserror.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md`, `scripts/prose_lint.py` (owned by Task 013), or files belonging to other tasks. Use `\u2014` escape sequences instead of literal em dashes in Python code.

## Implementation details

1. **`scripts/validate_skill.py` (`main`):**
   - Wrap `is_dir = root.is_dir()` inside `try ... except OSError as exc:`: on `OSError` (including `PermissionError`), print `f"error: cannot access root directory {args.root}: {exc}"` to `sys.stderr` and `return 2`. If `not is_dir`, keep printing `f"error: root directory not found: {args.root}"` to `sys.stderr` and `return 2`.
2. **`scripts/strip_markdown.py` (`main`):**
   - Wrap `path.is_file()` and `path.read_text(...)` inside `try ... except OSError as exc:` so any `PermissionError` or `OSError` prints a clean `error:` line to `sys.stderr` and returns `2` instead of raising an unhandled traceback.
3. **`tests/test_task_006_validate_skill.py` and `tests/test_task_011_cli_oserror.py`:**
   - In `tests/test_task_006_validate_skill.py` (around line 155), construct the nonexistent root path inside a `with tempfile.TemporaryDirectory() as tmp:` block (`str(Path(tmp) / "nonexistent" / "skill" / "root")`) rather than `/nonexistent/skill/root/path`.
   - Create `tests/test_task_011_cli_oserror.py` covering `TC-011-01`..`TC-011-03`, using `unittest.mock.patch.object(Path, "is_dir", side_effect=PermissionError(13, "Permission denied"))` and `patch.object(Path, "is_file", side_effect=PermissionError(13, "Permission denied"))` to prove both CLIs return exit code `2` cleanly under restricted filesystems.

## Verification plan

- Run `make check` inside the worktree and verify all unit tests and fitness checks pass with exit code `0`.
