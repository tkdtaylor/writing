# Interfaces

## 1. Slash commands (`commands/*.md`)

Installed optionally to `~/.claude/commands/`:

| Command | File | Passes to `SKILL.md` |
|---------|------|----------------------|
| `/write-draft` | `commands/write-draft.md` | `mode=draft $ARGUMENTS` |
| `/write-edit` | `commands/write-edit.md` | `mode=edit $ARGUMENTS` |
| `/write-review` | `commands/write-review.md` | `mode=review $ARGUMENTS` |
| `/write-lint` | `commands/write-lint.md` | `mode=lint $ARGUMENTS` |

## 2. CLI interfaces (`scripts/`)

### `scripts/strip_markdown.py`

```bash
python3 scripts/strip_markdown.py [FILE] [--json]
```

- Reads `FILE` or `stdin` when `FILE` is omitted or `-`.
- Default stdout: stripped reader-visible body paragraphs separated by blank lines.
- `--json`: emits the JSON object specified in [data-model.md](data-model.md).
- Exit codes: `0` on success, `2` on missing file, `OSError`, or invalid arguments.

### `scripts/prose_lint.py`

```bash
python3 scripts/prose_lint.py [FILE ...] [--json] [--raw] [--profile PROFILE]
```

- Reads one or more `FILE` paths (or `stdin` when omitted or `-`).
- Strips Markdown syntax automatically via `strip_markdown` unless `--raw` is passed. Raw lines remain checked for mechanical tells (em dashes, emoji bullets, bold-label restatements, hard wraps, shorthand ambiguities, prose exclamation marks, and false agency).
- `--profile` (alias `--mode`): optional genre profile (`default`, `technical`, `memo`, `one-pager`, `six-pager`, `narrative`) attaching `profile_checks` diagnostics to both human-readable and `--json` reports when non-default.
- Default stdout: concise human-readable diagnostic report per input.
- `--json`: emits a single JSON report object (for one input) or a list of report objects (for multiple inputs).
- Exit codes: `0` on successful analysis (advisory by default so writers are not blocked by earned style choices), `2` on file/permission (`OSError`) or usage error.

### `scripts/validate_skill.py`

```bash
python3 scripts/validate_skill.py [--root DIR] [--json]
```

- Validates frontmatter, word budgets, routing reachability, broken relative links, command `mode=` symmetry, `evals/*.json` schemas, and repository prose hygiene.
- Exit codes: `0` when all checks pass, `1` when any validation check fails, `2` on `OSError`, inaccessible path, or usage error.

### `scripts/package_skill.py`

```bash
python3 scripts/package_skill.py [--root DIR] [--output-dir DIR] [--install-to DIR] [--clean] [--check] [--json]
```

- Collects the self-contained runtime payload (`SKILL.md`, `LICENSE`, `commands/write-*.md`, `references/*.md`, `scripts/strip_markdown.py`, `scripts/prose_lint.py`, and `scripts/validate_skill.py`).
- `--check`: stages the payload into a temporary directory, confirms one `SKILL.md` with zero `.agents/`, `.claude/`, `docs/`, or `tests/` paths, and runs `validate_skill.validate_repo`. Runs by default when no output or install flag is passed.
- `--output-dir DIR`: writes deterministic `writing-skill.tar.gz` and `writing.skill` zip archives (rooted under `writing/`) into `DIR` after staging verification passes.
- `--install-to DIR`: copies only the clean runtime payload into `DIR` after unlinking pre-existing destination symlinks; `--clean` removes stale non-payload entries inside `DIR` first. Rejects unsafe targets (`/`, `$HOME`, the repository root or its ancestors, and `--clean` on collection directories `skills`, `commands`, `agents`, or `plugins`).
- `--json`: emits a JSON summary covering `payload_files`, `skill_md_count`, `excluded_dirs_absent`, `validation`, `archives`, and `installed_to`.
- Exit codes: `0` when staging validation and requested actions succeed, `1` when payload completeness or `validate_skill.py` checks fail, `2` on `OSError`, inaccessible path, or CLI usage error.

