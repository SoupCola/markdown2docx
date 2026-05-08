from __future__ import annotations

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from .utils import cn_size_to_pt, parse_distance

ALIGNMENT_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "distribute": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
}


def get_or_create_style(document, name: str, style_type: int):
    styles = document.styles
    if name in [style.name for style in styles]:
        return styles[name]
    return styles.add_style(name, WD_STYLE_TYPE(style_type))


def apply_font(run, font_cn: str, font_en: str, size: str, bold: bool, italic: bool):
    run.font.name = font_en
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font_cn)
    run.font.size = Pt(cn_size_to_pt(size))
    run.bold = bold
    run.italic = italic


def register_heading_style(document, name: str, level_config):
    style = get_or_create_style(document, name, WD_STYLE_TYPE.PARAGRAPH)
    style.font.name = level_config.font_en
    style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), level_config.font_cn)
    style.font.size = Pt(cn_size_to_pt(level_config.size))
    style.font.bold = level_config.bold
    style.paragraph_format.alignment = ALIGNMENT_MAP[level_config.align]

    before_unit, before_value = parse_distance(level_config.space_before)
    after_unit, after_value = parse_distance(level_config.space_after)
    if before_unit == "pt":
        style.paragraph_format.space_before = Pt(before_value)
    if after_unit == "pt":
        style.paragraph_format.space_after = Pt(after_value)
    return style
