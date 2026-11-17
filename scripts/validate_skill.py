#!/usr/bin/env python3
"""validate_skill.py - Skill package and prose hygiene validator CLI.

Uses only the Python 3.10+ standard library (plus sibling strip_markdown.py).
Enforces SKILL.md frontmatter and context-window word budgets, routing and
relative Markdown link integrity, slash-command mode= token symmetry,
evals/*.json schemas, and repository prose hygiene (zero prose \u2014, zero
emoji bullets, and zero hard-wrapped paragraphs).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote

try:
    from scripts import strip_markdown as _strip_md
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    import strip_markdown as _strip_md  # type: ignore[no-redef]

SKILL_MAX_WORDS = 1500
REFERENCE_MAX_WORDS = 1500
COMBINED_RUNTIME_BUDGET = 10000
COMBINED_MAX_WORDS = COMBINED_RUNTIME_BUDGET

REQUIRED_RUNTIME_SCRIPTS = (
    "strip_markdown.py",
    "prose_lint.py",
)

EXPECTED_EVAL_MODES = frozenset({"draft", "edit", "review", "lint"})
EXPECTED_EVAL_CATEGORIES = frozenset(
    {
        "factual_fidelity",
        "medium_fit",
        "false_positive_restraint",
        "voice_sample_boundary",
        "mode_boundary",
        "prompt_injection_isolation",
    }
)
REQUIRED_EVAL_KEYS = (
    "id",
    "eval_name",
    "category",
    "mode",
    "prompt",
    "expected_output",
    "assertions",
)

_EM_DASH_CHAR = "\u2014"

_FENCE_OPEN_RE = re.compile(r"^(?:\s*>)*\s*(`{3,}|~{3,})(.*)$")
_INLINE_CODE_RE = re.compile(r"(`+)([^`]+?)\1")
_MODE_TOKEN_RE = re.compile(r"\bmode=([A-Za-z0-9_-]+)\b")

_IGNORED_LINK_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "file://",
    "conversation://",
    "tel:",
    "data:",
    "javascript:",
    "#",
)

_LINK_TARGET_EXPR = r"<[^>]+>|(?:[^()\s]+|\([^()]*\))+(?:\s+(?:\"[^\"]*\"|'[^']*'))?"
_IMAGE_LINK_RE = re.compile(rf"!\[([^\]]*)\]\(({_LINK_TARGET_EXPR})\)")
_MD_LINK_RE = re.compile(
    rf"(?<!!)\[((?:[^\[\]]|\[[^\[\]]*\])*)\]\(({_LINK_TARGET_EXPR})\)"
)

_EMOJI_CHAR_CLASS = (
    r"[\U0001F300-\U0001FAFF"
    r"\u2600-\u26FF"
    r"\u2700-\u27BF"
    r"\u2B50\u2B55]"
)
_EMOJI_BULLET_RE = re.compile(
    rf"^\s*(?:(?:[-*+]|\d+[.)])\s*{_EMOJI_CHAR_CLASS}|{_EMOJI_CHAR_CLASS}\ufe0f?\s+\S)"
)

_ROOT_AUTHORED_DOCS = (
    "SKILL.md",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
)

_PROSE_EXEMPT_PREFIXES = (
    ".claude/",
    ".agents/",
    ".git/",
    "docs/tasks/",
    "training/",
)


def _count_words(text: str) -> int:
    """Count whitespace-delimited tokens matching context budget tests."""
    return len(text.split())


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, bool]:
    """Parse top-of-file YAML frontmatter into (fields, body, has_frontmatter)."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, normalized, False

    end_idx = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() in {"---", "..."}:
            end_idx = idx
            break
    if end_idx < 0:
        return {}, normalized, False

    raw_fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    parsed: dict[str, str] = {}
    current_key: str | None = None
    continuation: list[str] = []

    def flush() -> None:
        nonlocal current_key, continuation
        if current_key is not None and continuation:
            parsed[current_key] = " ".join(continuation).strip()
        current_key = None
        continuation = []

    for line in raw_fm_lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_key is not None:
            continuation.append(line.strip())
            continue
        flush()
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in {"", ">", ">-", "|", "|-"}:
                current_key = key
                parsed[key] = ""
            else:
                if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
                    val = val[1:-1]
                parsed[key] = val.strip()
                current_key = key
                continuation = [parsed[key]] if parsed[key] else []
    flush()
    return parsed, body, True


def _iter_non_fenced_lines(
    text: str, skip_frontmatter: bool = False
) -> list[tuple[int, str]]:
    """Return (1-based line_number, comment-masked line) outside fenced code blocks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = normalized.split("\n")
    masked = _strip_md._mask_html_comments(normalized).split("\n")

    start_idx = 0
    if skip_frontmatter:
        fm_end = _strip_md._find_frontmatter_end(raw_lines)
        if fm_end >= 0:
            start_idx = fm_end + 1

    out: list[tuple[int, str]] = []
    fence_char = ""
    fence_len = 0
    for idx in range(start_idx, len(masked)):
        line = masked[idx]
        if not fence_char:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                marker, rest = m.group(1), m.group(2)
                if not (marker[0] == "`" and "`" in rest):
                    fence_char = marker[0]
                    fence_len = len(marker)
                    continue
            out.append((idx + 1, line))
        else:
            close_re = re.compile(
                rf"^(?:\s*>)*\s*{re.escape(fence_char)}{{{fence_len},}}\s*$"
            )
            if close_re.match(line):
                fence_char = ""
                fence_len = 0
    return out


def _extract_mode_tokens(text: str) -> list[str]:
    """Extract mode=<token> values outside fenced code blocks and frontmatter."""
    tokens: list[str] = []
    for _, line in _iter_non_fenced_lines(text, skip_frontmatter=True):
        for match in _MODE_TOKEN_RE.finditer(line):
            tokens.append(match.group(1))
    return tokens


def _is_prose_hygiene_exempt(rel_posix: str) -> bool:
    """Return True if rel_posix is explicitly exempt from prose hygiene checks."""
    if rel_posix == "CODE_OF_CONDUCT.md":
        return True
    if rel_posix.endswith(".before.md"):
        return True
    return rel_posix.startswith(_PROSE_EXEMPT_PREFIXES)


def _clean_link_target(raw_expr: str) -> str:
    """Normalize a Markdown link target expression, stripping titles and fragments."""
    expr = raw_expr.strip()
    if expr.startswith("<") and ">" in expr:
        target = expr[1 : expr.index(">")].strip()
    else:
        target = expr.split()[0] if expr else ""
    return target


def _extract_links_from_line(line: str) -> list[str]:
    """Extract Markdown link and image targets from a single non-fenced line."""
    no_code = _INLINE_CODE_RE.sub(" ", line)
    targets: list[str] = []

    def _collect_image(match: re.Match[str]) -> str:
        targets.append(_clean_link_target(match.group(2)))
        return match.group(1)

    working = _IMAGE_LINK_RE.sub(_collect_image, no_code)

    for _ in range(3):
        found_in_pass = False

        def _collect_link(match: re.Match[str]) -> str:
            nonlocal found_in_pass
            found_in_pass = True
            targets.append(_clean_link_target(match.group(2)))
            return match.group(1)

        updated = _MD_LINK_RE.sub(_collect_link, working)
        working = updated
        if not found_in_pass:
            break

    return [t for t in targets if t]


def _collect_link_check_files(root: Path) -> list[Path]:
    """Collect Markdown files subject to relative-link validation."""
    candidates: list[Path] = []
    for name in _ROOT_AUTHORED_DOCS:
        p = root / name
        if p.is_file() and not p.is_symlink():
            candidates.append(p)

    for pattern in (
        "references/*.md",
        "commands/*.md",
        "docs/**/*.md",
        "samples/README.md",
        "samples/*.after.md",
        "evals/JUDGE.md",
    ):
        for p in sorted(root.glob(pattern)):
            if p.is_file() and not p.is_symlink():
                candidates.append(p)

    seen: set[Path] = set()
    unique: list[Path] = []
    for p in candidates:
        rel_posix = p.relative_to(root).as_posix()
        if rel_posix.startswith((".claude/", ".agents/", ".git/")):
            continue
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(p)
    return unique


def _collect_prose_hygiene_files(root: Path) -> list[Path]:
    """Collect authored Markdown files subject to repository prose hygiene rules."""
    candidates: list[Path] = []
    for name in _ROOT_AUTHORED_DOCS:
        p = root / name
        if p.is_file() and not p.is_symlink():
            candidates.append(p)

    for pattern in (
        "commands/**/*.md",
        "references/**/*.md",
        "docs/**/*.md",
        "samples/**/*.md",
        "evals/**/*.md",
    ):
        for p in sorted(root.glob(pattern)):
            if p.is_file() and not p.is_symlink():
                candidates.append(p)

    seen: set[Path] = set()
    authored: list[Path] = []
    for p in candidates:
        rel_posix = p.relative_to(root).as_posix()
        if _is_prose_hygiene_exempt(rel_posix):
            continue
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            authored.append(p)
    return authored


def _check_frontmatter_and_budgets(
    root: Path,
) -> tuple[dict[str, Any], dict[str, str], str | None, dict[str, Any]]:
    """REQ-006-01: Validate SKILL.md frontmatter and context-window word budgets."""
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    skill_fm: dict[str, str] = {}
    skill_text: str | None = None
    skill_words = 0

    if not skill_path.is_file():
        errors.append("SKILL.md: file not found")
    else:
        skill_text = skill_path.read_text(encoding="utf-8")
        skill_words = _count_words(skill_text)
        skill_fm, skill_body, has_fm = parse_frontmatter(skill_text)
        if not has_fm:
            errors.append("SKILL.md: missing top-of-file YAML frontmatter (---)")
        else:
            if not skill_fm.get("name", "").strip():
                errors.append("SKILL.md: frontmatter missing non-empty 'name'")
            if not skill_fm.get("description", "").strip():
                errors.append("SKILL.md: frontmatter missing non-empty 'description'")
        if not skill_body.strip():
            errors.append("SKILL.md: body content is empty")
        if skill_words > SKILL_MAX_WORDS:
            errors.append(
                f"SKILL.md: word count {skill_words} exceeds {SKILL_MAX_WORDS}-word budget"
            )

    refs_dir = root / "references"
    ref_counts: dict[str, int] = {}
    if not refs_dir.is_dir():
        errors.append("references/: directory not found")
    else:
        ref_files = sorted(p for p in refs_dir.glob("*.md") if p.is_file())
        if not ref_files:
            errors.append("references/: no reference Markdown files found")
        for ref_path in ref_files:
            rel_key = f"references/{ref_path.name}"
            words = _count_words(ref_path.read_text(encoding="utf-8"))
            ref_counts[rel_key] = words
            if words > REFERENCE_MAX_WORDS:
                errors.append(
                    f"{rel_key}: word count {words} exceeds {REFERENCE_MAX_WORDS}-word budget"
                )

    combined_words = skill_words + sum(ref_counts.values())
    if combined_words > COMBINED_RUNTIME_BUDGET:
        errors.append(
            f"combined runtime prose: word count {combined_words} exceeds {COMBINED_RUNTIME_BUDGET}-word budget"
        )

    word_counts: dict[str, Any] = {
        "SKILL.md": skill_words,
        "references": ref_counts,
        "combined_runtime": combined_words,
    }
    check = {
        "name": "frontmatter_and_budgets",
        "passed": len(errors) == 0,
        "errors": errors,
    }
    return check, skill_fm, skill_text, word_counts


def _check_routing_and_links(
    root: Path, skill_text: str | None
) -> dict[str, Any]:
    """REQ-006-02: Validate routing reachability, mode= symmetry, and relative links."""
    errors: list[str] = []
    root_resolved = root.resolve()

    if skill_text is not None:
        refs_dir = root / "references"
        if refs_dir.is_dir():
            for ref_path in sorted(p for p in refs_dir.glob("*.md") if p.is_file()):
                rel_ref = f"references/{ref_path.name}"
                if rel_ref not in skill_text:
                    errors.append(
                        f"{rel_ref}: unreferenced in SKILL.md routing table or steps"
                    )

        for script_name in REQUIRED_RUNTIME_SCRIPTS:
            script_rel = f"scripts/{script_name}"
            if not (root / "scripts" / script_name).is_file():
                errors.append(f"{script_rel}: runtime script file not found")
            if script_rel not in skill_text and script_name not in skill_text:
                errors.append(f"{script_rel}: runtime script not referenced in SKILL.md")

        commands_dir = root / "commands"
        if commands_dir.is_dir():
            skill_modes = set(_extract_mode_tokens(skill_text))
            cmd_files = sorted(p for p in commands_dir.glob("*.md") if p.is_file())
            write_cmd_files = [
                p for p in cmd_files if p.name.startswith("write-")
            ]
            all_cmd_modes: set[str] = set()

            for cmd_path in cmd_files:
                rel_cmd = f"commands/{cmd_path.name}"
                slash_token = f"/{cmd_path.stem}"
                if rel_cmd not in skill_text and slash_token not in skill_text:
                    errors.append(f"{rel_cmd}: command file not referenced in SKILL.md")

            for cmd_path in write_cmd_files:
                rel_cmd = f"commands/{cmd_path.name}"
                cmd_text = cmd_path.read_text(encoding="utf-8")
                cmd_fm, _, has_fm = parse_frontmatter(cmd_text)
                if not has_fm or not cmd_fm.get("description", "").strip():
                    errors.append(
                        f"{rel_cmd}: missing non-empty 'description' frontmatter"
                    )

                cmd_modes = set(_extract_mode_tokens(cmd_text))
                expected_slug = cmd_path.stem[len("write-") :]
                if not cmd_modes:
                    errors.append(f"{rel_cmd}: missing mode=<token> routing token")
                else:
                    all_cmd_modes.update(cmd_modes)
                    if cmd_modes != {expected_slug}:
                        errors.append(
                            f"{rel_cmd}: mode= token {sorted(cmd_modes)} does not match command stem '{expected_slug}'"
                        )
                    for tok in sorted(cmd_modes):
                        if tok not in skill_modes:
                            errors.append(
                                f"{rel_cmd}: mode={tok} does not appear in SKILL.md"
                            )

            if write_cmd_files:
                for tok in sorted(skill_modes):
                    if tok not in all_cmd_modes:
                        errors.append(
                            f"SKILL.md: mode={tok} has no matching commands/write-{tok}.md file"
                        )

    for md_path in _collect_link_check_files(root):
        rel_posix = md_path.relative_to(root).as_posix()
        text = md_path.read_text(encoding="utf-8")
        for lineno, line in _iter_non_fenced_lines(text, skip_frontmatter=True):
            for raw_target in _extract_links_from_line(line):
                lower_target = raw_target.lower()
                if lower_target.startswith(_IGNORED_LINK_PREFIXES):
                    continue
                path_part = raw_target.split("#", 1)[0].split("?", 1)[0]
                path_part = unquote(path_part).strip()
                if not path_part:
                    continue
                if path_part.startswith("/"):
                    candidate = (root_resolved / path_part.lstrip("/")).resolve()
                else:
                    candidate = (md_path.parent / path_part).resolve()

                if not candidate.is_relative_to(root_resolved):
                    errors.append(
                        f"{rel_posix}:{lineno}: relative link '{raw_target}' escapes repository root"
                    )
                elif not candidate.exists():
                    errors.append(
                        f"{rel_posix}:{lineno}: broken relative link '{raw_target}'"
                    )

    return {
        "name": "routing_and_links",
        "passed": len(errors) == 0,
        "errors": errors,
    }


def _check_eval_schemas(root: Path, skill_fm: dict[str, str]) -> dict[str, Any]:
    """REQ-006-03: Validate evals/evals.json and evals/trigger-evals.json when present."""
    errors: list[str] = []
    expected_skill_name = skill_fm.get("name", "").strip()

    evals_path = root / "evals" / "evals.json"
    if evals_path.is_file():
        try:
            data = json.loads(evals_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"evals/evals.json: invalid JSON ({exc.msg} at line {exc.lineno})")
            data = None

        if data is not None:
            if not isinstance(data, dict):
                errors.append("evals/evals.json: top-level JSON value must be an object")
            else:
                sname = data.get("skill_name")
                if not isinstance(sname, str) or not sname.strip():
                    errors.append("evals/evals.json: missing non-empty 'skill_name'")
                elif expected_skill_name and sname != expected_skill_name:
                    errors.append(
                        f"evals/evals.json: skill_name '{sname}' does not match SKILL.md name '{expected_skill_name}'"
                    )

                evals_list = data.get("evals")
                if not isinstance(evals_list, list) or len(evals_list) == 0:
                    errors.append("evals/evals.json: 'evals' must be a non-empty list")
                else:
                    seen_ids: set[Any] = set()
                    modes_seen: set[str] = set()
                    categories_seen: set[str] = set()

                    for idx, item in enumerate(evals_list):
                        prefix = f"evals/evals.json[evals[{idx}]]"
                        if not isinstance(item, dict):
                            errors.append(f"{prefix}: entry must be an object")
                            continue

                        missing = [k for k in REQUIRED_EVAL_KEYS if k not in item]
                        if missing:
                            errors.append(f"{prefix}: missing required keys: {', '.join(missing)}")
                            continue

                        eid = item["id"]
                        if isinstance(eid, bool) or not isinstance(eid, (int, str)) or (
                            isinstance(eid, str) and not eid.strip()
                        ):
                            errors.append(f"{prefix}: 'id' must be an int or non-empty string")
                        elif eid in seen_ids:
                            errors.append(f"{prefix}: duplicate eval id '{eid}'")
                        else:
                            seen_ids.add(eid)

                        for str_key in ("eval_name", "prompt", "expected_output"):
                            val = item[str_key]
                            if not isinstance(val, str) or not val.strip():
                                errors.append(f"{prefix}: '{str_key}' must be a non-empty string")

                        cat = item["category"]
                        if not isinstance(cat, str) or cat not in EXPECTED_EVAL_CATEGORIES:
                            errors.append(
                                f"{prefix}: invalid category '{cat}' (expected one of {sorted(EXPECTED_EVAL_CATEGORIES)})"
                            )
                        else:
                            categories_seen.add(cat)

                        mode = item["mode"]
                        if not isinstance(mode, str) or mode not in EXPECTED_EVAL_MODES:
                            errors.append(
                                f"{prefix}: invalid mode '{mode}' (expected one of {sorted(EXPECTED_EVAL_MODES)})"
                            )
                        else:
                            modes_seen.add(mode)

                        assertions = item["assertions"]
                        if (
                            not isinstance(assertions, list)
                            or len(assertions) == 0
                            or not all(isinstance(a, str) and a.strip() for a in assertions)
                        ):
                            errors.append(
                                f"{prefix}: 'assertions' must be a non-empty list of non-empty strings"
                            )

                        if "files" in item:
                            files_val = item["files"]
                            if not isinstance(files_val, list) or not all(
                                isinstance(f, str) for f in files_val
                            ):
                                errors.append(f"{prefix}: 'files' must be a list of strings")

                    missing_modes = sorted(EXPECTED_EVAL_MODES - modes_seen)
                    if missing_modes:
                        errors.append(
                            f"evals/evals.json: missing mode coverage for: {', '.join(missing_modes)}"
                        )
                    missing_cats = sorted(EXPECTED_EVAL_CATEGORIES - categories_seen)
                    if missing_cats:
                        errors.append(
                            f"evals/evals.json: missing category coverage for: {', '.join(missing_cats)}"
                        )

    triggers_path = root / "evals" / "trigger-evals.json"
    if triggers_path.is_file():
        try:
            tdata = json.loads(triggers_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(
                f"evals/trigger-evals.json: invalid JSON ({exc.msg} at line {exc.lineno})"
            )
            tdata = None

        if tdata is not None:
            if not isinstance(tdata, list) or len(tdata) == 0:
                errors.append(
                    "evals/trigger-evals.json: top-level JSON value must be a non-empty list"
                )
            else:
                has_positive = False
                has_negative = False
                for idx, entry in enumerate(tdata):
                    prefix = f"evals/trigger-evals.json[{idx}]"
                    if not isinstance(entry, dict):
                        errors.append(f"{prefix}: entry must be an object")
                        continue
                    query = entry.get("query")
                    if not isinstance(query, str) or not query.strip():
                        errors.append(f"{prefix}: 'query' must be a non-empty string")
                    trig = entry.get("should_trigger")
                    if not isinstance(trig, bool):
                        errors.append(f"{prefix}: 'should_trigger' must be a boolean")
                    elif trig:
                        has_positive = True
                    else:
                        has_negative = True

                if not has_positive:
                    errors.append(
                        "evals/trigger-evals.json: must contain at least one should_trigger=true entry"
                    )
                if not has_negative:
                    errors.append(
                        "evals/trigger-evals.json: must contain at least one should_trigger=false entry"
                    )

    return {
        "name": "eval_schemas",
        "passed": len(errors) == 0,
        "errors": errors,
    }


def _check_prose_hygiene(root: Path) -> dict[str, Any]:
    """REQ-006-04: Enforce prose hygiene across authored Markdown files."""
    errors: list[str] = []

    for md_path in _collect_prose_hygiene_files(root):
        rel_posix = md_path.relative_to(root).as_posix()
        text = md_path.read_text(encoding="utf-8")

        for lineno, line in _iter_non_fenced_lines(text, skip_frontmatter=False):
            if not line.strip():
                continue
            no_code = _strip_md.mask_inline_syntax_for_tells(line)
            if _EM_DASH_CHAR in no_code:
                errors.append(
                    f"{rel_posix}:{lineno}: prose em dash (U+2014) is disallowed"
                )
            if _EMOJI_BULLET_RE.match(no_code):
                errors.append(
                    f"{rel_posix}:{lineno}: emoji bullet line is disallowed in authored prose"
                )

        md_struct = _strip_md.extract_markdown_structure(text)
        if md_struct.hard_wrapped_lines:
            lines_str = ", ".join(str(ln) for ln in md_struct.hard_wrapped_lines)
            errors.append(
                f"{rel_posix}: hard-wrapped multi-line paragraph lines detected: {lines_str}"
            )

    return {
        "name": "prose_hygiene",
        "passed": len(errors) == 0,
        "errors": errors,
    }


def validate_repo(root: Path) -> dict[str, Any]:
    """Validate skill package budgets, routing, links, eval schemas, and prose hygiene."""
    root_path = Path(root)
    fm_check, skill_fm, skill_text, word_counts = _check_frontmatter_and_budgets(
        root_path
    )
    routing_check = _check_routing_and_links(root_path, skill_text)
    eval_check = _check_eval_schemas(root_path, skill_fm)
    hygiene_check = _check_prose_hygiene(root_path)

    checks = [fm_check, routing_check, eval_check, hygiene_check]
    all_errors = [err for chk in checks for err in chk["errors"]]
    return {
        "passed": len(all_errors) == 0,
        "checks": checks,
        "errors": all_errors,
        "word_counts": word_counts,
    }


def _format_human_report(result: dict[str, Any], root: Path) -> str:
    """Format a concise human-readable validation summary."""
    status = "PASS" if result["passed"] else "FAIL"
    lines = [f"Skill package validation: {status} (root: {root})"]
    for chk in result["checks"]:
        chk_status = "PASS" if chk["passed"] else "FAIL"
        err_cnt = len(chk["errors"])
        suffix = f" ({err_cnt} error{'s' if err_cnt != 1 else ''})" if err_cnt else ""
        lines.append(f"  [{chk_status}] {chk['name']}{suffix}")

    wc = result["word_counts"]
    refs = wc.get("references", {})
    max_ref = max(refs.values(), default=0)
    lines.append(
        f"Word budgets: SKILL.md={wc['SKILL.md']}/{SKILL_MAX_WORDS}, "
        f"references={len(refs)} (max {max_ref}/{REFERENCE_MAX_WORDS}), "
        f"combined={wc['combined_runtime']}/{COMBINED_MAX_WORDS}"
    )

    if result["errors"]:
        lines.append(f"Errors ({len(result['errors'])}):")
        for err in result["errors"]:
            lines.append(f"  - {err}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        prog="validate_skill.py",
        description=(
            "Validate skill frontmatter, context word budgets, routing and link "
            "integrity, eval schemas, and repository prose hygiene."
        ),
    )
    parser.add_argument(
        "--root",
        default=str(default_root),
        help="Repository root directory to validate (defaults to repo root).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit validation report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    root = Path(args.root)
    if not root.is_dir():
        print(f"error: root directory not found: {args.root}", file=sys.stderr)
        return 2

    result = validate_repo(root)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human_report(result, root))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
