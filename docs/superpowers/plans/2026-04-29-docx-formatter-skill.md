# DOCX Formatter Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill that can analyze, create, and accurately format DOCX documents for both academic and office-document scenarios using python-docx and YAML-backed style templates.

**Architecture:** The implementation centers on a small Python package, `docx_formatter`, with focused modules for config parsing, unit conversion, document analysis, page setup, heading/body formatting, and figure/table caption handling. The skill entrypoint will guide Claude through a confirm-before-write workflow: inspect document or requested new document settings, resolve a template plus optional overrides, summarize the final formatting plan, then execute formatting and save to a new output file.

**Tech Stack:** Python 3, python-docx, PyYAML, pytest

---

## File Structure

### New files
- `D:/2026project/docx_skill/skill.md` — skill instructions, trigger phrases, user interaction flow, and safe-output rules.
- `D:/2026project/docx_skill/requirements.txt` — runtime dependencies for the skill.
- `D:/2026project/docx_skill/docx_formatter/__init__.py` — public package exports.
- `D:/2026project/docx_skill/docx_formatter/config.py` — dataclasses and YAML loading/parsing helpers for templates and runtime overrides.
- `D:/2026project/docx_skill/docx_formatter/utils.py` — Chinese font-size conversion, unit parsing, indent conversion, naming helpers.
- `D:/2026project/docx_skill/docx_formatter/styles.py` — shared font/style registration helpers.
- `D:/2026project/docx_skill/docx_formatter/analyzer.py` — document structure inspection for existing DOCX files.
- `D:/2026project/docx_skill/docx_formatter/pages.py` — page size, margins, header/footer, and page number helpers.
- `D:/2026project/docx_skill/docx_formatter/headings.py` — heading style registration and application.
- `D:/2026project/docx_skill/docx_formatter/paragraphs.py` — body paragraph detection and formatting.
- `D:/2026project/docx_skill/docx_formatter/figures.py` — caption detection/reformatting and three-line-table helpers.
- `D:/2026project/docx_skill/docx_formatter/pipeline.py` — top-level workflow for analyze/create/format/save operations.
- `D:/2026project/docx_skill/templates/thesis.yaml` — academic thesis preset.
- `D:/2026project/docx_skill/templates/academic_paper.yaml` — academic paper preset.
- `D:/2026project/docx_skill/templates/report.yaml` — office report preset.
- `D:/2026project/docx_skill/tests/test_utils.py` — tests for unit conversion helpers.
- `D:/2026project/docx_skill/tests/test_config.py` — tests for YAML config loading and override merging.
- `D:/2026project/docx_skill/tests/test_analyzer.py` — tests for existing-document structure analysis.
- `D:/2026project/docx_skill/tests/test_styles.py` — tests for style registration.
- `D:/2026project/docx_skill/tests/test_pages.py` — tests for page setup and page numbering XML.
- `D:/2026project/docx_skill/tests/test_headings.py` — tests for heading style application.
- `D:/2026project/docx_skill/tests/test_paragraphs.py` — tests for body paragraph formatting.
- `D:/2026project/docx_skill/tests/test_figures.py` — tests for caption formatting and table borders.
- `D:/2026project/docx_skill/tests/test_pipeline.py` — end-to-end tests for formatting existing docs and creating new docs.

### Notes on boundaries
- Keep raw XML manipulation only in `pages.py` and `figures.py` so low-level WordprocessingML stays isolated.
- Keep YAML/data normalization in `config.py` so feature modules receive typed configuration instead of parsing strings repeatedly.
- Keep document orchestration in `pipeline.py`; feature modules should not load files or decide output paths.

## Task 1: Set up package skeleton and dependency manifest

**Files:**
- Create: `D:/2026project/docx_skill/requirements.txt`
- Create: `D:/2026project/docx_skill/docx_formatter/__init__.py`
- Test: `D:/2026project/docx_skill/tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_package_root_contains_python_package():
    package_dir = Path("D:/2026project/docx_skill/docx_formatter")
    init_file = package_dir / "__init__.py"
    assert package_dir.is_dir()
    assert init_file.is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_config.py::test_package_root_contains_python_package -v`
Expected: FAIL with `file or directory not found` or `assert False` because the package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/requirements.txt`
```text
python-docx>=0.8.11
PyYAML>=6.0
pytest>=8.0
```

`D:/2026project/docx_skill/docx_formatter/__init__.py`
```python
from .pipeline import create_document, format_document, summarize_analysis

__all__ = ["create_document", "format_document", "summarize_analysis"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_config.py::test_package_root_contains_python_package -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/requirements.txt D:/2026project/docx_skill/docx_formatter/__init__.py D:/2026project/docx_skill/tests/test_config.py
git commit -m "chore: initialize docx formatter package"
```

## Task 2: Implement config models and YAML loading

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/config.py`
- Create: `D:/2026project/docx_skill/templates/thesis.yaml`
- Create: `D:/2026project/docx_skill/templates/academic_paper.yaml`
- Create: `D:/2026project/docx_skill/templates/report.yaml`
- Test: `D:/2026project/docx_skill/tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from docx_formatter.config import load_template, merge_overrides


def test_load_template_reads_thesis_defaults():
    config = load_template(Path("D:/2026project/docx_skill/templates/thesis.yaml"))
    assert config.name == "毕业论文"
    assert config.page.size == "A4"
    assert config.body.font_cn == "宋体"
    assert config.headings.level_1.font_cn == "黑体"


def test_merge_overrides_replaces_nested_fields_only():
    config = load_template(Path("D:/2026project/docx_skill/templates/report.yaml"))
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.config'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/config.py`
```python
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class HeadingLevelConfig:
    font_cn: str
    font_en: str
    size: str
    bold: bool
    align: str
    space_before: str
    space_after: str


@dataclass
class HeadingsConfig:
    level_1: HeadingLevelConfig
    level_2: HeadingLevelConfig
    level_3: HeadingLevelConfig


@dataclass
class BodyConfig:
    font_cn: str
    font_en: str
    size: str
    first_line_indent: str
    line_spacing: str
    line_spacing_rule: str
    align: str
    space_before: str
    space_after: str


@dataclass
class HeaderConfig:
    content: str
    font_cn: str
    font_en: str
    size: str


@dataclass
class FooterConfig:
    content: str


@dataclass
class PageNumberConfig:
    position: str
    format: str
    start: int


@dataclass
class PageMarginsConfig:
    top: str
    bottom: str
    left: str
    right: str


@dataclass
class PageConfig:
    size: str
    margins: PageMarginsConfig
    header: HeaderConfig
    footer: FooterConfig
    page_number: PageNumberConfig


@dataclass
class FiguresConfig:
    caption_font_cn: str
    caption_font_en: str
    caption_size: str
    caption_bold: bool
    figure_caption_position: str
    table_caption_position: str
    numbering: str
    table_style: str


@dataclass
class FormatterConfig:
    name: str
    description: str
    page: PageConfig
    headings: HeadingsConfig
    body: BodyConfig
    figures: FiguresConfig


def _heading(data: dict[str, Any]) -> HeadingLevelConfig:
    return HeadingLevelConfig(**data)


def _from_dict(data: dict[str, Any]) -> FormatterConfig:
    return FormatterConfig(
        name=data["name"],
        description=data["description"],
        page=PageConfig(
            size=data["page"]["size"],
            margins=PageMarginsConfig(**data["page"]["margins"]),
            header=HeaderConfig(**data["page"]["header"]),
            footer=FooterConfig(**data["page"]["footer"]),
            page_number=PageNumberConfig(**data["page"]["page_number"]),
        ),
        headings=HeadingsConfig(
            level_1=_heading(data["headings"]["level_1"]),
            level_2=_heading(data["headings"]["level_2"]),
            level_3=_heading(data["headings"]["level_3"]),
        ),
        body=BodyConfig(**data["body"]),
        figures=FiguresConfig(**data["figures"]),
    )


def load_template(path: Path) -> FormatterConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _from_dict(raw)


def merge_overrides(config: FormatterConfig, overrides: dict[str, Any]) -> FormatterConfig:
    base = deepcopy(config.__dict__)
    base["page"] = deepcopy(config.page.__dict__)
    base["page"]["margins"] = deepcopy(config.page.margins.__dict__)
    base["page"]["header"] = deepcopy(config.page.header.__dict__)
    base["page"]["footer"] = deepcopy(config.page.footer.__dict__)
    base["page"]["page_number"] = deepcopy(config.page.page_number.__dict__)
    base["headings"] = {
        "level_1": deepcopy(config.headings.level_1.__dict__),
        "level_2": deepcopy(config.headings.level_2.__dict__),
        "level_3": deepcopy(config.headings.level_3.__dict__),
    }
    base["body"] = deepcopy(config.body.__dict__)
    base["figures"] = deepcopy(config.figures.__dict__)

    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            for nested_key, nested_value in value.items():
                if isinstance(nested_value, dict) and isinstance(base[key].get(nested_key), dict):
                    base[key][nested_key].update(nested_value)
                else:
                    base[key][nested_key] = nested_value
        else:
            base[key] = value

    return _from_dict(base)
```

`D:/2026project/docx_skill/templates/thesis.yaml`
```yaml
name: "毕业论文"
description: "中国高校毕业论文通用模板"
page:
  size: A4
  margins:
    top: 2.54cm
    bottom: 2.54cm
    left: 3.17cm
    right: 3.17cm
  header:
    content: "毕业论文"
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小五"
  footer:
    content: ""
  page_number:
    position: bottom_center
    format: arabic
    start: 1
headings:
  level_1:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "三号"
    bold: true
    align: center
    space_before: 24pt
    space_after: 18pt
  level_2:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "小三"
    bold: true
    align: left
    space_before: 13pt
    space_after: 13pt
  level_3:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "四号"
    bold: true
    align: left
    space_before: 13pt
    space_after: 13pt
body:
  font_cn: "宋体"
  font_en: "Times New Roman"
  size: "小四"
  first_line_indent: 2chars
  line_spacing: 1.5lines
  line_spacing_rule: multiple
  align: justify
  space_before: 0pt
  space_after: 0pt
figures:
  caption_font_cn: "宋体"
  caption_font_en: "Times New Roman"
  caption_size: "五号"
  caption_bold: false
  figure_caption_position: below
  table_caption_position: above
  numbering: chapter
  table_style: three_line
```

`D:/2026project/docx_skill/templates/academic_paper.yaml`
```yaml
name: "学术论文"
description: "中文学术论文模板"
page:
  size: A4
  margins:
    top: 2.54cm
    bottom: 2.54cm
    left: 2.54cm
    right: 2.54cm
  header:
    content: "学术论文"
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小五"
  footer:
    content: ""
  page_number:
    position: bottom_center
    format: arabic
    start: 1
headings:
  level_1:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "四号"
    bold: true
    align: center
    space_before: 18pt
    space_after: 12pt
  level_2:
    font_cn: "黑体"
    font_en: "Times New Roman"
    size: "小四"
    bold: true
    align: left
    space_before: 12pt
    space_after: 6pt
  level_3:
    font_cn: "楷体"
    font_en: "Times New Roman"
    size: "小四"
    bold: true
    align: left
    space_before: 6pt
    space_after: 6pt
body:
  font_cn: "宋体"
  font_en: "Times New Roman"
  size: "小四"
  first_line_indent: 2chars
  line_spacing: 1.5lines
  line_spacing_rule: multiple
  align: justify
  space_before: 0pt
  space_after: 0pt
figures:
  caption_font_cn: "宋体"
  caption_font_en: "Times New Roman"
  caption_size: "五号"
  caption_bold: false
  figure_caption_position: below
  table_caption_position: above
  numbering: continuous
  table_style: three_line
```

`D:/2026project/docx_skill/templates/report.yaml`
```yaml
name: "企业报告"
description: "通用办公报告模板"
page:
  size: A4
  margins:
    top: 2.54cm
    bottom: 2.54cm
    left: 2.54cm
    right: 2.54cm
  header:
    content: ""
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小五"
  footer:
    content: ""
  page_number:
    position: bottom_center
    format: arabic
    start: 1
headings:
  level_1:
    font_cn: "黑体"
    font_en: "Arial"
    size: "三号"
    bold: true
    align: left
    space_before: 18pt
    space_after: 12pt
  level_2:
    font_cn: "黑体"
    font_en: "Arial"
    size: "四号"
    bold: true
    align: left
    space_before: 12pt
    space_after: 6pt
  level_3:
    font_cn: "宋体"
    font_en: "Arial"
    size: "小四"
    bold: true
    align: left
    space_before: 6pt
    space_after: 6pt
body:
  font_cn: "宋体"
  font_en: "Arial"
  size: "小四"
  first_line_indent: 2chars
  line_spacing: 1.5lines
  line_spacing_rule: multiple
  align: justify
  space_before: 0pt
  space_after: 6pt
figures:
  caption_font_cn: "宋体"
  caption_font_en: "Arial"
  caption_size: "五号"
  caption_bold: false
  figure_caption_position: below
  table_caption_position: above
  numbering: continuous
  table_style: three_line
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/config.py D:/2026project/docx_skill/templates/thesis.yaml D:/2026project/docx_skill/templates/academic_paper.yaml D:/2026project/docx_skill/templates/report.yaml D:/2026project/docx_skill/tests/test_config.py
git commit -m "feat: add docx formatter config templates"
```

## Task 3: Implement unit conversion helpers

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/utils.py`
- Test: `D:/2026project/docx_skill/tests/test_utils.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest

from docx_formatter.utils import chars_to_pt, cn_size_to_pt, parse_distance, parse_line_spacing


@pytest.mark.parametrize(
    ("name", "expected"),
    [("三号", 16.0), ("小四", 12.0), ("五号", 10.5)],
)
def test_cn_size_to_pt_returns_point_values(name, expected):
    assert cn_size_to_pt(name) == expected


def test_chars_to_pt_uses_font_size_multiplier():
    assert chars_to_pt("2chars", 12.0) == 24.0


@pytest.mark.parametrize(
    ("value", "expected"),
    [("2.54cm", 2.54), ("24pt", 24.0), ("1in", 1.0)],
)
def test_parse_distance_preserves_unit_value_for_constructor_input(value, expected):
    unit, number = parse_distance(value)
    assert unit in {"cm", "pt", "in"}
    assert number == expected


def test_parse_line_spacing_multiple_lines():
    mode, value = parse_line_spacing("1.5lines")
    assert mode == "multiple"
    assert value == 1.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_utils.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.utils'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/utils.py`
```python
from __future__ import annotations

SIZE_MAP = {
    "初号": 42.0,
    "小初": 36.0,
    "一号": 26.0,
    "小一": 24.0,
    "二号": 22.0,
    "小二": 18.0,
    "三号": 16.0,
    "小三": 15.0,
    "四号": 14.0,
    "小四": 12.0,
    "五号": 10.5,
    "小五": 9.0,
    "六号": 7.5,
    "小六": 6.5,
    "七号": 5.5,
}


def cn_size_to_pt(name: str) -> float:
    if name.endswith("pt"):
        return float(name[:-2])
    return SIZE_MAP[name]


def chars_to_pt(value: str, font_size_pt: float) -> float:
    if not value.endswith("chars"):
        raise ValueError(f"Unsupported chars value: {value}")
    return float(value[:-5]) * font_size_pt


def parse_distance(value: str) -> tuple[str, float]:
    for unit in ("cm", "pt", "in"):
        if value.endswith(unit):
            return unit, float(value[:-len(unit)])
    raise ValueError(f"Unsupported distance value: {value}")


def parse_line_spacing(value: str) -> tuple[str, float]:
    if value.endswith("lines"):
        return "multiple", float(value[:-5])
    if value.endswith("pt"):
        return "exactly", float(value[:-2])
    raise ValueError(f"Unsupported line spacing value: {value}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_utils.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/utils.py D:/2026project/docx_skill/tests/test_utils.py
git commit -m "feat: add formatting unit conversion helpers"
```

## Task 4: Implement shared style helpers

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/styles.py`
- Test: `D:/2026project/docx_skill/tests/test_styles.py`

- [ ] **Step 1: Write the failing test**

```python
from docx import Document

from docx_formatter.config import load_template
from docx_formatter.styles import apply_font, get_or_create_style, register_heading_style


def test_get_or_create_style_returns_same_style_instance(tmp_path):
    document = Document()
    style_a = get_or_create_style(document, "CustomHeading", 1)
    style_b = get_or_create_style(document, "CustomHeading", 1)
    assert style_a.style_id == style_b.style_id


def test_apply_font_sets_run_font_fields(tmp_path):
    document = Document()
    run = document.add_paragraph().add_run("示例")
    apply_font(run, "宋体", "Times New Roman", "小四", True, False)
    assert run.font.name == "Times New Roman"
    assert run.bold is True


def test_register_heading_style_sets_alignment_and_spacing():
    document = Document()
    config = load_template(tmp_path / "thesis.yaml")
    style = register_heading_style(document, "Heading 1", config.headings.level_1)
    assert style.paragraph_format.space_before.pt == 24.0
    assert style.paragraph_format.space_after.pt == 18.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_styles.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.styles'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/styles.py`
```python
from __future__ import annotations

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from .utils import cn_size_to_pt, parse_distance

ALIGNMENT_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def get_or_create_style(document, name: str, style_type: int):
    styles = document.styles
    if name in [style.name for style in styles]:
        return styles[name]
    return styles.add_style(name, WD_STYLE_TYPE(style_type))


def apply_font(run, font_cn: str, font_en: str, size: str, bold: bool, italic: bool):
    run.font.name = font_en
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_cn)
    run.font.size = Pt(cn_size_to_pt(size))
    run.bold = bold
    run.italic = italic


def register_heading_style(document, name: str, level_config):
    style = get_or_create_style(document, name, WD_STYLE_TYPE.PARAGRAPH)
    sample_run = document.add_paragraph().add_run()
    apply_font(sample_run, level_config.font_cn, level_config.font_en, level_config.size, level_config.bold, False)
    style.font.name = sample_run.font.name
    style._element.rPr.rFonts.set(qn("w:eastAsia"), level_config.font_cn)
    style.font.size = sample_run.font.size
    style.font.bold = level_config.bold
    style.paragraph_format.alignment = ALIGNMENT_MAP[level_config.align]
    before_unit, before_value = parse_distance(level_config.space_before)
    after_unit, after_value = parse_distance(level_config.space_after)
    if before_unit == "pt":
        style.paragraph_format.space_before = Pt(before_value)
    if after_unit == "pt":
        style.paragraph_format.space_after = Pt(after_value)
    return style
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_styles.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/styles.py D:/2026project/docx_skill/tests/test_styles.py
git commit -m "feat: add shared docx style helpers"
```

## Task 5: Implement document analyzer for existing docs

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/analyzer.py`
- Test: `D:/2026project/docx_skill/tests/test_analyzer.py`

- [ ] **Step 1: Write the failing test**

```python
from docx import Document

from docx_formatter.analyzer import analyze, summarize_analysis


def test_analyze_reports_headings_paragraphs_tables_and_sections(tmp_path):
    source = tmp_path / "sample.docx"
    document = Document()
    document.add_heading("第一章 绪论", level=1)
    document.add_paragraph("这是正文")
    document.add_table(rows=2, cols=2)
    document.save(source)

    result = analyze(source)

    assert result["total_paragraphs"] == 2
    assert result["headings_count"]["level_1"] == 1
    assert len(result["tables"]) == 1
    assert result["sections"][0]["page_size"]


def test_summarize_analysis_returns_user_readable_text(tmp_path):
    source = tmp_path / "sample.docx"
    document = Document()
    document.add_heading("标题", level=1)
    document.add_paragraph("正文")
    document.save(source)

    summary = summarize_analysis(analyze(source))
    assert "段落数" in summary
    assert "一级标题" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_analyzer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.analyzer'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/analyzer.py`
```python
from __future__ import annotations

from pathlib import Path

from docx import Document


def analyze(filepath: Path) -> dict:
    document = Document(filepath)
    heading_counts = {"level_1": 0, "level_2": 0, "level_3": 0}
    paragraphs = []
    for index, paragraph in enumerate(document.paragraphs):
        style_name = paragraph.style.name if paragraph.style else ""
        if style_name == "Heading 1":
            heading_counts["level_1"] += 1
        if style_name == "Heading 2":
            heading_counts["level_2"] += 1
        if style_name == "Heading 3":
            heading_counts["level_3"] += 1
        paragraphs.append(
            {
                "index": index,
                "text": paragraph.text,
                "style": style_name,
                "font": paragraph.runs[0].font.name if paragraph.runs else None,
            }
        )

    sections = []
    for section in document.sections:
        sections.append(
            {
                "page_size": f"{section.page_width}x{section.page_height}",
                "margins": {
                    "top": section.top_margin.cm,
                    "bottom": section.bottom_margin.cm,
                    "left": section.left_margin.cm,
                    "right": section.right_margin.cm,
                },
            }
        )

    return {
        "paragraphs": paragraphs,
        "tables": [
            {"index": index, "rows": len(table.rows), "cols": len(table.columns), "has_caption": False}
            for index, table in enumerate(document.tables)
        ],
        "images": [],
        "sections": sections,
        "total_paragraphs": len(document.paragraphs),
        "headings_count": heading_counts,
    }


def summarize_analysis(result: dict) -> str:
    return (
        f"段落数: {result['total_paragraphs']}\n"
        f"一级标题: {result['headings_count']['level_1']}\n"
        f"二级标题: {result['headings_count']['level_2']}\n"
        f"三级标题: {result['headings_count']['level_3']}\n"
        f"表格数: {len(result['tables'])}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/analyzer.py D:/2026project/docx_skill/tests/test_analyzer.py
git commit -m "feat: add docx document analyzer"
```

## Task 6: Implement page setup and page numbering helpers

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/pages.py`
- Test: `D:/2026project/docx_skill/tests/test_pages.py`

- [ ] **Step 1: Write the failing test**

```python
from docx import Document

from docx_formatter.config import load_template
from docx_formatter.pages import apply_page_settings


def test_apply_page_settings_updates_margins_header_footer_and_page_number(tmp_path):
    source_template = Path("D:/2026project/docx_skill/templates/thesis.yaml")
    config = load_template(source_template)
    document = Document()

    apply_page_settings(document, config.page)

    section = document.sections[0]
    assert round(section.top_margin.cm, 2) == 2.54
    assert round(section.left_margin.cm, 2) == 3.17
    assert section.header.paragraphs[0].text == "毕业论文"
    footer_xml = section.footer._element.xml
    assert "PAGE" in footer_xml
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_pages.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.pages'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/pages.py`
```python
from __future__ import annotations

from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

from .styles import apply_font
from .utils import cn_size_to_pt, parse_distance

PAGE_NUMBER_ALIGNMENT = {
    "bottom_center": WD_ALIGN_PARAGRAPH.CENTER,
    "top_center": WD_ALIGN_PARAGRAPH.CENTER,
    "top_right": WD_ALIGN_PARAGRAPH.RIGHT,
}


def _apply_measure(value: str):
    unit, number = parse_distance(value)
    if unit == "cm":
        return Cm(number)
    if unit == "in":
        return Inches(number)
    return Pt(number)


def _add_page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instruction)
    run._r.append(end)


def apply_page_settings(document, page_config):
    section = document.sections[0]
    section.top_margin = _apply_measure(page_config.margins.top)
    section.bottom_margin = _apply_measure(page_config.margins.bottom)
    section.left_margin = _apply_measure(page_config.margins.left)
    section.right_margin = _apply_measure(page_config.margins.right)

    header = section.header.paragraphs[0]
    header.text = page_config.header.content
    if header.runs:
        apply_font(
            header.runs[0],
            page_config.header.font_cn,
            page_config.header.font_en,
            page_config.header.size,
            False,
            False,
        )

    footer = section.footer.paragraphs[0]
    footer.text = page_config.footer.content
    footer.alignment = PAGE_NUMBER_ALIGNMENT[page_config.page_number.position]
    _add_page_number(footer)
    sect_pr = section._sectPr
    pg_num_type = OxmlElement("w:pgNumType")
    pg_num_type.set(qn("w:start"), str(page_config.page_number.start))
    sect_pr.append(pg_num_type)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_pages.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/pages.py D:/2026project/docx_skill/tests/test_pages.py
git commit -m "feat: add page setup and page numbering helpers"
```

## Task 7: Implement heading formatting

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/headings.py`
- Test: `D:/2026project/docx_skill/tests/test_headings.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from docx import Document

from docx_formatter.config import load_template
from docx_formatter.headings import apply_heading_formatting


def test_apply_heading_formatting_updates_heading_paragraphs():
    document = Document()
    heading = document.add_heading("第一章 绪论", level=1)
    config = load_template(Path("D:/2026project/docx_skill/templates/thesis.yaml"))

    apply_heading_formatting(document, config.headings)

    assert heading.style.name == "Heading 1"
    assert heading.paragraph_format.alignment is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_headings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.headings'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/headings.py`
```python
from __future__ import annotations

from .styles import register_heading_style


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
            paragraph.style = style
            paragraph.paragraph_format.alignment = style.paragraph_format.alignment
            paragraph.paragraph_format.space_before = style.paragraph_format.space_before
            paragraph.paragraph_format.space_after = style.paragraph_format.space_after
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_headings.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/headings.py D:/2026project/docx_skill/tests/test_headings.py
git commit -m "feat: add heading formatting support"
```

## Task 8: Implement body paragraph formatting

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/paragraphs.py`
- Test: `D:/2026project/docx_skill/tests/test_paragraphs.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from docx import Document

from docx_formatter.config import load_template
from docx_formatter.paragraphs import apply_body_formatting


def test_apply_body_formatting_updates_normal_paragraphs():
    document = Document()
    paragraph = document.add_paragraph("正文内容")
    config = load_template(Path("D:/2026project/docx_skill/templates/thesis.yaml"))

    apply_body_formatting(document, config.body)

    assert round(paragraph.paragraph_format.first_line_indent.pt, 1) == 24.0
    assert paragraph.paragraph_format.alignment is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_paragraphs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.paragraphs'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/paragraphs.py`
```python
from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Pt

from .styles import apply_font
from .utils import chars_to_pt, cn_size_to_pt, parse_distance, parse_line_spacing

ALIGNMENT_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
}

LINE_SPACING_RULES = {
    "multiple": WD_LINE_SPACING.MULTIPLE,
    "exactly": WD_LINE_SPACING.EXACTLY,
    "at_least": WD_LINE_SPACING.AT_LEAST,
}


def apply_body_formatting(document, body_config):
    font_size = cn_size_to_pt(body_config.size)
    for paragraph in document.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        if style_name.startswith("Heading"):
            continue
        if not paragraph.text.strip():
            continue
        paragraph.paragraph_format.first_line_indent = Pt(
            chars_to_pt(body_config.first_line_indent, font_size)
        )
        spacing_mode, spacing_value = parse_line_spacing(body_config.line_spacing)
        paragraph.paragraph_format.line_spacing_rule = LINE_SPACING_RULES[spacing_mode]
        paragraph.paragraph_format.line_spacing = spacing_value
        paragraph.paragraph_format.alignment = ALIGNMENT_MAP[body_config.align]
        before_unit, before_value = parse_distance(body_config.space_before)
        after_unit, after_value = parse_distance(body_config.space_after)
        if before_unit == "pt":
            paragraph.paragraph_format.space_before = Pt(before_value)
        if after_unit == "pt":
            paragraph.paragraph_format.space_after = Pt(after_value)
        for run in paragraph.runs:
            apply_font(run, body_config.font_cn, body_config.font_en, body_config.size, False, False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_paragraphs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/paragraphs.py D:/2026project/docx_skill/tests/test_paragraphs.py
git commit -m "feat: add body paragraph formatting"
```

## Task 9: Implement figure, table caption, and three-line-table formatting

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/figures.py`
- Test: `D:/2026project/docx_skill/tests/test_figures.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from docx import Document

from docx_formatter.config import load_template
from docx_formatter.figures import apply_figure_table_formatting


def test_apply_figure_table_formatting_formats_caption_paragraphs():
    document = Document()
    document.add_paragraph("图 1-1 系统架构")
    document.add_paragraph("表 1-1 测试数据")
    table = document.add_table(rows=2, cols=2)
    config = load_template(Path("D:/2026project/docx_skill/templates/thesis.yaml"))

    apply_figure_table_formatting(document, config.figures)

    figure_caption = document.paragraphs[0]
    table_caption = document.paragraphs[1]
    assert figure_caption.alignment is not None
    assert table_caption.alignment is not None
    assert table._tbl.xml.count("w:top") >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_figures.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.figures'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/figures.py`
```python
from __future__ import annotations

import re

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .styles import apply_font

FIGURE_PATTERN = re.compile(r"^图\s+\d+(?:-\d+)?")
TABLE_PATTERN = re.compile(r"^表\s+\d+(?:-\d+)?")


def _set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge, edge_data in kwargs.items():
        tag = f"w:{edge}"
        element = tc_borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            tc_borders.append(element)
        for key, value in edge_data.items():
            element.set(qn(f"w:{key}"), str(value))


def apply_figure_table_formatting(document, figures_config):
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if FIGURE_PATTERN.match(text) or TABLE_PATTERN.match(text):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                apply_font(
                    run,
                    figures_config.caption_font_cn,
                    figures_config.caption_font_en,
                    figures_config.caption_size,
                    figures_config.caption_bold,
                    False,
                )
    if figures_config.table_style == "three_line":
        for table in document.tables:
            for cell in table.rows[0].cells:
                _set_cell_border(
                    cell,
                    top={"val": "single", "sz": 12},
                    bottom={"val": "single", "sz": 6},
                )
            for cell in table.rows[-1].cells:
                _set_cell_border(cell, bottom={"val": "single", "sz": 12})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_figures.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/figures.py D:/2026project/docx_skill/tests/test_figures.py
git commit -m "feat: add figure and table formatting"
```

## Task 10: Implement end-to-end formatting pipeline

**Files:**
- Create: `D:/2026project/docx_skill/docx_formatter/pipeline.py`
- Test: `D:/2026project/docx_skill/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from docx import Document

from docx_formatter.pipeline import create_document, format_document


def test_format_document_saves_formatted_copy(tmp_path):
    source = tmp_path / "source.docx"
    document = Document()
    document.add_heading("第一章 绪论", level=1)
    document.add_paragraph("正文内容")
    document.save(source)

    output = format_document(
        source_path=source,
        template_path=Path("D:/2026project/docx_skill/templates/thesis.yaml"),
        overrides={},
    )

    assert output.exists()
    assert output.name == "source_formatted.docx"


def test_create_document_builds_new_docx_from_sections(tmp_path):
    output = create_document(
        output_path=tmp_path / "new.docx",
        template_path=Path("D:/2026project/docx_skill/templates/report.yaml"),
        paragraphs=[
            {"type": "heading_1", "text": "项目概述"},
            {"type": "body", "text": "这里是正文。"},
        ],
        overrides={},
    )

    created = Document(output)
    assert created.paragraphs[0].text == "项目概述"
    assert created.paragraphs[1].text == "这里是正文。"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_pipeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.pipeline'`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/docx_formatter/pipeline.py`
```python
from __future__ import annotations

from pathlib import Path

from docx import Document

from .analyzer import analyze, summarize_analysis
from .config import load_template, merge_overrides
from .figures import apply_figure_table_formatting
from .headings import apply_heading_formatting
from .pages import apply_page_settings
from .paragraphs import apply_body_formatting


def _resolved_config(template_path: Path, overrides: dict):
    config = load_template(template_path)
    return merge_overrides(config, overrides)


def format_document(source_path: Path, template_path: Path, overrides: dict) -> Path:
    document = Document(source_path)
    config = _resolved_config(template_path, overrides)
    apply_page_settings(document, config.page)
    apply_heading_formatting(document, config.headings)
    apply_body_formatting(document, config.body)
    apply_figure_table_formatting(document, config.figures)
    output_path = source_path.with_name(f"{source_path.stem}_formatted.docx")
    document.save(output_path)
    return output_path


def create_document(output_path: Path, template_path: Path, paragraphs: list[dict], overrides: dict) -> Path:
    document = Document()
    config = _resolved_config(template_path, overrides)
    for item in paragraphs:
        if item["type"] == "heading_1":
            document.add_heading(item["text"], level=1)
        else:
            document.add_paragraph(item["text"])
    apply_page_settings(document, config.page)
    apply_heading_formatting(document, config.headings)
    apply_body_formatting(document, config.body)
    apply_figure_table_formatting(document, config.figures)
    document.save(output_path)
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/pipeline.py D:/2026project/docx_skill/tests/test_pipeline.py
git commit -m "feat: add docx formatting pipeline"
```

## Task 11: Write skill instructions and interaction contract

**Files:**
- Create: `D:/2026project/docx_skill/skill.md`
- Test: `D:/2026project/docx_skill/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_skill_md_mentions_confirmation_and_safe_output_path():
    content = Path("D:/2026project/docx_skill/skill.md").read_text(encoding="utf-8")
    assert "确认" in content
    assert "_formatted.docx" in content
    assert "模板" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest D:/2026project/docx_skill/tests/test_pipeline.py::test_skill_md_mentions_confirmation_and_safe_output_path -v`
Expected: FAIL with `FileNotFoundError` for `skill.md`

- [ ] **Step 3: Write minimal implementation**

`D:/2026project/docx_skill/skill.md`
```markdown
---
name: docx-formatter
summary: 根据模板和对话要求准确设置 docx 标题、正文、图表标题和页面格式
---

当用户要求排版、格式化、创建或修正文档样式时，使用这个 skill。

## 工作流程

1. 如果用户提供已有 `.docx` 文件，先分析文档结构并用中文总结段落数、标题数、表格数。
2. 询问用户使用哪种方式定义格式：
   - 预设模板
   - 对话指定
   - 模板 + 局部覆盖
3. 将最终格式设置整理为确认清单，请用户确认后再执行。
4. 执行 Python 格式化流程。
5. 输出新文件路径，默认文件名为原文件名加 `_formatted.docx`。

## 约束

- 不覆盖原始文档。
- 每次执行前必须确认最终格式设置。
- 若遇到无法自动识别的段落或图表标题，明确告诉用户需要人工复核。
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest D:/2026project/docx_skill/tests/test_pipeline.py::test_skill_md_mentions_confirmation_and_safe_output_path -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/skill.md D:/2026project/docx_skill/tests/test_pipeline.py
git commit -m "feat: add docx formatter skill instructions"
```

## Task 12: Run full verification and tighten plan/documentation gaps

**Files:**
- Modify: `D:/2026project/docx_skill/docx_formatter/config.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/utils.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/styles.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/analyzer.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/pages.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/headings.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/paragraphs.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/figures.py`
- Modify: `D:/2026project/docx_skill/docx_formatter/pipeline.py`
- Modify: `D:/2026project/docx_skill/skill.md`
- Modify: `D:/2026project/docx_skill/tests/test_config.py`
- Modify: `D:/2026project/docx_skill/tests/test_utils.py`
- Modify: `D:/2026project/docx_skill/tests/test_styles.py`
- Modify: `D:/2026project/docx_skill/tests/test_analyzer.py`
- Modify: `D:/2026project/docx_skill/tests/test_pages.py`
- Modify: `D:/2026project/docx_skill/tests/test_headings.py`
- Modify: `D:/2026project/docx_skill/tests/test_paragraphs.py`
- Modify: `D:/2026project/docx_skill/tests/test_figures.py`
- Modify: `D:/2026project/docx_skill/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing integration test**

```python
from pathlib import Path

from docx import Document

from docx_formatter.pipeline import format_document


def test_format_document_applies_heading_body_and_page_changes(tmp_path):
    source = tmp_path / "integration.docx"
    document = Document()
    document.add_heading("第一章 绪论", level=1)
    document.add_paragraph("这是第一段正文。")
    document.add_paragraph("图 1-1 系统架构")
    document.save(source)

    output = format_document(
        source_path=source,
        template_path=Path("D:/2026project/docx_skill/templates/thesis.yaml"),
        overrides={"body": {"first_line_indent": "2chars"}},
    )

    formatted = Document(output)
    assert formatted.paragraphs[0].style.name == "Heading 1"
    assert round(formatted.paragraphs[1].paragraph_format.first_line_indent.pt, 1) == 24.0
    assert "PAGE" in formatted.sections[0].footer._element.xml
```

- [ ] **Step 2: Run full test suite and verify the failing case**

Run: `pytest D:/2026project/docx_skill/tests -v`
Expected: at least one FAIL showing a mismatch between expected formatting behavior and the current implementation.

- [ ] **Step 3: Close the gaps found during full verification**

```python
# Update modules only where the full suite shows a real mismatch.
# Keep these signatures stable:
# - load_template(path: Path) -> FormatterConfig
# - merge_overrides(config: FormatterConfig, overrides: dict[str, Any]) -> FormatterConfig
# - analyze(filepath: Path) -> dict
# - summarize_analysis(result: dict) -> str
# - apply_page_settings(document, page_config) -> None
# - apply_heading_formatting(document, headings_config) -> None
# - apply_body_formatting(document, body_config) -> None
# - apply_figure_table_formatting(document, figures_config) -> None
# - format_document(source_path: Path, template_path: Path, overrides: dict) -> Path
# - create_document(output_path: Path, template_path: Path, paragraphs: list[dict], overrides: dict) -> Path
```

- [ ] **Step 4: Run full test suite to verify all modules pass together**

Run: `pytest D:/2026project/docx_skill/tests -v`
Expected: PASS for all test files.

- [ ] **Step 5: Commit**

```bash
git add D:/2026project/docx_skill/docx_formatter/config.py D:/2026project/docx_skill/docx_formatter/utils.py D:/2026project/docx_skill/docx_formatter/styles.py D:/2026project/docx_skill/docx_formatter/analyzer.py D:/2026project/docx_skill/docx_formatter/pages.py D:/2026project/docx_skill/docx_formatter/headings.py D:/2026project/docx_skill/docx_formatter/paragraphs.py D:/2026project/docx_skill/docx_formatter/figures.py D:/2026project/docx_skill/docx_formatter/pipeline.py D:/2026project/docx_skill/skill.md D:/2026project/docx_skill/tests/test_config.py D:/2026project/docx_skill/tests/test_utils.py D:/2026project/docx_skill/tests/test_styles.py D:/2026project/docx_skill/tests/test_analyzer.py D:/2026project/docx_skill/tests/test_pages.py D:/2026project/docx_skill/tests/test_headings.py D:/2026project/docx_skill/tests/test_paragraphs.py D:/2026project/docx_skill/tests/test_figures.py D:/2026project/docx_skill/tests/test_pipeline.py
git commit -m "test: verify end-to-end docx formatting workflow"
```

## Spec coverage check
- Existing document formatting: covered by Tasks 5, 6, 7, 8, 9, 10, and 12.
- New document creation: covered by Task 10.
- Dual configuration sources (template + runtime overrides): covered by Task 2 and exercised in Tasks 10 and 12.
- Heading formatting: covered by Task 7.
- Body formatting with 宋体、首行缩进、行距: covered by Task 8.
- Figure/table caption formatting and three-line tables: covered by Task 9.
- Page settings including margins, headers/footers, page numbers: covered by Task 6.
- Claude-facing interaction flow and confirmation requirement: covered by Task 11.

## Self-review notes
- Removed placeholders and kept file paths explicit.
- Kept function names consistent across tasks.
- Preserved a single orchestration entrypoint in `pipeline.py` so the skill can call one API for format/create flows.
