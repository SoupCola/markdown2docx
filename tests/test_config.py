from pathlib import Path

from docx_formatter.config import load_template, merge_overrides


THESIS_TEMPLATE = Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml")
REPORT_TEMPLATE = Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/report.yaml")


def test_package_root_contains_python_package():
    package_dir = Path("D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter")
    init_file = package_dir / "__init__.py"
    assert package_dir.is_dir()
    assert init_file.is_file()


def test_load_template_reads_thesis_defaults():
    config = load_template(THESIS_TEMPLATE)
    assert config.name == "毕业论文"
    assert config.page.size == "A4"
    assert config.body.font_cn == "宋体"
    assert config.headings.level_1.font_cn == "黑体"


def test_load_template_reads_numbering_defaults():
    config = load_template(THESIS_TEMPLATE)
    assert config.numbering.strict_mode is True
    assert config.numbering.level_1.style == "arabic_dot"
    assert config.numbering.level_2.style == "paren_cn"
    assert config.numbering.bracket.style == "bracket_arabic"


def test_merge_overrides_replaces_nested_fields_only():
    config = load_template(REPORT_TEMPLATE)
    merged = merge_overrides(
        config,
        {
            "body": {"first_line_indent": "0chars"},
            "headings": {"level_1": {"align": "left"}},
        },
    )
    assert merged.body.first_line_indent == "0chars"
    assert merged.headings.level_1.align == "left"
    assert merged.page.size == "A4"


def test_merge_overrides_updates_nested_numbering_fields_only():
    config = load_template(THESIS_TEMPLATE)
    merged = merge_overrides(
        config,
        {
            "numbering": {
                "level_1": {"align": "center"},
                "bracket": {"hanging_indent": "3chars"},
            }
        },
    )
    assert merged.numbering.level_1.align == "center"
    assert merged.numbering.bracket.hanging_indent == "3chars"
    assert merged.numbering.level_2.style == "paren_cn"
