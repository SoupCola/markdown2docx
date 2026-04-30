from __future__ import annotations

from pathlib import Path


def test_parse_markdown_headings_and_body(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "chapter1.md"
    md_path.write_text(
        "# 第一章\n\n正文第一段。\n\n## 背景\n\n补充说明。\n\n### 小节\n\n结尾。\n",
        encoding="utf-8",
    )

    paragraphs, references = parse_markdown_files([md_path])

    assert references == []
    assert paragraphs == [
        {"type": "heading_1", "text": "第一章"},
        {"type": "body", "text": "正文第一段。"},
        {"type": "heading_2", "text": "背景"},
        {"type": "body", "text": "补充说明。"},
        {"type": "heading_3", "text": "小节"},
        {"type": "body", "text": "结尾。"},
    ]


def test_parse_markdown_multiple_files_keep_order(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md1 = tmp_path / "01.md"
    md2 = tmp_path / "02.md"
    md1.write_text("# 第一章\n\n第一章内容。\n", encoding="utf-8")
    md2.write_text("# 第二章\n\n第二章内容。\n", encoding="utf-8")

    paragraphs, _ = parse_markdown_files([md1, md2])

    assert paragraphs == [
        {"type": "heading_1", "text": "第一章"},
        {"type": "body", "text": "第一章内容。"},
        {"type": "heading_1", "text": "第二章"},
        {"type": "body", "text": "第二章内容。"},
    ]


def test_parse_markdown_lists(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "lists.md"
    md_path.write_text(
        "1. 第一项\n2. 第二项\n\n- 无序项\n* 另一项\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert paragraphs == [
        {"type": "numbered_level_1", "text": "第一项"},
        {"type": "numbered_level_1", "text": "第二项"},
        {"type": "body", "text": "• 无序项"},
        {"type": "body", "text": "• 另一项"},
    ]


def test_parse_markdown_images_with_and_without_keys(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "images.md"
    md_path.write_text(
        "![系统架构 @fig:arch](images/arch.png)\n\n![流程图](images/flow.png)\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert paragraphs == [
        {"type": "image", "path": "images/arch.png", "caption": "系统架构", "key": "fig:arch"},
        {"type": "image", "path": "images/flow.png", "caption": "流程图", "key": "fig:auto_1"},
    ]


def test_parse_markdown_display_formulas(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "formula.md"
    md_path.write_text(
        "$$E=mc^2$$\n\n$$a+b$$ <!-- key: formula:add -->\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert paragraphs == [
        {"type": "formula", "latex": "E=mc^2", "key": "formula:auto_1"},
        {"type": "formula", "latex": "a+b", "key": "formula:add"},
    ]


def test_parse_markdown_footnote_references(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "refs.md"
    md_path.write_text(
        "根据研究[^smith2024]，效果显著。\n\n[^smith2024]: Smith J. Deep Learning. Nature, 2024.\n",
        encoding="utf-8",
    )

    paragraphs, references = parse_markdown_files([md_path])

    assert paragraphs == [
        {"type": "body", "text": "根据研究{ref:smith2024}，效果显著。"},
    ]
    assert references == [
        {"key": "ref:smith2024", "text": "Smith J. Deep Learning. Nature, 2024."},
    ]


def test_parse_markdown_numbered_references(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "numbered_refs.md"
    md_path.write_text(
        "根据研究[1]，效果显著。\n\n[1] Smith J. Deep Learning. Nature, 2024.\n",
        encoding="utf-8",
    )

    paragraphs, references = parse_markdown_files([md_path])

    assert paragraphs == [
        {"type": "body", "text": "根据研究{ref:1}，效果显著。"},
    ]
    assert references == [
        {"key": "ref:1", "text": "Smith J. Deep Learning. Nature, 2024."},
    ]


def test_parse_markdown_tables(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "tables.md"
    md_path.write_text(
        "| 项目 | 配置情况 | 说明 |\n"
        "| --- | --- | --- |\n"
        "| GPU | RTX 3060 | 用于推理 |\n"
        "| 操作系统 | Windows 11 | 运行环境 |\n",
        encoding="utf-8",
    )

    paragraphs, references = parse_markdown_files([md_path])

    assert references == []
    assert paragraphs == [
        {
            "type": "table",
            "rows": [
                ["项目", "配置情况", "说明"],
                ["GPU", "RTX 3060", "用于推理"],
                ["操作系统", "Windows 11", "运行环境"],
            ],
            "key": "tab:auto_1",
        }
    ]


def test_parse_markdown_recognizes_natural_figure_and_table_references(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "natural-xrefs.md"
    md_path.write_text(
        "系统总体结构如图 4-1 所示。\n\n"
        "![图4-1 系统总体设计结构图](images/overall-design.png)\n\n"
        "各层职责如表 4-1 所示。\n\n"
        "| 层次 | 组成内容 | 主要职责 |\n"
        "| --- | --- | --- |\n"
        "| 用户层 | 普通用户 | 发起处理任务 |\n",
        encoding="utf-8",
    )

    paragraphs, references = parse_markdown_files([md_path])

    assert references == []
    assert paragraphs == [
        {"type": "body", "text": "系统总体结构如{fig:auto_1}所示。"},
        {"type": "image", "path": "images/overall-design.png", "caption": "系统总体设计结构图", "key": "fig:auto_1"},
        {"type": "body", "text": "各层职责如{tab:auto_1}所示。"},
        {
            "type": "table",
            "rows": [
                ["层次", "组成内容", "主要职责"],
                ["用户层", "普通用户", "发起处理任务"],
            ],
            "key": "tab:auto_1",
        },
    ]
