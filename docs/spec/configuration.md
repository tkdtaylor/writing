# Configuration

## Skill context budgets (enforced by `scripts/validate_skill.py`)

| Scope | Budget | Rationale |
|-------|--------|-----------|
| `SKILL.md` | `<= 1,500` words | Keeps baseline skill load small across every turn |
| Each `references/*.md` file | `<= 1,500` words | Bounds on-demand mode and genre reference loads |
| Combined runtime prose (`SKILL.md` + all `references/*.md`) | `<= 8,500` words | Prevents gradual context-window bloat as rules evolve |

## House-style and voice overrides

At runtime, the `writing` skill checks for user or project overrides in this precedence order:

1. **Explicit prompt constraints or author voice sample** in the current conversation (governs tone, cadence, and punctuation; never factual claims).
2. **Workspace style rules** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or a linked style guide in the active repo).
3. **Skill defaults** in `SKILL.md` and the active `references/*.md` genre guide.

## Repository development environment variables

| Variable | Values | Purpose |
|----------|--------|---------|
| `CLAUDE_HOOK_PROFILE` | `minimal`, `standard` (default), `strict` | Controls which `.claude/scripts/*.py` hooks execute |
| `CLAUDE_DISABLED_HOOKS` | Comma-separated hook stems | Selectively disables individual hooks |
| `CLAUDE_SKIP_SPEC_COVERAGE` | `1` | Bypasses `spec-coverage-check.py` for non-task commits |
| `TASK_BASE_BRANCH` | Branch name | Overrides base/merge target branch in `start-task.sh` and `finish-task.sh` |
