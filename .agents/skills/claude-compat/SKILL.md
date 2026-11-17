---
name: claude-compat
description: >-
  Translation layer for following Claude Code skills, agent roles (.claude/agents/*.md),
  and slash commands (.claude/commands/*.md) inside Antigravity. Activate whenever another
  skill says to "read and follow" a Claude file, mentions $CLAUDE_SKILL_DIR, Claude tool
  names (Read/Write/Edit/Bash/Grep/Glob/Agent/Task), sub-agents, or Claude Code hooks.
---

# Claude Code → Antigravity compatibility

Use this skill whenever you follow a skill, agent role or slash command written for
**Claude Code** while running in **Antigravity**. The Claude file stays the
canonical source, shared by both harnesses. **Never edit the Claude file to fit
Antigravity.** Translate it as you read, using the tables below.

## Tool names

| Claude Code | Antigravity |
|---|---|
| `Read` | `view_file` |
| `Write` | `write_to_file` |
| `Edit` / `MultiEdit` | `replace_file_content` (one contiguous block per call) |
| `Bash` | `run_command`. Each call is a fresh shell: no `cd`, and no shell variables carry over unless you use `RunPersistent`. |
| `Grep` / `Glob` | `run_command` with `grep -rn` / `find` / `rg` |
| `WebFetch` / `WebSearch` | `read_url_content` / `search_web` |
| `AskUserQuestion` | `ask_question` |
| `TodoWrite` | A task-list artifact in the conversation's artifact directory |
| `tools:` / `model:` / `color:` agent frontmatter | The generated custom subagents (`.agents/agents/`) map `tools:` and `model:` for real. When acting as a role **inline**, there are no per-role limits, so **honour the intent**: if a role's `tools:` has no `Write`/`Edit`, it is read-only, so don't modify source files while acting as it. |

## Environment variables and paths

| Claude Code | Antigravity |
|---|---|
| `$CLAUDE_SKILL_DIR` | The skill's own directory. Installed copies state it at the top of their `SKILL.md` under "Antigravity notes". Antigravity shells don't set it, so write the path inline, or prefix commands with `CLAUDE_SKILL_DIR=<path>`. |
| `$CLAUDE_PROJECT_DIR` | The workspace / repository root. |
| `$ARGUMENTS` (slash commands) | Whatever the user wrote after invoking the skill, e.g. `/backlog-run --local` gives `--local`. Empty if nothing was given. |
| `~/.claude/...` (any path) | **Not readable here.** Antigravity's default file policy denies `read_file` under `~/.claude/`, even through symlinks. Global skills from `~/.claude/skills` are installed as **copies** in `~/.gemini/config/skills/` (refresh them with `install-global-skills.py`). Don't use `cat` or similar to get around the policy. Workspace `.claude/` directories (inside the repo) *are* readable. |
| `CLAUDE.md` | In repos with the layered setup, `AGENTS.md` is the harness-neutral briefing, and Antigravity already loads it via the `GEMINI.md` symlink. `CLAUDE.md` adds Claude-only mechanics. Read it for context, but treat its hooks and plan-mode sections as **not active** here. |
| "Claude Code" (as a capability, e.g. "requires Claude Code shell access") | Antigravity: you have shell, file and web tools. |

## Sub-agents ("use the X agent", `Agent`/`Task` tool, `isolation: worktree`)

Pick the first option your surface supports.

### 1. Custom subagent (Antigravity App and CLI)
If you have the `invoke_subagent` tool and the repo has `.agents/agents/<role>.md`
(dep-scan generates these with `scripts/sync-agy-skills.py`), invoke that subagent
with the dispatch prompt the Claude file would have sent. It runs in its own
context with the role's mapped tools (`view_file`, `write_to_file`,
`replace_file_content`, `grep_search`, `run_command`) and model (`opus` maps to
`pro`, everything else inherits). This is the real equivalent of Claude's
sub-agent dispatch. For worktree isolation, create the worktree first and tell
the subagent to work only there (pass the path as `Cwd`).

### 2. Inline (IDE, or no subagent tool)
The Antigravity IDE has no custom subagents. Read the role file, act as that role
in the current conversation, produce the output the role specifies, then go back
to the main task.

For **verification** roles (spec-verifier, qa, code-reviewer), a self-review is
weaker than an independent check. State `verification: inline (same agent)` in the
report, so nobody mistakes it for an independent gate. If the user wants a real
independent gate, use option 3.

### 3. Isolated: a headless Antigravity agent
```bash
agy -p "Invoke the <role> subagent: <the dispatch prompt>" --print-timeout 0
```
- Set the `Cwd` to the repo root, or to the task's worktree for worktree-isolated
  dispatches (create it first, e.g. with the repo's `scripts/start-task.sh`).
- The child auto-loads the repo's `AGENTS.md`/`GEMINI.md`, `.agents/` skills,
  subagents and hooks.
- Long runs: launch as a background command and wait for the completion
  notification. Don't poll.
- Parallel dispatches (`*-parallel` commands): one `agy -p` per task, each in its
  **own worktree**, at most 3 or 4 at once. Run `scripts/verify-worktree-isolation.sh`
  (if present) before and after.

**Headless permission limit (verified on this machine, 2026-10-25):** `agy -p`
cannot prompt, so any shell command or file write that isn't allow-listed is
**auto-denied**, and the child finishes without doing the work. `--mode auto` is
unavailable because this host has no terminal sandbox. Before an isolated
dispatch, check that `~/.gemini/antigravity-cli/settings.json` →
`permissions.allow` covers what the role needs (e.g. `command(cargo)`,
`command(git)`, `write_file(...)`). If it doesn't, **fall back to inline and
tell the user**. Do not edit that settings file yourself. Never add
`--dangerously-skip-permissions` without the user's explicit approval for that
run.

## Hooks

Claude Code hooks live in `.claude/settings.json` → `.claude/scripts/*.py`.
dep-scan runs the safety subset in Antigravity through `.agents/hooks.json` and
`.agents/hooks/claude_hook_adapter.py`, which feeds the same scripts a
Claude-shaped payload:

| Claude hook | Antigravity |
|---|---|
| PreToolUse Bash: block-no-verify, protect-checkout, no-commit-on-main, spec-coverage-check | PreToolUse on `run_command`; a block becomes a tool denial with the script's message |
| PreToolUse Write/Edit: protect-secrets, config-protection | PreToolUse on `write_to_file`, `replace_file_content`, `multi_replace_file_content` (IDE) and `write_file`, `edit_file` (CLI) |
| SessionStart: inject-retros | PreInvocation, first model call of each turn, as an ephemeral message |
| Everything else (compaction, session lock, plan restructuring, edit tracker, Stop checks, notifications) | Not ported |

Verified in the CLI. The IDE may not load workspace hooks, so in every surface
enforce the rules yourself as well:

- Don't commit to the default branch without the repo's escape tag (e.g. `[allow-main]`).
- Never `git checkout -- <path>` over uncommitted work.
- Never `git commit --no-verify`.
- Don't read or print secrets files (`.env`, private keys, credentials).
- At session start, read the repo's retro log (e.g. `docs/agent-rules.md`) yourself.
- Plan mode: the exit-plan hook that converts plans into backlog task files doesn't run. Write the task files and test specs by hand, following the repo's conventions.

