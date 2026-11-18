# Task 015: CLI Safety Hardening and Agent Model Tier Mapping

- **Priority:** P0
- **Model tier:** `balanced` (`inherit` / Gemini 4 Carbon High)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/015-cli-safety-and-agent-model-tiers-test-spec.md`

## Objective

Harden `scripts/package_skill.py` against unsafe `--install-to` / `--clean` targets and symlink overwrites, wrap `validate_repo(root)` in `scripts/validate_skill.py` against mid-scan `OSError`, sync `docs/spec/interfaces.md`, and configure concrete model tiers across `.claude/agents/*.md`, `.agents/agents/*.md`, `.claude/skill-manifest.json`, and `CLAUDE.md`.

## Deliverables (exclusive file scope)

- `scripts/package_skill.py`
- `scripts/validate_skill.py`
- `docs/spec/interfaces.md`
- `.claude/agents/*.md`
- `.agents/agents/*.md` and `.agents/skills/*/SKILL.md` (regenerated via `scripts/sync-agy-skills.py`)
- `.claude/skill-manifest.json`
- `CLAUDE.md`
- `tests/test_task_015_cli_safety_and_models.py`

Do not modify files owned by Task 016 (`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/architecture/*`, `docs/spec/SPEC.md`, `references/draft-and-brief.md`) or `docs/tasks/test-specs/coverage-tracker.md`.

## Implementation details

1. **Harden `install_payload` in `scripts/package_skill.py` (`REQ-015-01`):**
   - Resolve `root_resolved = root.resolve()` and `target_resolved = target_dir.resolve()`.
   - Reject `target_resolved == Path("/")`, `target_resolved == Path.home().resolve()`, `target_resolved == root_resolved`, and `root_resolved.is_relative_to(target_resolved)` (when `target_dir` is an ancestor directory containing `root`) by raising `OSError` with a clear message.
   - When `clean=True`, also reject `target_resolved.name in {"skills", "commands", "agents", "plugins"}` by raising `OSError` so an accidental `--install-to ~/.claude/skills --clean` (omitting `/writing`) never deletes sibling skills. Keep normal skill folder names (such as `writing` or `dirty-writing`) working cleanly.
   - Before writing each `dst = target_dir / rel`, check that no parent directory inside `target_dir` is a symlink (unlinking if a symlink occupies `dst` or a subdirectory path) and call `dst.unlink()` when `dst.is_symlink()` so `dst.write_bytes(...)` and `os.chmod(dst, mode)` never follow pre-existing symlinks to external files.
2. **Wrap `validate_repo(root)` in `scripts/validate_skill.py` and sync `docs/spec/interfaces.md` (`REQ-015-02`):**
   - Wrap `result = validate_repo(root)` in `validate_skill.py` `main()` inside `try ... except OSError as exc:`, printing `error: validation I/O failure under <root>: <exc>` to `sys.stderr` and returning `2`.
   - Update `docs/spec/interfaces.md` exit-code bullets for `strip_markdown.py` and `validate_skill.py` to mention `OSError` / inaccessible path exit code `2`.
3. **Configure concrete agent model tiers (`REQ-015-03`):**
   - Update `model:` in `.claude/agents/*.md` while preserving all `# model-tier:` comments:
     - `architect.md` -> `model: opus`
     - `security-auditor.md` -> `model: opus`
     - `code-reviewer.md` -> `model: sonnet`
     - `qa.md` -> `model: sonnet`
     - `spec-verifier.md` -> `model: sonnet`
     - `task-planner.md` -> `model: sonnet`
     - `task-executor.md` -> `model: sonnet`
     - `docs-writer.md` -> `model: inherit`
   - Run `python3 scripts/sync-agy-skills.py` so `.agents/agents/{architect,security-auditor}.md` update cleanly to `model: pro`.
   - Recompute and update `installed_hash` (SHA-256) in `.claude/skill-manifest.json` for every modified `.claude/agents/*.md` entry (keeping `template_hash` unchanged).
   - Update `CLAUDE.md` line 15 so it describes the configured `opus` / `sonnet` / `inherit` tier mapping instead of saying all agents default to `model: inherit`.

## Verification plan

- Write `tests/test_task_015_cli_safety_and_models.py` verifying `TC-015-01`, `TC-015-02`, and `TC-015-03`.
- Move this task file to `docs/tasks/completed/015-cli-safety-and-agent-model-tiers.md` via `git mv`.
- Run `make check` and confirm zero errors.
