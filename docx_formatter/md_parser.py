from __future__ import annotations

import re
from pathlib import Path

_IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
_EXPLICIT_KEY_PATTERN = re.compile(r"(?P<caption>.*?)(?:\s+@(?P<key>(?:fig|tab):[^\s]+))$")
_FIGURE_CAPTION_PREFIX_PATTERN = re.compile(r"^图\s*\d+(?:-\d+)?\s*")
_TABLE_CAPTION_PREFIX_PATTERN = re.compile(r"^表\s*\d+(?:-\d+)?\s*")
_NATURAL_FIGURE_REF_PATTERN = re.compile(r"图\s*\d+(?:-\d+)?\s*")
_NATURAL_TABLE_REF_PATTERN = re.compile(r"表\s*\d+(?:-\d+)?\s*")
_FORMULA_COMMENT_KEY_PATTERN = re.compile(r"^(?P<latex>.*?)\s*<!--\s*key:\s*(?P<key>[^\s]+)\s*-->\s*$")
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


def _replace_natural_xrefs(text: str, last_figure_key: str | None, last_table_key: str | None) -> str:
    if last_figure_key is not None:
        text = _NATURAL_FIGURE_REF_PATTERN.sub(f"{{{last_figure_key}}}", text)
    if last_table_key is not None:
        text = _NATURAL_TABLE_REF_PATTERN.sub(f"{{{last_table_key}}}", text)
    return text


def _resolve_pending_xrefs(paragraphs: list[dict], last_figure_key: str | None, last_table_key: str | None) -> None:
    if last_figure_key is None and last_table_key is None:
        return
    for paragraph in paragraphs:
        text = paragraph.get("text")
        if not text:
            continue
        paragraph["text"] = _replace_natural_xrefs(text, last_figure_key, last_table_key)


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
    return {"type": "image", "path": str(image_path), "caption": caption, "key": key}, fig_counter


def _parse_formula(line: str, formula_counter: int) -> tuple[dict, int] | None:
    stripped = line.strip()
    if not stripped.startswith("$$"):
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
    if key is None:
        formula_counter += 1
        key = f"formula:auto_{formula_counter}"
    return {"type": "formula", "latex": content, "key": key}, formula_counter


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


def parse_markdown_files(md_paths: list[Path]) -> tuple[list[dict], list[dict]]:
    paragraphs: list[dict] = []
    references: list[dict] = []
    fig_counter = 0
    formula_counter = 0
    table_counter = 0
    last_figure_key: str | None = None
    last_table_key: str | None = None

    for md_path in md_paths:
        lines = md_path.read_text(encoding="utf-8").splitlines()
        idx = 0
        while idx < len(lines):
            raw_line = lines[idx]
            line = raw_line.strip()

            if not line:
                idx += 1
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
                last_table_key = table_item["key"]
                _resolve_pending_xrefs(paragraphs, last_figure_key, last_table_key)
                idx = next_idx
                continue

            image_result = _parse_image(raw_line, fig_counter, md_path.parent)
            if image_result is not None:
                image_item, fig_counter = image_result
                paragraphs.append(image_item)
                last_figure_key = image_item["key"]
                _resolve_pending_xrefs(paragraphs, last_figure_key, last_table_key)
                idx += 1
                continue

            formula_result = _parse_formula(raw_line, formula_counter)
            if formula_result is not None:
                formula_item, formula_counter = formula_result
                paragraphs.append(formula_item)
                idx += 1
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
                list_text = _replace_natural_xrefs(list_text, last_figure_key, last_table_key)
                paragraphs.append({"type": "numbered_level_1", "text": list_text})
                idx += 1
                continue

            unordered = _UNORDERED_LIST_PATTERN.match(line)
            if unordered:
                list_text = _replace_reference_markers(_normalize_text(unordered.group('text')))
                list_text = _replace_natural_xrefs(list_text, last_figure_key, last_table_key)
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
                    or _TABLE_ROW_PATTERN.match(next_line)
                ):
                    break
                body_lines.append(next_line)
                idx += 1
            body_text = _replace_reference_markers(_normalize_text(" ".join(body_lines)))
            body_text = _replace_natural_xrefs(body_text, last_figure_key, last_table_key)
            paragraphs.append({"type": "body", "text": body_text})

    return paragraphs, references
