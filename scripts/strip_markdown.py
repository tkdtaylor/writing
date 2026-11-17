#!/usr/bin/env python3
"""strip_markdown.py - Strip Markdown syntax to clean reader-visible prose.

Uses only the Python 3.10+ standard library. Separates headings from body
paragraphs, strips YAML frontmatter, fenced code blocks, HTML comments, pipe
tables, images, and link URL targets (preserving anchor text), and detects
hard-wrapped consecutive prose lines.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019-][A-Za-z0-9]+)*")
_FRONTMATTER_OPEN_RE = re.compile(r"^---\s*$")
_FRONTMATTER_CLOSE_RE = re.compile(r"^(?:---|\.\.\.)\s*$")
_FENCE_OPEN_RE = re.compile(r"^(?:\s*>)*\s*(`{3,}|~{3,})(.*)$")
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")
_REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*\S+.*$")
_ATX_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})(?:\s+(.*?))?\s*#*\s*$")
_SETEXT_UNDERLINE_RE = re.compile(r"^\s{0,3}(?:={2,}|-{2,})\s*$")
_HR_RE = re.compile(r"^\s{0,3}(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})$")
_LIST_ITEM_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
_TASK_MARKER_RE = re.compile(r"^\[[ xX]\]\s+")
_BLOCKQUOTE_RE = re.compile(r"^\s*(?:>\s?)+(.*)$")
_TABLE_DELIM_RE = re.compile(
    r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?\s*$"
)
_PIPE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_STANDALONE_HTML_BLOCK_RE = re.compile(r"^\s{0,3}</?[A-Za-z][^>]*>\s*$")
_STANDALONE_BADGE_OR_IMAGE_RE = re.compile(
    r"^\s{0,3}(?:!\[[^\]]*\]\([^)]*\)|\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\))\s*$"
)
_IMPORT_DIRECTIVE_RE = re.compile(r"^@[A-Za-z0-9_./-]+\s*$")
_KV_LINE_RE = re.compile(
    r"^(?:\*\*[^*]+:\*\*|\*\*[^*]+\*\*:|[A-Z][A-Za-z0-9 _/-]{1,24}:\s+\S)"
)

# Inline cleanup patterns
_BADGE_LINK_RE = re.compile(
    r"\[!\[[^\]]*\]\((?:[^()\s]+|\([^()]*\))+(?:\s+\"[^\"]*\")?\)\]"
    r"\((?:[^()\s]+|\([^()]*\))+(?:\s+\"[^\"]*\")?\)"
)
_INLINE_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\((?:[^()\s]+|\([^()]*\))+(?:\s+\"[^\"]*\")?\)"
)
_REF_IMAGE_RE = re.compile(r"!\[[^\]]*\]\[[^\]]*\]")
_INLINE_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((?:[^()\s]+|\([^()]*\))+(?:\s+\"[^\"]*\")?\)"
)
_REF_LINK_RE = re.compile(r"\[([^\]]+)\]\[[^\]]*\]")
_AUTOLINK_RE = re.compile(r"<(?:https?://|mailto:)[^>]+>")
_BR_TAG_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s+[^<>]*)?>")
_INLINE_CODE_RE = re.compile(r"(`+)([^`]+?)\1")
_BOLD_ITALIC_RE = re.compile(r"(\*{3}|_{3})(.+?)\1")
_BOLD_RE = re.compile(r"(\*{2}|_{2})(.+?)\1")
_ITALIC_STAR_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
_ITALIC_UNDER_RE = re.compile(r"(?<![A-Za-z0-9])_([^_\n]+?)_(?![A-Za-z0-9])")
_STRIKE_RE = re.compile(r"~~(.+?)~~")
_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|])")


@dataclass(frozen=True)
class MarkdownStructure:
    """Line-aware extracted Markdown structure shared with prose_lint.py."""

    paragraphs_with_lines: list[tuple[int, str]]
    prose_without_code_with_lines: list[tuple[int, str]]
    headings_with_lines: list[tuple[int, str]]
    hard_wrapped_lines: list[int]
    masked_lines: list[str]
    raw_lines: list[str]


def _mask_html_comments(text: str) -> str:
    """Replace HTML comments with spaces while preserving newline positions."""

    def _repl(match: re.Match[str]) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in match.group(0))

    return _HTML_COMMENT_RE.sub(_repl, text)


def clean_inline_markdown(text: str, keep_code_text: bool = True) -> str:
    """Strip inline Markdown formatting while keeping reader-visible prose."""
    code_spans: list[str] = []

    def _stash_code(match: re.Match[str]) -> str:
        idx = len(code_spans)
        code_spans.append(match.group(2))
        return f"\x01CODE{idx}\x02"

    s = _INLINE_CODE_RE.sub(_stash_code, text)
    s = _BADGE_LINK_RE.sub("", s)
    s = _INLINE_IMAGE_RE.sub("", s)
    s = _REF_IMAGE_RE.sub("", s)
    s = _BR_TAG_RE.sub(" ", s)
    s = _AUTOLINK_RE.sub("", s)

    # Iteratively unwrap nested or adjacent Markdown links.
    for _ in range(3):
        updated = _INLINE_LINK_RE.sub(r"\1", s)
        updated = _REF_LINK_RE.sub(r"\1", updated)
        if updated == s:
            break
        s = updated

    s = _HTML_TAG_RE.sub("", s)
    s = _BOLD_ITALIC_RE.sub(r"\2", s)
    s = _BOLD_RE.sub(r"\2", s)
    s = _ITALIC_STAR_RE.sub(r"\1", s)
    s = _ITALIC_UNDER_RE.sub(r"\1", s)
    s = _STRIKE_RE.sub(r"\1", s)
    s = _ESCAPE_RE.sub(r"\1", s)

    for idx, code_txt in enumerate(code_spans):
        replacement = code_txt if keep_code_text else " "
        s = s.replace(f"\x01CODE{idx}\x02", replacement)

    return re.sub(r"[ \t]+", " ", s).strip()


def mask_inline_syntax_for_tells(line: str) -> str:
    """Mask inline code, images, and link URLs so raw-line tell checks stay clean."""
    s = _BADGE_LINK_RE.sub(" ", line)
    s = _INLINE_IMAGE_RE.sub(" ", s)
    s = _REF_IMAGE_RE.sub(" ", s)
    s = _INLINE_CODE_RE.sub(" ", s)
    s = _AUTOLINK_RE.sub(" ", s)
    for _ in range(3):
        updated = _INLINE_LINK_RE.sub(r"\1", s)
        updated = _REF_LINK_RE.sub(r"\1", updated)
        if updated == s:
            break
        s = updated
    s = _HTML_TAG_RE.sub(" ", s)
    return s


def count_words(text: str) -> int:
    """Count lexical word tokens in reader-visible text."""
    return len(_WORD_RE.findall(text))


def _find_frontmatter_end(lines: list[str]) -> int:
    """Return inclusive 0-based end line of top-of-file YAML frontmatter, or -1."""
    if not lines or not _FRONTMATTER_OPEN_RE.match(lines[0]):
        return -1
    for idx in range(1, len(lines)):
        if _FRONTMATTER_CLOSE_RE.match(lines[idx]):
            return idx
    return -1


def _identify_table_lines(lines: list[str], skipped: list[bool]) -> set[int]:
    """Identify 0-based line indices belonging to Markdown pipe tables."""
    table_indices: set[int] = set()
    n = len(lines)
    i = 0
    while i < n:
        if skipped[i]:
            i += 1
            continue
        line = lines[i]
        if (
            i + 1 < n
            and not skipped[i + 1]
            and "|" in line
            and _TABLE_DELIM_RE.match(lines[i + 1])
        ):
            table_indices.add(i)
            table_indices.add(i + 1)
            j = i + 2
            while j < n and not skipped[j] and lines[j].strip() and "|" in lines[j]:
                table_indices.add(j)
                j += 1
            i = j
            continue
        if _PIPE_ROW_RE.match(line):
            table_indices.add(i)
        i += 1
    return table_indices


def extract_markdown_structure(text: str) -> MarkdownStructure:
    """Extract paragraphs, headings, hard-wrapped lines, and masked lines."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = normalized.split("\n")
    comment_masked = _mask_html_comments(normalized).split("\n")
    n = len(comment_masked)

    skipped = [False] * n
    fm_end = _find_frontmatter_end(raw_lines)
    if fm_end >= 0:
        for idx in range(fm_end + 1):
            skipped[idx] = True

    # Mask fenced code blocks (` ``` ` and ` ~~~ `).
    fence_char = ""
    fence_len = 0
    for idx, line in enumerate(comment_masked):
        if skipped[idx]:
            continue
        if not fence_char:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                marker, rest = m.group(1), m.group(2)
                # In CommonMark, backtick fence info strings cannot contain backticks.
                if marker[0] == "`" and "`" in rest:
                    continue
                fence_char = marker[0]
                fence_len = len(marker)
                skipped[idx] = True
        else:
            skipped[idx] = True
            close_re = re.compile(
                rf"^(?:\s*>)*\s*{re.escape(fence_char)}{{{fence_len},}}\s*$"
            )
            if close_re.match(line):
                fence_char = ""
                fence_len = 0

    # Mask reference link definitions.
    for idx, line in enumerate(comment_masked):
        if not skipped[idx] and _REF_DEF_RE.match(line):
            skipped[idx] = True

    table_lines = _identify_table_lines(comment_masked, skipped)
    masked_lines = [
        "" if (skipped[i] or i in table_lines) else comment_masked[i]
        for i in range(n)
    ]

    paragraphs_with_lines: list[tuple[int, str]] = []
    prose_without_code_with_lines: list[tuple[int, str]] = []
    headings_with_lines: list[tuple[int, str]] = []
    ordinary_prose_flags = [False] * n

    buf_lines: list[str] = []
    buf_nocode_lines: list[str] = []
    buf_start_line = 0
    buf_kind = ""  # "prose", "list", "quote"

    def flush_buf() -> None:
        nonlocal buf_lines, buf_nocode_lines, buf_start_line, buf_kind
        if buf_lines:
            joined = " ".join(part for part in buf_lines if part).strip()
            joined_nocode = " ".join(part for part in buf_nocode_lines if part).strip()
            if joined:
                paragraphs_with_lines.append((buf_start_line, joined))
                prose_without_code_with_lines.append(
                    (buf_start_line, joined_nocode or " ")
                )
        buf_lines = []
        buf_nocode_lines = []
        buf_start_line = 0
        buf_kind = ""

    i = 0
    while i < n:
        lineno = i + 1
        if skipped[i] or i in table_lines:
            flush_buf()
            i += 1
            continue

        line = comment_masked[i]
        stripped = line.strip()
        if not stripped:
            flush_buf()
            i += 1
            continue

        if (
            _STANDALONE_HTML_BLOCK_RE.match(line)
            or _STANDALONE_BADGE_OR_IMAGE_RE.match(line)
            or _IMPORT_DIRECTIVE_RE.match(stripped)
        ):
            flush_buf()
            i += 1
            continue

        # ATX heading (# .. ######)
        m_atx = _ATX_HEADING_RE.match(line)
        if m_atx:
            flush_buf()
            heading_text = clean_inline_markdown(m_atx.group(2) or "")
            if heading_text:
                headings_with_lines.append((lineno, heading_text))
            i += 1
            continue

        # Setext heading (Title followed by === or ---)
        if (
            i + 1 < n
            and not skipped[i + 1]
            and (i + 1) not in table_lines
            and not _LIST_ITEM_RE.match(line)
            and not _BLOCKQUOTE_RE.match(line)
            and not _HR_RE.match(line)
            and _SETEXT_UNDERLINE_RE.match(comment_masked[i + 1])
        ):
            flush_buf()
            heading_text = clean_inline_markdown(line)
            if heading_text:
                headings_with_lines.append((lineno, heading_text))
            i += 2
            continue

        # Horizontal rule
        if _HR_RE.match(line):
            flush_buf()
            i += 1
            continue

        # Blockquote line
        m_quote = _BLOCKQUOTE_RE.match(line)
        if m_quote:
            inner = m_quote.group(1).strip()
            if not inner:
                flush_buf()
                i += 1
                continue
            m_q_atx = _ATX_HEADING_RE.match(inner)
            if m_q_atx:
                flush_buf()
                heading_text = clean_inline_markdown(m_q_atx.group(2) or "")
                if heading_text:
                    headings_with_lines.append((lineno, heading_text))
                i += 1
                continue
            cleaned = clean_inline_markdown(inner)
            if cleaned:
                if buf_kind != "quote":
                    flush_buf()
                    buf_kind = "quote"
                    buf_start_line = lineno
                buf_lines.append(cleaned)
                buf_nocode_lines.append(
                    clean_inline_markdown(inner, keep_code_text=False)
                )
            i += 1
            continue

        # List item
        m_list = _LIST_ITEM_RE.match(line)
        if m_list:
            flush_buf()
            item_body = _TASK_MARKER_RE.sub("", m_list.group(2))
            cleaned = clean_inline_markdown(item_body)
            if cleaned:
                buf_kind = "list"
                buf_start_line = lineno
                buf_lines.append(cleaned)
                buf_nocode_lines.append(
                    clean_inline_markdown(item_body, keep_code_text=False)
                )
            i += 1
            continue

        # Indented continuation of an open list item
        if buf_kind == "list" and re.match(r"^(?:\t| {2,})\S", line):
            cleaned = clean_inline_markdown(stripped)
            if cleaned:
                buf_lines.append(cleaned)
                buf_nocode_lines.append(
                    clean_inline_markdown(stripped, keep_code_text=False)
                )
            i += 1
            continue

        # Ordinary prose line
        cleaned = clean_inline_markdown(line)
        if cleaned:
            if buf_kind != "prose":
                flush_buf()
                buf_kind = "prose"
                buf_start_line = lineno
            buf_lines.append(cleaned)
            buf_nocode_lines.append(clean_inline_markdown(line, keep_code_text=False))
            if re.match(r"^ {0,3}\S", line):
                ordinary_prose_flags[i] = True
        i += 1

    flush_buf()

    hard_wrapped_set: set[int] = set()
    for idx in range(n - 1):
        if not (ordinary_prose_flags[idx] and ordinary_prose_flags[idx + 1]):
            continue
        cur_raw = comment_masked[idx].rstrip("\n")
        nxt_raw = comment_masked[idx + 1].rstrip("\n")

        # Intentional Markdown hard line breaks: two trailing spaces, trailing \, or <br>.
        if (
            cur_raw.endswith("  ")
            or cur_raw.rstrip().endswith("\\")
            or _BR_TAG_RE.search(cur_raw)
        ):
            continue

        cur_trim = cur_raw.strip()
        nxt_trim = nxt_raw.strip()
        if _KV_LINE_RE.match(cur_trim) or _KV_LINE_RE.match(nxt_trim):
            continue

        cur_vis = clean_inline_markdown(cur_trim)
        nxt_vis = clean_inline_markdown(nxt_trim)
        raw_len = len(cur_trim)
        vis_len = len(cur_vis)

        ends_terminal = bool(re.search(r"[.!?][\"'\)\]]*$", cur_trim))
        continues_flow = bool(re.match(r"^[A-Za-z0-9(\[\"'`*_]", nxt_trim))

        mid_sentence_wrap = (
            (40 <= raw_len <= 130 or 40 <= vis_len <= 105)
            and not ends_terminal
            and continues_flow
        )
        paragraph_col_wrap = (
            (50 <= raw_len <= 105 or 50 <= vis_len <= 95)
            and continues_flow
            and len(nxt_vis.split()) >= 3
        )
        if mid_sentence_wrap or paragraph_col_wrap:
            hard_wrapped_set.add(idx + 1)
            hard_wrapped_set.add(idx + 2)

    return MarkdownStructure(
        paragraphs_with_lines=paragraphs_with_lines,
        prose_without_code_with_lines=prose_without_code_with_lines,
        headings_with_lines=headings_with_lines,
        hard_wrapped_lines=sorted(hard_wrapped_set),
        masked_lines=masked_lines,
        raw_lines=raw_lines,
    )


def strip_markdown(text: str, source: str = "<stdin>") -> dict[str, Any]:
    """Strip Markdown to reader-visible body prose matching data-model.md."""
    structure = extract_markdown_structure(text)
    paragraphs = [p for _, p in structure.paragraphs_with_lines]
    headings = [h for _, h in structure.headings_with_lines]
    body_text = "\n\n".join(paragraphs)
    return {
        "source": source,
        "text": body_text,
        "paragraphs": paragraphs,
        "headings": headings,
        "hard_wrapped_lines": structure.hard_wrapped_lines,
        "word_count": count_words(body_text),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strip_markdown.py",
        description="Strip Markdown syntax to clean reader-visible body prose.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Markdown file path to strip (reads stdin if omitted or '-').",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON object matching docs/spec/data-model.md.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.file is None or args.file == "-":
        source = "<stdin>"
        content = sys.stdin.read()
    else:
        path = Path(args.file)
        if not path.is_file():
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 2
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 2
        source = args.file

    result = strip_markdown(content, source=source)
    if args.as_json:
        print(json.dumps(result, indent=2))
    elif result["text"]:
        print(result["text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
