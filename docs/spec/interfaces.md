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
- Exit codes: `0` on success, `2` on missing file or invalid arguments.

### `scripts/prose_lint.py`

```bash
python3 scripts/prose_lint.py [FILE ...] [--json] [--raw]
```

- Reads one or more `FILE` paths (or `stdin` when omitted or `-`).
- Strips Markdown syntax automatically via `strip_markdown` unless `--raw` is passed, while still inspecting raw Markdown lines for mechanical checks (em dashes, emoji bullets, bold-label restatements, hard-wrapped lines).
- Default stdout: concise human-readable diagnostic report per input.
- `--json`: emits a single JSON report object (for one input) or a list of report objects (for multiple inputs).
- Exit codes: `0` on successful analysis (advisory by default so writers are not blocked by earned style choices), `2` on file/usage error.

### `scripts/validate_skill.py`

```bash
python3 scripts/validate_skill.py [--root DIR] [--json]
```

- Validates frontmatter, word budgets, routing reachability, broken relative links, command `mode=` symmetry, `evals/*.json` schemas, and repository prose hygiene.
- Exit codes: `0` when all checks pass, `1` when any validation check fails, `2` on usage error.
