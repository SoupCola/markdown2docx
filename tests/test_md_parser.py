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
    (tmp_path / "images").mkdir(exist_ok=True)
    md_path.write_text(
        "![系统架构 @fig:arch](images/arch.png)\n\n![流程图](images/flow.png)\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert len(paragraphs) == 2
    assert paragraphs[0]["type"] == "image"
    assert paragraphs[0]["caption"] == "系统架构"
    assert paragraphs[0]["key"] == "fig:arch"
    assert paragraphs[1]["type"] == "image"
    assert paragraphs[1]["caption"] == "流程图"
    assert paragraphs[1]["key"] == "fig:auto_1"


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
    assert len(paragraphs) == 1
    assert paragraphs[0]["type"] == "table"
    assert paragraphs[0]["rows"] == [
        ["项目", "配置情况", "说明"],
        ["GPU", "RTX 3060", "用于推理"],
        ["操作系统", "Windows 11", "运行环境"],
    ]
    assert paragraphs[0]["key"] == "tab:auto_1"


def test_parse_markdown_recognizes_natural_figure_and_table_references(tmp_path):
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "natural-xrefs.md"
    (tmp_path / "images").mkdir(exist_ok=True)
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
    assert len(paragraphs) == 4
    # Body text before image: natural ref "图 4-1" replaced with {fig:auto_1}
    assert paragraphs[0]["type"] == "body"
    assert paragraphs[0]["text"] == "系统总体结构如{fig:auto_1}所示。"
    # Image item
    assert paragraphs[1]["type"] == "image"
    assert paragraphs[1]["key"] == "fig:auto_1"
    assert paragraphs[1]["caption"] == "系统总体设计结构图"
    assert paragraphs[1]["figure_num"] == "4-1"
    # Body text before table: natural ref "表 4-1" replaced with {tab:auto_1}
    assert paragraphs[2]["type"] == "body"
    assert paragraphs[2]["text"] == "各层职责如{tab:auto_1}所示。"
    # Table item
    assert paragraphs[3]["type"] == "table"
    assert paragraphs[3]["key"] == "tab:auto_1"


def test_parse_markdown_forward_figure_reference(tmp_path):
    """Natural figure reference BEFORE the image definition should resolve."""
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "forward-fig.md"
    (tmp_path / "images").mkdir(exist_ok=True)
    md_path.write_text(
        "如图 1-1 所示的架构。\n\n"
        "![图1-1 系统架构](images/arch.png)\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert paragraphs[0]["type"] == "body"
    assert "{fig:auto_1}" in paragraphs[0]["text"]
    assert "图 1-1" not in paragraphs[0]["text"]


def test_parse_markdown_multiple_figures_with_natural_refs(tmp_path):
    """Multiple figures with chapter-based natural references should each resolve correctly."""
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "multi-fig.md"
    (tmp_path / "images").mkdir(exist_ok=True)
    md_path.write_text(
        "# 第一章\n\n"
        "如图 1-1 所示。\n\n"
        "![图1-1 架构图](images/arch.png)\n\n"
        "如图 1-2 所示。\n\n"
        "![图1-2 流程图](images/flow.png)\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    body1 = paragraphs[1]
    body2 = paragraphs[3]
    # Natural refs resolved to {key} placeholders
    assert "{fig:auto_1}" in body1["text"]
    assert "{fig:auto_2}" in body2["text"]


def test_parse_markdown_multiline_formula_with_key(tmp_path):
    """Multi-line $$...$$ formula with key comment should be parsed correctly."""
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "multiline-formula.md"
    md_path.write_text(
        "$$\n"
        "E = mc^2\n"
        "$$\n"
        "<!-- key: formula:einstein -->\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    assert len(paragraphs) == 1
    assert paragraphs[0]["type"] == "formula"
    assert paragraphs[0]["latex"] == "E = mc^2"
    assert paragraphs[0]["key"] == "formula:einstein"


def test_parse_markdown_mixed_forward_and_backward_refs(tmp_path):
    """Both forward (before definition) and backward (after definition) refs should work."""
    from docx_formatter.md_parser import parse_markdown_files

    md_path = tmp_path / "mixed-refs.md"
    (tmp_path / "images").mkdir(exist_ok=True)
    md_path.write_text(
        "前向引用图 2-1。\n\n"
        "![图2-1 架构图](images/arch.png)\n\n"
        "后向引用图 2-1。\n",
        encoding="utf-8",
    )

    paragraphs, _ = parse_markdown_files([md_path])

    # Both body paragraphs should have the reference resolved
    assert "{fig:auto_1}" in paragraphs[0]["text"]
    assert "{fig:auto_1}" in paragraphs[2]["text"]
