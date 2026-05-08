from __future__ import annotations

from docx.shared import RGBColor

from .styles import apply_font, register_heading_style


def apply_heading_formatting(document, headings_config):
    style_map = {
        "Heading 1": headings_config.level_1,
        "Heading 2": headings_config.level_2,
        "Heading 3": headings_config.level_3,
    }
    for style_name, level_config in style_map.items():
        register_heading_style(document, style_name, level_config)

    for paragraph in document.paragraphs:
        if paragraph.style and paragraph.style.name in style_map:
            style = document.styles[paragraph.style.name]
            level_config = style_map[paragraph.style.name]
            paragraph.style = style
            paragraph.paragraph_format.alignment = style.paragraph_format.alignment
            paragraph.paragraph_format.space_before = style.paragraph_format.space_before
            paragraph.paragraph_format.space_after = style.paragraph_format.space_after
            paragraph.paragraph_format.first_line_indent = None
            for run in paragraph.runs:
                apply_font(
                    run,
                    level_config.font_cn,
                    level_config.font_en,
                    level_config.size,
                    level_config.bold,
                    False,
                )
                run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
