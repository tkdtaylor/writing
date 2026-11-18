# Test Spec 011: Fix CLI `OSError` / `PermissionError` Handling and Restricted-FS Tests

- **Task:** `docs/tasks/backlog/011-fix-cli-oserror-and-restricted-fs-tests.md`
- **Test file:** `tests/test_task_011_cli_oserror.py` (plus update to `tests/test_task_006_validate_skill.py`)

## Requirements

- **REQ-011-01:** `scripts/validate_skill.py` wraps its `--root` directory validation (`root.is_dir()`) in `try ... except OSError:` so `PermissionError` or other `OSError` exceptions on restricted filesystems print a clean error message to `stderr` and return exit code `2` (never crashing with exit code `1` or an unhandled traceback).
- **REQ-011-02:** `scripts/strip_markdown.py` wraps its CLI input-path check and read in `try ... except OSError:` so `PermissionError` or missing files return exit code `2` cleanly.
- **REQ-011-03:** `tests/test_task_006_validate_skill.py` constructs its nonexistent `--root` test path inside `tempfile.TemporaryDirectory()` rather than `/nonexistent/skill/root/path`, and `tests/test_task_011_cli_oserror.py` explicitly verifies both `TemporaryDirectory`-scoped nonexistent paths and mocked `PermissionError` on `Path.is_dir` / `Path.is_file` returning exit code `2`.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-011-01` | `REQ-011-01` | `validate_skill.main` with mocked `PermissionError` on `Path.is_dir` + CLI nonexistent path in `TemporaryDirectory` | Returns `2` (no uncaught `PermissionError`) and writes `error:` to `stderr` |
| `TC-011-02` | `REQ-011-02` | `strip_markdown.main` with mocked `PermissionError` + CLI nonexistent path in `TemporaryDirectory` | Returns `2` (no uncaught `PermissionError`) and writes error to `stderr` |
| `TC-011-03` | `REQ-011-03` | `tests/test_task_006_validate_skill.py` source + suite execution | Contains zero hardcoded `"/nonexistent/` root paths and passes `unittest` cleanly |
