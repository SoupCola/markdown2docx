from __future__ import annotations

from docx.enum.text import WD_LINE_SPACING
from docx.shared import Pt

from .styles import ALIGNMENT_MAP, apply_font
from .utils import cn_size_to_pt, parse_distance, parse_indent, parse_line_spacing

LINE_SPACING_RULES = {
    "multiple": WD_LINE_SPACING.MULTIPLE,
}


def apply_body_formatting(document, body_config):
    font_size = cn_size_to_pt(body_config.size)
    spacing_mode, spacing_value = parse_line_spacing(body_config.line_spacing)
    before_unit, before_value = parse_distance(body_config.space_before)
    after_unit, after_value = parse_distance(body_config.space_after)

    for paragraph in document.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        if style_name.startswith("Heading"):
            continue
        if not paragraph.text.strip():
            continue

        paragraph.paragraph_format.first_line_indent = Pt(
            parse_indent(body_config.first_line_indent, font_size)
        )
        paragraph.paragraph_format.line_spacing_rule = LINE_SPACING_RULES[spacing_mode]
        paragraph.paragraph_format.line_spacing = spacing_value
        paragraph.paragraph_format.alignment = ALIGNMENT_MAP[body_config.align]
        if before_unit == "pt":
            paragraph.paragraph_format.space_before = Pt(before_value)
        if after_unit == "pt":
            paragraph.paragraph_format.space_after = Pt(after_value)

        for run in paragraph.runs:
            apply_font(run, body_config.font_cn, body_config.font_en, body_config.size, False, False)
