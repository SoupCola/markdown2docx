from __future__ import annotations

import re
from dataclasses import dataclass, field

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .styles import ALIGNMENT_MAP, apply_font
from .utils import cn_size_to_pt, parse_indent


@dataclass
class LabelEntry:
    kind: str           # "figure" | "table" | "formula" | "reference"
    key: str            # user-specified unique ID, e.g. "fig:system_arch"
    label_text: str     # display text, e.g. "图 1-1" or "(1-1)" or "[1]"
    paragraph_index: int
    bookmark_name: str  # e.g. "_fig_system_arch"
    bookmark_id: int    # auto-incrementing


@dataclass
class LabelRegistry:
    entries: dict[str, LabelEntry] = field(default_factory=dict)
    _next_bookmark_id: int = 1

    def register(self, kind: str, key: str, label_text: str, paragraph_index: int) -> LabelEntry:
        bookmark_name = f"_{key.replace(':', '_')}"
        entry = LabelEntry(
            kind=kind,
            key=key,
            label_text=label_text,
            paragraph_index=paragraph_index,
            bookmark_name=bookmark_name,
            bookmark_id=self._next_bookmark_id,
        )
        self.entries[key] = entry
        self._next_bookmark_id += 1
        return entry

    def lookup(self, key: str) -> LabelEntry | None:
        return self.entries.get(key)


def wrap_in_bookmark(paragraph_element, run_element, entry: LabelEntry) -> None:
    """Wrap a run element in w:bookmarkStart and w:bookmarkEnd."""
    p = paragraph_element
    r = run_element
    idx = list(p).index(r)

    bm_start = OxmlElement("w:bookmarkStart")
    bm_start.set(qn("w:id"), str(entry.bookmark_id))
    bm_start.set(qn("w:name"), entry.bookmark_name)

    bm_end = OxmlElement("w:bookmarkEnd")
    bm_end.set(qn("w:id"), str(entry.bookmark_id))

    p.insert(idx, bm_start)
    p.insert(idx + 2, bm_end)


def make_ref_field(bookmark_name: str, display_text: str, superscript: bool = False) -> list:
    """Create a list of XML elements for a Word REF field code.

    Returns 5 elements: begin, instrText, separate, display text run, end.
    If superscript is True, the display text run uses superscript vertical alignment.
    """
    begin_r = OxmlElement("w:r")
    begin_char = OxmlElement("w:fldChar")
    begin_char.set(qn("w:fldCharType"), "begin")
    begin_r.append(begin_char)

    instr_r = OxmlElement("w:r")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = f" REF {bookmark_name} \\h "
    instr_r.append(instr_text)

    sep_r = OxmlElement("w:r")
    sep_char = OxmlElement("w:fldChar")
    sep_char.set(qn("w:fldCharType"), "separate")
    sep_r.append(sep_char)

    display_r = OxmlElement("w:r")
    if superscript:
        rPr = OxmlElement("w:rPr")
        vertAlign = OxmlElement("w:vertAlign")
        vertAlign.set(qn("w:val"), "superscript")
        rPr.append(vertAlign)
        display_r.append(rPr)
    display_t = OxmlElement("w:t")
    display_t.text = display_text
    display_r.append(display_t)

    end_r = OxmlElement("w:r")
    end_char = OxmlElement("w:fldChar")
    end_char.set(qn("w:fldCharType"), "end")
    end_r.append(end_char)

    return [begin_r, instr_r, sep_r, display_r, end_r]


_PLACEHOLDER_RE = re.compile(r"\{([^}]+)\}")


def parse_placeholders(text: str) -> list[tuple[str, str]]:
    """Parse text with {key} placeholders into segments.

    Returns a list of ("text", "plain text") and ("ref", "key") tuples.
    """
    segments = []
    last_end = 0
    for match in _PLACEHOLDER_RE.finditer(text):
        start, end = match.span()
        if start > last_end:
            segments.append(("text", text[last_end:start]))
        segments.append(("ref", match.group(1)))
        last_end = end
    if last_end < len(text):
        segments.append(("text", text[last_end:]))
    return segments


def _number_label(index: int, style: str) -> str:
    if style == "bracket":
        return f"[{index}]"
    if style == "paren":
        return f"({index})"
    return f"{index}."


def generate_bibliography(document, registry: LabelRegistry, references: list[dict], config) -> None:
    """Generate bibliography section at end of document with bookmarks."""
    title_p = document.add_paragraph(config.title)
    title_p.alignment = ALIGNMENT_MAP.get(config.title_align, WD_ALIGN_PARAGRAPH.LEFT)
    if title_p.runs:
        apply_font(
            title_p.runs[0],
            config.title_font_cn, config.title_font_en,
            config.title_size, config.title_bold, False,
        )

    for i, ref in enumerate(references):
        index = i + 1
        entry = registry.lookup(ref["key"])
        if entry is None:
            continue

        label_text = _number_label(index, config.number_style)
        entry.label_text = label_text

        p = document.add_paragraph()
        p.alignment = ALIGNMENT_MAP.get(config.align, WD_ALIGN_PARAGRAPH.LEFT)

        label_run = p.add_run(label_text + " ")
        entry.paragraph_index = len(document.paragraphs) - 1
        wrap_in_bookmark(p._p, label_run._r, entry)

        text_run = p.add_run(ref["text"])

        for run in p.runs:
            apply_font(run, config.font_cn, config.font_en, config.size, False, False)

        if config.hanging_indent:
            font_size = cn_size_to_pt(config.size)
            indent_pt = parse_indent(config.hanging_indent, font_size)
            p.paragraph_format.first_line_indent = Pt(-indent_pt)
            p.paragraph_format.left_indent = Pt(indent_pt)
