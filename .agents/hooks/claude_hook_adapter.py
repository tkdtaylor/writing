#!/usr/bin/env python3
"""Run this repo's Claude Code hook scripts from Antigravity hooks.

The canonical hooks live in .claude/scripts/ (managed by create-project; do not
edit them for Antigravity). They speak Claude's hook contract: a JSON payload
on stdin with tool_name / tool_input, exit 2 plus stderr to block, and
hookSpecificOutput.additionalContext to add context. Antigravity sends a
different payload and expects a different reply, so this adapter translates.

Usage (from .agents/hooks.json, cwd = .agents/):
  claude_hook_adapter.py pre <script> [<script> ...]
      PreToolUse. Maps the agy tool call to the Claude payload and runs each
      script. The first exit 2 becomes {"decision": "deny", "reason": ...}.
      If nothing blocks, prints nothing, which defers to normal permissions.
      (Printing "{}" would deny: an empty decision is treated as a denial.)
  claude_hook_adapter.py context <script> [<script> ...]
      PreInvocation. On the first model call of each user turn, runs each
      script and injects its additionalContext as an ephemeral message.
      Stands in for Claude's SessionStart hooks.

Profile gating (CLAUDE_HOOK_PROFILE, CLAUDE_DISABLED_HOOKS) is inherited from
the environment and applied by the scripts themselves.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".claude" / "scripts"
TIMEOUT = 20

SHELL_TOOLS = {"run_command"}
# IDE names first, then CLI names. Both surfaces send their own names to hooks.
WRITE_TOOLS = {
    "write_to_file": "Write",
    "write_file": "Write",
    "replace_file_content": "Edit",
    "multi_replace_file_content": "Edit",
    "edit_file": "Edit",
}
PATH_KEYS = ("TargetFile", "Path", "AbsolutePath", "FilePath")


def claude_payload(tool: str, args: dict) -> tuple[dict, str | None] | None:
    """Return (Claude payload, cwd) for a tool call, or None if no hook applies."""
    if tool in SHELL_TOOLS:
        cwd = args.get("Cwd") or None
        return {"tool_name": "Bash", "tool_input": {"command": args.get("CommandLine", "")}}, cwd
    if tool in WRITE_TOOLS:
        path = next((args[k] for k in PATH_KEYS if args.get(k)), "")
        return {"tool_name": WRITE_TOOLS[tool], "tool_input": {"file_path": path}}, None
    return None


def run_script(name: str, payload: dict, cwd: str | None) -> subprocess.CompletedProcess:
    script = SCRIPTS / f"{name}.py"
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    run_cwd = cwd if cwd and Path(cwd).is_dir() else str(ROOT)
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=run_cwd,
        env=env,
        timeout=TIMEOUT,
        check=False,
    )


def pre(event: dict, scripts: list[str]) -> None:
    call = event.get("toolCall") or {}
    mapped = claude_payload(call.get("name", ""), call.get("args") or {})
    if mapped is None:
        return
    payload, cwd = mapped
    for name in scripts:
        if not (SCRIPTS / f"{name}.py").exists():
            # Fail closed: a missing safety hook means the guard is gone.
            deny(f"hook script .claude/scripts/{name}.py is missing; refusing until restored")
            return
        try:
            res = run_script(name, payload, cwd)
        except subprocess.TimeoutExpired:
            deny(f"hook {name} timed out after {TIMEOUT}s")
            return
        if res.returncode == 2:
            deny(res.stderr.strip() or f"blocked by {name}")
            return


def deny(reason: str) -> None:
    print(json.dumps({"decision": "deny", "reason": reason}))


def context(event: dict, scripts: list[str]) -> None:
    if event.get("invocationNum", 0) != 0:
        return
    parts = []
    for name in scripts:
        if not (SCRIPTS / f"{name}.py").exists():
            continue
        try:
            res = run_script(name, {"hook_event_name": "SessionStart"}, None)
        except subprocess.TimeoutExpired:
            continue
        try:
            out = json.loads(res.stdout) if res.stdout.strip() else {}
        except json.JSONDecodeError:
            continue
        ctx = (out.get("hookSpecificOutput") or {}).get("additionalContext")
        if ctx:
            parts.append(ctx)
    if parts:
        print(json.dumps({"injectSteps": [{"ephemeralMessage": "\n\n".join(parts)}]}))


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in {"pre", "context"}:
        print(__doc__, file=sys.stderr)
        return 1
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        event = {}
    if sys.argv[1] == "pre":
        pre(event, sys.argv[2:])
    else:
        context(event, sys.argv[2:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
