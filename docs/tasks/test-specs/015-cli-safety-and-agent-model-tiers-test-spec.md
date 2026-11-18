# Test Spec 015: CLI Safety Hardening and Agent Model Tier Mapping

- **Task:** `docs/tasks/backlog/015-cli-safety-and-agent-model-tiers.md`
- **Verification target:** L5 (`make check` + `package_skill.py --check` + `sync-agy-skills.py --check`)

## Requirements and Test Cases

### `REQ-015-01`: `package_skill.py` target-directory and symlink safety

- **`TC-015-01`**: `scripts/package_skill.py` `install_payload()` and CLI `--install-to` reject `/`, `$HOME`, the repository root, and any ancestor directory containing the repository root with `OSError` (CLI exit code `2`); reject `--clean` when `target_dir.resolve().name` is a multi-skill collection directory (`skills`, `commands`, `agents`, `plugins`) with `OSError` (CLI exit code `2`); and unlink pre-existing symlinks at destination file paths inside `target_dir` before writing so external symlink targets are never overwritten or `chmod`-modified.

### `REQ-015-02`: `validate_skill.py` inner `OSError` handling and `docs/spec/interfaces.md` sync

- **`TC-015-02`**: `scripts/validate_skill.py` `main()` wraps `validate_repo(root)` inside `try ... except OSError:` so mid-run permission or I/O errors print an `error:` message to `stderr` and return exit code `2` cleanly, and `docs/spec/interfaces.md` documents `OSError` exit code `2` behavior across `strip_markdown.py` and `validate_skill.py` alongside `prose_lint.py` and `package_skill.py`.

### `REQ-015-03`: Concrete model-tier mapping in `.claude/agents/`, `.agents/agents/`, and `.claude/skill-manifest.json`

- **`TC-015-03`**: `.claude/agents/*.md` map `# model-tier:` comments to concrete tier models (`architect` and `security-auditor` -> `opus`; `code-reviewer`, `qa`, `spec-verifier`, `task-planner`, and `task-executor` -> `sonnet`; `docs-writer` -> `inherit`) while preserving `# model-tier:` comments; `python3 scripts/sync-agy-skills.py --check` exits `0` with `.agents/agents/{architect,security-auditor}.md` mapped to `model: pro`; every `installed_hash` in `.claude/skill-manifest.json` matches the SHA-256 digest on disk; and `CLAUDE.md` accurately describes the configured agent tiers without literal em dashes or `prose_lint.py` tell hits.
