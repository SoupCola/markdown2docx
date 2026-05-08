from __future__ import annotations

import re
from pathlib import Path

_IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
_EXPLICIT_KEY_PATTERN = re.compile(r"(?P<caption>.*?)(?:\s+@(?P<key>(?:fig|tab):[^\s]+))$")
_FIGURE_CAPTION_PREFIX_PATTERN = re.compile(r"^图\s*\d+(?:-\d+)?\s*")
_TABLE_CAPTION_PREFIX_PATTERN = re.compile(r"^表\s*\d+(?:-\d+)?\s*")
_NATURAL_FIGURE_REF_PATTERN = re.compile(r"图\s*(\d+(?:-\d+)?)")
_NATURAL_TABLE_REF_PATTERN = re.compile(r"表\s*(\d+(?:-\d+)?)")
_FOOTNOTE_DEF_PATTERN = re.compile(r"^\[\^(?P<key>[^\]]+)\]:\s*(?P<text>.+)$")
_NUMBERED_REF_DEF_PATTERN = re.compile(r"^\[(?P<key>\d+)\]\s+(?P<text>.+)$")
_ORDERED_LIST_PATTERN = re.compile(r"^\d+\.\s+(?P<text>.+)$")
_UNORDERED_LIST_PATTERN = re.compile(r"^[*-]\s+(?P<text>.+)$")
_TABLE_ROW_PATTERN = re.compile(r"^\|.*\|$")
_TABLE_SEPARATOR_PATTERN = re.compile(r"^\|?(\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?$")
_INLINE_FOOTNOTE_REF_PATTERN = re.compile(r"\[\^(?P<key>[^\]]+)\]")
_INLINE_NUMBERED_REF_PATTERN = re.compile(r"(?<!\!)\[(?P<key>\d+)\]")


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def _replace_reference_markers(text: str) -> str:
    text = _INLINE_FOOTNOTE_REF_PATTERN.sub(lambda m: f"{{ref:{m.group('key')}}}", text)
    text = _INLINE_NUMBERED_REF_PATTERN.sub(lambda m: f"{{ref:{m.group('key')}}}", text)
    return text


def _strip_caption_prefix(caption: str, item_type: str) -> str:
    pattern = _FIGURE_CAPTION_PREFIX_PATTERN if item_type == "figure" else _TABLE_CAPTION_PREFIX_PATTERN
    return pattern.sub("", caption).strip()


def _parse_image(line: str, fig_counter: int, base_path: Path) -> tuple[dict, int] | None:
    match = _IMAGE_PATTERN.fullmatch(line.strip())
    if not match:
        return None
    alt = match.group("alt").strip()
    raw_path = match.group("path").strip()
    image_path = Path(raw_path)
    if not image_path.is_absolute():
        image_path = (base_path / image_path).resolve()
    key_match = _EXPLICIT_KEY_PATTERN.match(alt)
    if key_match:
        raw_caption = key_match.group("caption").strip()
        key = key_match.group("key")
    else:
        raw_caption = alt
        fig_counter += 1
        key = f"fig:auto_{fig_counter}"
    caption = _strip_caption_prefix(raw_caption, "figure")
    # Extract user-specified figure number from raw alt text (e.g. "图4-1" → "4-1")
    explicit_num_match = _EXPLICIT_FIGURE_NUM_PATTERN.match(raw_caption)
    figure_num = explicit_num_match.group(1) if explicit_num_match else None
    return {"type": "image", "path": str(image_path), "caption": caption, "key": key, "figure_num": figure_num}, fig_counter


def _parse_formula_single(line: str, formula_counter: int) -> tuple[dict, int] | None:
    stripped = line.strip()
    if not stripped.startswith("$$"):
        return None
    # Bare "$$" is a multi-line delimiter, not a single-line formula
    if stripped == "$$":
        return None
    key = None
    payload = stripped
    comment_start = stripped.find("<!--")
    if comment_start != -1:
        payload = stripped[:comment_start].strip()
        comment = stripped[comment_start:].strip()
        match = re.match(r"^<!--\s*key:\s*(?P<key>[^\s]+)\s*-->$", comment)
        if match:
            key = match.group("key").strip()
    if not (payload.startswith("$$") and payload.endswith("$$")):
        return None
    content = payload[2:-2].strip()
    if not content:
        return None
    if key is None:
        formula_counter += 1
        key = f"formula:auto_{formula_counter}"
    return {"type": "formula", "latex": content, "key": key}, formula_counter


def _try_parse_multiline_formula(lines: list[str], idx: int, formula_counter: int) -> tuple[dict, int, int] | None:
    """Try to parse a multi-line $$...$$ formula starting at idx.

    The opening $$ must be on its own line. Returns (item, next_idx, new_counter) or None.
    """
    if lines[idx].strip() != "$$":
        return None

    # Collect lines until closing $$
    content_lines = []
    j = idx + 1
    while j < len(lines):
        if lines[j].strip() == "$$":
            break
        content_lines.append(lines[j])
        j += 1

    if j >= len(lines):
        return None  # unclosed

    next_idx = j + 1

    # Check for key in comment on the next line
    key = None
    if next_idx < len(lines):
        after = lines[next_idx].strip()
        key_match = re.match(r"^<!--\s*key:\s*(?P<key>[^\s]+)\s*-->$", after)
        if key_match:
            key = key_match.group("key").strip()
            next_idx += 1

    latex = "\n".join(content_lines).strip()
    if not latex:
        return None

    if key is None:
        formula_counter += 1
        key = f"formula:auto_{formula_counter}"

    return {"type": "formula", "latex": latex, "key": key}, next_idx, formula_counter


def _is_reference_definition(line: str) -> bool:
    return bool(_FOOTNOTE_DEF_PATTERN.match(line.strip()) or _NUMBERED_REF_DEF_PATTERN.match(line.strip()))


def _parse_reference_definition(line: str) -> dict | None:
    stripped = line.strip()
    footnote = _FOOTNOTE_DEF_PATTERN.match(stripped)
    if footnote:
        return {"key": f"ref:{footnote.group('key')}", "text": footnote.group('text').strip()}
    numbered = _NUMBERED_REF_DEF_PATTERN.match(stripped)
    if numbered:
        return {"key": f"ref:{numbered.group('key')}", "text": numbered.group('text').strip()}
    return None


def _parse_table(lines: list[str], start: int, table_counter: int) -> tuple[dict, int, int] | None:
    if start + 1 >= len(lines):
        return None
    if not _TABLE_ROW_PATTERN.match(lines[start].strip()):
        return None
    if not _TABLE_SEPARATOR_PATTERN.match(lines[start + 1].strip()):
        return None

    rows: list[list[str]] = []
    idx = start
    while idx < len(lines) and _TABLE_ROW_PATTERN.match(lines[idx].strip()):
        row = [cell.strip() for cell in lines[idx].strip().strip("|").split("|")]
        rows.append(row)
        idx += 1
    if len(rows) < 2:
        return None

    header = rows[0]
    body_rows = rows[2:] if len(rows) >= 2 else []
    table_counter += 1
    return {
        "type": "table",
        "rows": [header, *body_rows],
        "caption": "",
        "key": f"tab:auto_{table_counter}",
    }, idx, table_counter


_EXPLICIT_FIGURE_NUM_PATTERN = re.compile(r"^图\s*(\d+(?:-\d+)?)\s*")
_EXPLICIT_TABLE_NUM_PATTERN = re.compile(r"^表\s*(\d+(?:-\d+)?)\s*")


def _build_natural_xref_map(paragraphs: list[dict]) -> dict[str, str]:
    """Build a mapping from natural reference numbers to keys.

    Strategy:
    1. Extract explicit numbers from image alt text (e.g. "图4-1" → "4-1")
    2. Scan body text for unmapped "图 N" / "表 N" patterns
    3. Assign unmapped patterns to items by sequential order

    Returns: dict mapping "图 1" or "表 2-1" style strings to "{key}" placeholders.
    """
    xref_map: dict[str, str] = {}
    chapter_num = 0
    fig_in_chapter = 0
    tab_in_chapter = 0

    # Collect items with their explicit numbers (from alt text)
    fig_items: list[tuple[str, str | None]] = []  # (key, explicit_num or None)
    tab_items: list[tuple[str, str | None]] = []   # (key, explicit_num or None)

    for item in paragraphs:
        if item["type"] == "heading_1":
            chapter_num += 1
            fig_in_chapter = 0
            tab_in_chapter = 0
        elif item["type"] == "image":
            fig_in_chapter += 1
            key = item["key"]
            figure_num = item.get("figure_num")
            fig_items.append((key, figure_num))
            # Register explicit number if available
            if figure_num:
                xref_map[f"图 {figure_num}"] = f"{{{key}}}"
            # Also register chapter-based number
            xref_map[f"图 {chapter_num}-{fig_in_chapter}"] = f"{{{key}}}"
        elif item["type"] == "table":
            tab_in_chapter += 1
            key = item["key"]
            tab_items.append((key, None))  # tables have no explicit number
            xref_map[f"表 {chapter_num}-{tab_in_chapter}"] = f"{{{key}}}"

    # Scan body text for unmapped natural references
    seen_fig_refs: list[str] = []
    seen_tab_refs: list[str] = []
    for item in paragraphs:
        text = item.get("text", "")
        if not text:
            continue
        for m in _NATURAL_FIGURE_REF_PATTERN.finditer(text):
            ref = f"图 {m.group(1)}"
            if ref not in xref_map and ref not in seen_fig_refs:
                seen_fig_refs.append(ref)
        for m in _NATURAL_TABLE_REF_PATTERN.finditer(text):
            ref = f"表 {m.group(1)}"
            if ref not in xref_map and ref not in seen_tab_refs:
                seen_tab_refs.append(ref)

    # Assign unmapped figure refs to figure items without explicit numbers, by order
    unassigned_fig_items = [(k, n) for k, n in fig_items if n is None]
    for i, ref in enumerate(seen_fig_refs):
        if i < len(unassigned_fig_items):
            xref_map[ref] = f"{{{unassigned_fig_items[i][0]}}}"

    # Assign unmapped table refs to table items by order
    for i, ref in enumerate(seen_tab_refs):
        if i < len(tab_items):
            xref_map[ref] = f"{{{tab_items[i][0]}}}"

    return xref_map


def _resolve_natural_xrefs_in_text(text: str, xref_map: dict[str, str]) -> str:
    """Replace all natural xref patterns in text using the complete xref_map."""
    if not xref_map:
        return text
    # Sort by length descending to match longer patterns first (e.g. "图 1-2" before "图 1")
    for natural_ref, replacement in sorted(xref_map.items(), key=lambda x: -len(x[0])):
        # Replace "图 N " (with trailing space) or "图 N" (without)
        text = text.replace(natural_ref + " ", replacement)
        text = text.replace(natural_ref, replacement)
    return text


def _resolve_all_natural_xrefs(paragraphs: list[dict], xref_map: dict[str, str]) -> None:
    """Replace natural xrefs in all paragraph texts using the complete map."""
    for paragraph in paragraphs:
        text = paragraph.get("text")
        if not text:
            continue
        paragraph["text"] = _resolve_natural_xrefs_in_text(text, xref_map)


_HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)


def _skip_html_comments(lines: list[str], idx: int) -> int:
    """Skip HTML comments (single or multi-line) and return next index."""
    if idx >= len(lines):
        return idx

    line = lines[idx].strip()

    # Single-line comment: <!-- ... -->
    if line.startswith("<!--") and line.endswith("-->"):
        return idx + 1

    # Multi-line comment: starts with <!-- but doesn't end with -->
    if line.startswith("<!--") and "-->" not in line:
        j = idx + 1
        while j < len(lines):
            if lines[j].strip().endswith("-->"):
                return j + 1
            j += 1

    return idx


def parse_markdown_files(md_paths: list[Path]) -> tuple[list[dict], list[dict]]:
    paragraphs: list[dict] = []
    references: list[dict] = []
    fig_counter = 0
    formula_counter = 0
    table_counter = 0

    for md_path in md_paths:
        lines = md_path.read_text(encoding="utf-8").splitlines()
        idx = 0
        while idx < len(lines):
            raw_line = lines[idx]
            line = raw_line.strip()

            if not line:
                idx += 1
                continue

            # Skip HTML comments
            new_idx = _skip_html_comments(lines, idx)
            if new_idx != idx:
                idx = new_idx
                continue

            ref_def = _parse_reference_definition(raw_line)
            if ref_def is not None:
                references.append(ref_def)
                idx += 1
                continue

            table_result = _parse_table(lines, idx, table_counter)
            if table_result is not None:
                table_item, next_idx, table_counter = table_result
                paragraphs.append(table_item)
                idx = next_idx
                continue

            image_result = _parse_image(raw_line, fig_counter, md_path.parent)
            if image_result is not None:
                image_item, fig_counter = image_result
                paragraphs.append(image_item)
                idx += 1
                continue

            # Try single-line formula first
            formula_result = _parse_formula_single(raw_line, formula_counter)
            if formula_result is not None:
                formula_item, formula_counter = formula_result
                paragraphs.append(formula_item)
                idx += 1
                continue

            # Try multi-line formula ($$ on its own line)
            if line == "$$":
                ml_result = _try_parse_multiline_formula(lines, idx, formula_counter)
                if ml_result is not None:
                    formula_item, next_idx, formula_counter = ml_result
                    paragraphs.append(formula_item)
                    idx = next_idx
                    continue

            if line.startswith("### "):
                paragraphs.append({"type": "heading_3", "text": _normalize_text(line[4:])})
                idx += 1
                continue
            if line.startswith("## "):
                paragraphs.append({"type": "heading_2", "text": _normalize_text(line[3:])})
                idx += 1
                continue
            if line.startswith("# "):
                paragraphs.append({"type": "heading_1", "text": _normalize_text(line[2:])})
                idx += 1
                continue

            ordered = _ORDERED_LIST_PATTERN.match(line)
            if ordered:
                list_text = _replace_reference_markers(_normalize_text(ordered.group('text')))
                paragraphs.append({"type": "numbered_level_1", "text": list_text})
                idx += 1
                continue

            unordered = _UNORDERED_LIST_PATTERN.match(line)
            if unordered:
                list_text = _replace_reference_markers(_normalize_text(unordered.group('text')))
                paragraphs.append({"type": "body", "text": f"• {list_text}"})
                idx += 1
                continue

            body_lines = [line]
            idx += 1
            while idx < len(lines):
                next_line = lines[idx].strip()
                if not next_line:
                    break
                if (
                    next_line.startswith("# ")
                    or next_line.startswith("## ")
                    or next_line.startswith("### ")
                    or _is_reference_definition(next_line)
                    or _ORDERED_LIST_PATTERN.match(next_line)
                    or _UNORDERED_LIST_PATTERN.match(next_line)
                    or _IMAGE_PATTERN.fullmatch(next_line)
                    or (next_line.startswith("$$") and next_line.endswith("$$"))
                    or next_line == "$$"
                    or _TABLE_ROW_PATTERN.match(next_line)
                ):
                    break
                body_lines.append(next_line)
                idx += 1
            body_text = _replace_reference_markers(_normalize_text(" ".join(body_lines)))
            paragraphs.append({"type": "body", "text": body_text})

    # Phase 2: build complete natural xref map and resolve all at once
    xref_map = _build_natural_xref_map(paragraphs)
    _resolve_all_natural_xrefs(paragraphs, xref_map)

    return paragraphs, references
