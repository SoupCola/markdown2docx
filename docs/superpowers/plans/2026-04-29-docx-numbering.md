# DOCX Automatic Numbering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Word-native automatic numbering support for generated documents and conservative conversion of clearly matched handwritten numbering in existing `.docx` files.

**Architecture:** Keep numbering responsibilities isolated in a new `docx_formatter/numbering.py` module. Extend configuration and template loading so numbering styles are first-class settings, then route `create_document()` and `format_document()` through the numbering module while keeping headings, body, figures, and pages responsibilities unchanged.

**Tech Stack:** Python 3, `python-docx`, OOXML paragraph/numbering XML, PyYAML, pytest

---

## File Structure

- `docx_formatter/config.py`
  - Add numbering config dataclasses and loader support.
  - Extend `FormatterConfig` and override merging so templates/overrides can carry numbering settings.
- `templates/thesis.yaml`
  - Add the first supported `numbering:` block used by tests and examples.
- `docx_formatter/numbering.py`
  - New focused module for numbering pattern detection, numbering definition registration, generated numbering application, and safe conversion.
- `docx_formatter/pipeline.py`
  - Route `create_document()` numbered paragraph types into numbering generation.
  - Route `format_document()` through numbering detection/conversion after existing formatting passes.
- `tests/test_config.py`
  - Verify numbering config loads and override merging works.
- `tests/test_numbering.py`
  - New direct unit tests for numbering detection, rejection, grouping, conversion, and generation helpers.
- `tests/test_pipeline.py`
  - Add end-to-end tests for generated numbering and format-time conversion.
- `examples/thesis_full_sample.docx`
  - Regenerate after implementation to include automatic numbering examples for manual inspection.

## Implementation Notes

- Keep the first version limited to three numbering styles only:
  - `numbered_level_1` → `1.`
  - `numbered_level_2` → `（1）`
  - `numbered_bracket` → `[1]`
- Detection must be strict and conservative:
  - level 1 must start at `1.` and be continuous
  - bracket lists must start at `[1]` and be continuous
  - level 2 items only convert when attached to a recognized parent level-1 item
  - ambiguous groups stay unchanged
- Conversion removes handwritten prefixes from paragraph text before applying Word numbering.
- Body formatting should continue to style converted/generated numbered paragraphs, but numbering-specific indentation/alignment should be applied by `numbering.py`.
- Tests should validate behavior via reopened documents and XML traits, not by visual assumptions alone.

### Task 1: Extend template and config support for numbering

**Files:**
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/config.py`
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_config.py`

- [ ] **Step 1: Write the failing config tests**

```python
from pathlib import Path

from docx_formatter.config import load_template, merge_overrides


def test_load_template_reads_numbering_defaults():
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))
    assert config.numbering.strict_mode is True
    assert config.numbering.level_1.style == "arabic_dot"
    assert config.numbering.level_2.style == "paren_cn"
    assert config.numbering.bracket.style == "bracket_arabic"


def test_merge_overrides_updates_nested_numbering_fields_only():
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))
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
```

- [ ] **Step 2: Run the config tests to verify they fail**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_config.py -v`
Expected: FAIL with `FormatterConfig` missing `numbering` or template key errors.

- [ ] **Step 3: Add numbering dataclasses and loader support**

```python
@dataclass
class NumberingLevelConfig:
    style: str
    align: str
    first_line_indent: str
    hanging_indent: str
    font_cn: str
    font_en: str
    size: str
    line_spacing: str
    space_before: str
    space_after: str


@dataclass
class NumberingConfig:
    strict_mode: bool
    level_1: NumberingLevelConfig
    level_2: NumberingLevelConfig
    bracket: NumberingLevelConfig


@dataclass
class FormatterConfig:
    name: str
    description: str
    page: PageConfig
    headings: HeadingsConfig
    body: BodyConfig
    figures: FiguresConfig
    numbering: NumberingConfig
```

```python
def _numbering_level(data: dict[str, Any]) -> NumberingLevelConfig:
    return NumberingLevelConfig(**data)


def _from_dict(data: dict[str, Any]) -> FormatterConfig:
    return FormatterConfig(
        name=data["name"],
        description=data["description"],
        page=PageConfig(...),
        headings=HeadingsConfig(...),
        body=BodyConfig(**data["body"]),
        figures=FiguresConfig(**data["figures"]),
        numbering=NumberingConfig(
            strict_mode=data["numbering"].get("strict_mode", True),
            level_1=_numbering_level(data["numbering"]["level_1"]),
            level_2=_numbering_level(data["numbering"]["level_2"]),
            bracket=_numbering_level(data["numbering"]["bracket"]),
        ),
    )
```

```python
base = {
    "name": config.name,
    "description": config.description,
    "page": {...},
    "headings": {...},
    "body": deepcopy(config.body.__dict__),
    "figures": deepcopy(config.figures.__dict__),
    "numbering": {
        "strict_mode": config.numbering.strict_mode,
        "level_1": deepcopy(config.numbering.level_1.__dict__),
        "level_2": deepcopy(config.numbering.level_2.__dict__),
        "bracket": deepcopy(config.numbering.bracket.__dict__),
    },
}
```

- [ ] **Step 4: Add numbering defaults to the thesis template**

```yaml
numbering:
  strict_mode: true
  level_1:
    style: arabic_dot
    align: left
    first_line_indent: 0chars
    hanging_indent: 2chars
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小四"
    line_spacing: 1.5lines
    space_before: 0pt
    space_after: 0pt
  level_2:
    style: paren_cn
    align: left
    first_line_indent: 0chars
    hanging_indent: 2chars
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小四"
    line_spacing: 1.5lines
    space_before: 0pt
    space_after: 0pt
  bracket:
    style: bracket_arabic
    align: left
    first_line_indent: 0chars
    hanging_indent: 2chars
    font_cn: "宋体"
    font_en: "Times New Roman"
    size: "小四"
    line_spacing: 1.5lines
    space_before: 0pt
    space_after: 0pt
```

- [ ] **Step 5: Run the config tests to verify they pass**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_config.py -v`
Expected: PASS for both existing config tests and the new numbering tests.

- [ ] **Step 6: Commit the config and template changes**

```bash
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" add docx_formatter/config.py templates/thesis.yaml tests/test_config.py
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" commit -m "feat: add numbering configuration support"
```

### Task 2: Add strict numbering detection and analysis helpers

**Files:**
- Create: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/numbering.py`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py`

- [ ] **Step 1: Write the failing detection tests**

```python
from pathlib import Path

from docx import Document

from docx_formatter.config import load_template
from docx_formatter.numbering import detect_numbering_groups


def test_detect_numbering_groups_recognizes_supported_prefixes():
    document = Document()
    document.add_paragraph("1. 一级内容")
    document.add_paragraph("（1）二级内容")
    document.add_paragraph("[1] 参考文献1")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    assert any(item.text == "一级内容" for item in analysis.convertible_items)
    assert any(item.text == "二级内容" for item in analysis.rejected_items)
    assert any(item.text == "参考文献1" for item in analysis.convertible_items)


def test_detect_numbering_groups_rejects_non_starting_or_non_contiguous_sequences():
    document = Document()
    document.add_paragraph("2. 内容")
    document.add_paragraph("[2] 参考文献2")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    reasons = {item.reason for item in analysis.rejected_items}
    assert "sequence_must_start_at_1" in reasons


def test_detect_numbering_groups_rejects_figure_like_prefixes():
    document = Document()
    document.add_paragraph("表 1. 测试数据")
    document.add_paragraph("图 1. 系统架构")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    assert analysis.convertible_items == []
    assert analysis.rejected_items == []
```

- [ ] **Step 2: Run the direct numbering tests to verify they fail**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'docx_formatter.numbering'`.

- [ ] **Step 3: Create the minimal numbering analysis types and parsing helpers**

```python
from __future__ import annotations

from dataclasses import dataclass
import re

LEVEL_1_PATTERN = re.compile(r"^(\d+)\.\s+(.+)$")
LEVEL_2_PATTERN = re.compile(r"^（(\d+)）(.+)$")
BRACKET_PATTERN = re.compile(r"^\[(\d+)\]\s*(.+)$")


@dataclass
class NumberingCandidate:
    paragraph_index: int
    kind: str
    number: int
    prefix: str
    text: str
    paragraph: object


@dataclass
class RejectedNumberingItem:
    paragraph_index: int
    kind: str
    original_text: str
    text: str
    reason: str


@dataclass
class DetectedNumberingAnalysis:
    convertible_items: list[NumberingCandidate]
    rejected_items: list[RejectedNumberingItem]


def _parse_candidate(paragraph, index: int) -> NumberingCandidate | None:
    text = paragraph.text.strip()
    for kind, pattern in (
        ("level_1", LEVEL_1_PATTERN),
        ("level_2", LEVEL_2_PATTERN),
        ("bracket", BRACKET_PATTERN),
    ):
        match = pattern.match(text)
        if match:
            number = int(match.group(1))
            body = match.group(2).strip()
            prefix = text[: len(text) - len(body)].rstrip()
            return NumberingCandidate(index, kind, number, prefix, body, paragraph)
    return None
```

- [ ] **Step 4: Implement strict grouping and rejection logic**

```python
def _evaluate_flat_sequence(
    candidates: list[NumberingCandidate],
    rejected_items: list[RejectedNumberingItem],
) -> list[NumberingCandidate]:
    if not candidates:
        return []
    if candidates[0].number != 1:
        for candidate in candidates:
            rejected_items.append(
                RejectedNumberingItem(
                    paragraph_index=candidate.paragraph_index,
                    kind=candidate.kind,
                    original_text=candidate.paragraph.text,
                    text=candidate.text,
                    reason="sequence_must_start_at_1",
                )
            )
        return []
    expected = 1
    convertible: list[NumberingCandidate] = []
    for candidate in candidates:
        if candidate.number != expected:
            for item in candidates:
                rejected_items.append(
                    RejectedNumberingItem(
                        paragraph_index=item.paragraph_index,
                        kind=item.kind,
                        original_text=item.paragraph.text,
                        text=item.text,
                        reason="sequence_must_be_contiguous",
                    )
                )
            return []
        convertible.append(candidate)
        expected += 1
    return convertible
```

```python
def detect_numbering_groups(document, numbering_config) -> DetectedNumberingAnalysis:
    candidates = []
    rejected_items: list[RejectedNumberingItem] = []
    for index, paragraph in enumerate(document.paragraphs):
        candidate = _parse_candidate(paragraph, index)
        if candidate is not None:
            candidates.append(candidate)

    level_1_candidates = [item for item in candidates if item.kind == "level_1"]
    bracket_candidates = [item for item in candidates if item.kind == "bracket"]
    level_2_candidates = [item for item in candidates if item.kind == "level_2"]

    convertible_items = []
    convertible_items.extend(_evaluate_flat_sequence(level_1_candidates, rejected_items))
    convertible_items.extend(_evaluate_flat_sequence(bracket_candidates, rejected_items))

    for candidate in level_2_candidates:
        rejected_items.append(
            RejectedNumberingItem(
                paragraph_index=candidate.paragraph_index,
                kind=candidate.kind,
                original_text=candidate.paragraph.text,
                text=candidate.text,
                reason="missing_parent_level_1_context",
            )
        )

    convertible_items.sort(key=lambda item: item.paragraph_index)
    return DetectedNumberingAnalysis(convertible_items=convertible_items, rejected_items=rejected_items)
```

- [ ] **Step 5: Expand tests for parent-child grouping rules before implementing them**

```python
def test_detect_numbering_groups_assigns_level_2_items_under_level_1_parent():
    document = Document()
    document.add_paragraph("1. 一级内容")
    document.add_paragraph("（1）二级内容")
    document.add_paragraph("（2）二级补充")
    document.add_paragraph("2. 第二项")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    level_2_items = [item for item in analysis.convertible_items if item.kind == "level_2"]
    assert [item.text for item in level_2_items] == ["二级内容", "二级补充"]


def test_detect_numbering_groups_rejects_orphan_level_2_items():
    document = Document()
    document.add_paragraph("（2）脱离父级")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    assert analysis.rejected_items[0].reason == "missing_parent_level_1_context"
```

- [ ] **Step 6: Run the numbering tests to verify the new parent-child tests fail**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py -v`
Expected: FAIL because `level_2` items are still always rejected.

- [ ] **Step 7: Implement parent-aware level-2 grouping**

```python
def _evaluate_level_2_sequences(
    candidates: list[NumberingCandidate],
    convertible_level_1: list[NumberingCandidate],
    rejected_items: list[RejectedNumberingItem],
) -> list[NumberingCandidate]:
    if not candidates:
        return []

    parent_indexes = {item.paragraph_index for item in convertible_level_1}
    result: list[NumberingCandidate] = []
    current_group: list[NumberingCandidate] = []
    seen_parent = False
    last_index = -1

    for candidate in candidates:
        if any(parent_index < candidate.paragraph_index for parent_index in parent_indexes):
            if current_group and candidate.paragraph_index != last_index + 1:
                if current_group[0].number == 1 and [item.number for item in current_group] == list(range(1, len(current_group) + 1)):
                    result.extend(current_group)
                else:
                    for item in current_group:
                        rejected_items.append(
                            RejectedNumberingItem(
                                paragraph_index=item.paragraph_index,
                                kind=item.kind,
                                original_text=item.paragraph.text,
                                text=item.text,
                                reason="missing_parent_level_1_context" if current_group[0].number != 1 else "sequence_must_be_contiguous",
                            )
                        )
                current_group = []
            seen_parent = True

        if not seen_parent:
            rejected_items.append(
                RejectedNumberingItem(
                    paragraph_index=candidate.paragraph_index,
                    kind=candidate.kind,
                    original_text=candidate.paragraph.text,
                    text=candidate.text,
                    reason="missing_parent_level_1_context",
                )
            )
            continue

        current_group.append(candidate)
        last_index = candidate.paragraph_index

    if current_group:
        if current_group[0].number == 1 and [item.number for item in current_group] == list(range(1, len(current_group) + 1)):
            result.extend(current_group)
        else:
            for item in current_group:
                rejected_items.append(
                    RejectedNumberingItem(
                        paragraph_index=item.paragraph_index,
                        kind=item.kind,
                        original_text=item.paragraph.text,
                        text=item.text,
                        reason="missing_parent_level_1_context" if current_group[0].number != 1 else "sequence_must_be_contiguous",
                    )
                )
    return result
```

```python
convertible_level_1 = _evaluate_flat_sequence(level_1_candidates, rejected_items)
convertible_items.extend(convertible_level_1)
convertible_items.extend(_evaluate_flat_sequence(bracket_candidates, rejected_items))
convertible_items.extend(_evaluate_level_2_sequences(level_2_candidates, convertible_level_1, rejected_items))
```

- [ ] **Step 8: Run the numbering tests to verify detection passes**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py -v`
Expected: PASS for supported detection, rejection, and parent-child grouping tests.

- [ ] **Step 9: Commit the numbering detection module**

```bash
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" add docx_formatter/numbering.py tests/test_numbering.py
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" commit -m "feat: add strict numbering detection"
```

### Task 3: Add numbering definition registration and generated paragraph support

**Files:**
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/numbering.py`
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/pipeline.py`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing generation tests**

```python
from docx import Document

from docx_formatter.numbering import apply_generated_numbering


def test_apply_generated_numbering_assigns_numbering_xml_to_supported_items():
    document = Document()
    paragraphs = [
        {"type": "numbered_level_1", "text": "研究目标"},
        {"type": "numbered_level_2", "text": "理论基础"},
        {"type": "numbered_bracket", "text": "参考文献1"},
    ]

    apply_generated_numbering(document, paragraphs, load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml")).numbering)

    assert document.paragraphs[0].text == "研究目标"
    assert "w:numPr" in document.paragraphs[0]._p.xml
    assert "w:ilvl" in document.paragraphs[1]._p.xml
    assert "w:numPr" in document.paragraphs[2]._p.xml
```

```python
def test_create_document_builds_word_numbered_paragraphs(tmp_path):
    output = create_document(
        output_path=tmp_path / "numbered.docx",
        template_path=Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"),
        paragraphs=[
            {"type": "heading_1", "text": "第一章 绪论"},
            {"type": "numbered_level_1", "text": "研究目标"},
            {"type": "numbered_level_2", "text": "理论基础"},
            {"type": "numbered_bracket", "text": "参考文献1"},
        ],
        overrides={},
    )

    created = Document(output)
    assert created.paragraphs[1].text == "研究目标"
    assert "w:numPr" in created.paragraphs[1]._p.xml
    assert "w:numPr" in created.paragraphs[2]._p.xml
    assert "w:numPr" in created.paragraphs[3]._p.xml
```

- [ ] **Step 2: Run the generation tests to verify they fail**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py -v`
Expected: FAIL because `apply_generated_numbering` does not exist and `create_document()` treats numbered items as plain paragraphs.

- [ ] **Step 3: Add minimal numbering definition registration helpers**

```python
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from .styles import ALIGNMENT_MAP, apply_font
from .utils import chars_to_pt, cn_size_to_pt, parse_distance, parse_line_spacing


def _ensure_abstract_numbering(document, abstract_id: int, level_text: str) -> None:
    numbering = document.part.numbering_part.element
    if numbering.find(qn(f"w:abstractNum[@w:abstractNumId='{abstract_id}']")) is not None:
        return
```

```python
def _append_level(abstract_num, ilvl: int, num_fmt: str, level_text: str) -> None:
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), str(ilvl))
    start = OxmlElement("w:start")
    start.set(qn("w:val"), "1")
    num_fmt_element = OxmlElement("w:numFmt")
    num_fmt_element.set(qn("w:val"), num_fmt)
    lvl_text = OxmlElement("w:lvlText")
    lvl_text.set(qn("w:val"), level_text)
    level.extend([start, num_fmt_element, lvl_text])
    abstract_num.append(level)
```

```python
def _register_numbering_definitions(document) -> dict[str, int]:
    return {
        "level_1": _ensure_number_definition(document, abstract_id=100, num_id=100, num_fmt="decimal", level_text="%1."),
        "level_2": _ensure_number_definition(document, abstract_id=101, num_id=101, num_fmt="decimal", level_text="（%1）"),
        "bracket": _ensure_number_definition(document, abstract_id=102, num_id=102, num_fmt="decimal", level_text="[%1]"),
    }
```

- [ ] **Step 4: Add paragraph numbering/style application helpers**

```python
def _set_paragraph_numbering(paragraph, num_id: int, ilvl: int) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.get_or_add_numPr()
    ilvl_element = num_pr.find(qn("w:ilvl")) or OxmlElement("w:ilvl")
    ilvl_element.set(qn("w:val"), str(ilvl))
    num_id_element = num_pr.find(qn("w:numId")) or OxmlElement("w:numId")
    num_id_element.set(qn("w:val"), str(num_id))
    if ilvl_element.getparent() is None:
        num_pr.append(ilvl_element)
    if num_id_element.getparent() is None:
        num_pr.append(num_id_element)
```

```python
def _apply_numbering_paragraph_format(paragraph, level_config) -> None:
    font_size = cn_size_to_pt(level_config.size)
    spacing_mode, spacing_value = parse_line_spacing(level_config.line_spacing)
    before_unit, before_value = parse_distance(level_config.space_before)
    after_unit, after_value = parse_distance(level_config.space_after)

    paragraph.paragraph_format.first_line_indent = Pt(chars_to_pt(level_config.first_line_indent, font_size))
    paragraph.paragraph_format.left_indent = Pt(chars_to_pt(level_config.hanging_indent, font_size))
    paragraph.paragraph_format.alignment = ALIGNMENT_MAP[level_config.align]
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE if spacing_mode == "multiple" else None
    paragraph.paragraph_format.line_spacing = spacing_value
    if before_unit == "pt":
        paragraph.paragraph_format.space_before = Pt(before_value)
    if after_unit == "pt":
        paragraph.paragraph_format.space_after = Pt(after_value)
    for run in paragraph.runs:
        apply_font(run, level_config.font_cn, level_config.font_en, level_config.size, False, False)
```

```python
def apply_generated_numbering(document, paragraphs: list[dict], numbering_config) -> None:
    num_ids = _register_numbering_definitions(document)
    config_map = {
        "numbered_level_1": ("level_1", 0),
        "numbered_level_2": ("level_2", 0),
        "numbered_bracket": ("bracket", 0),
    }
    for item in paragraphs:
        kind = item["type"]
        if kind not in config_map:
            continue
        config_key, ilvl = config_map[kind]
        paragraph = document.add_paragraph(item["text"])
        _set_paragraph_numbering(paragraph, num_ids[config_key], ilvl)
        _apply_numbering_paragraph_format(paragraph, getattr(numbering_config, config_key))
```

- [ ] **Step 5: Update `create_document()` to call the numbering generator**

```python
from .numbering import apply_generated_numbering


def create_document(output_path: Path, template_path: Path, paragraphs: list[dict], overrides: dict) -> Path:
    document = Document()
    config = _resolved_config(template_path, overrides)
    for item in paragraphs:
        if item["type"] == "heading_1":
            document.add_heading(item["text"], level=1)
        elif item["type"] == "heading_2":
            document.add_heading(item["text"], level=2)
        elif item["type"] == "heading_3":
            document.add_heading(item["text"], level=3)
        elif item["type"] in {"numbered_level_1", "numbered_level_2", "numbered_bracket"}:
            apply_generated_numbering(document, [item], config.numbering)
        else:
            document.add_paragraph(item["text"])
```

- [ ] **Step 6: Run the generation tests to verify they pass**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py -v`
Expected: PASS for the new generation tests and existing pipeline tests.

- [ ] **Step 7: Commit generated numbering support**

```bash
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" add docx_formatter/numbering.py docx_formatter/pipeline.py tests/test_numbering.py tests/test_pipeline.py
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" commit -m "feat: generate word numbering paragraphs"
```

### Task 4: Add safe conversion from handwritten numbering to Word numbering

**Files:**
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/numbering.py`
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/docx_formatter/pipeline.py`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py`
- Test: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing conversion tests**

```python
from docx import Document

from docx_formatter.numbering import convert_detected_numbering, detect_numbering_groups


def test_convert_detected_numbering_replaces_bracket_prefix_with_word_numbering():
    document = Document()
    document.add_paragraph("[1] 参考文献1")
    document.add_paragraph("[2] 参考文献2")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))
    analysis = detect_numbering_groups(document, config.numbering)

    convert_detected_numbering(document, analysis, config.numbering)

    assert document.paragraphs[0].text == "参考文献1"
    assert document.paragraphs[1].text == "参考文献2"
    assert "w:numPr" in document.paragraphs[0]._p.xml
    assert "w:numPr" in document.paragraphs[1]._p.xml
```

```python
def test_format_document_converts_supported_numbering_and_preserves_ambiguous_text(tmp_path):
    source = tmp_path / "numbering-source.docx"
    document = Document()
    document.add_paragraph("[1] 参考文献1")
    document.add_paragraph("[2] 参考文献2")
    document.add_paragraph("2. 不安全编号")
    document.save(source)

    output = format_document(
        source_path=source,
        template_path=Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"),
        overrides={},
    )

    formatted = Document(output)
    assert formatted.paragraphs[0].text == "参考文献1"
    assert formatted.paragraphs[1].text == "参考文献2"
    assert "w:numPr" in formatted.paragraphs[0]._p.xml
    assert formatted.paragraphs[2].text == "2. 不安全编号"
    assert "w:numPr" not in formatted.paragraphs[2]._p.xml
```

- [ ] **Step 2: Run the conversion tests to verify they fail**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py -v`
Expected: FAIL because `convert_detected_numbering` does not exist and `format_document()` never converts numbering.

- [ ] **Step 3: Implement minimal conversion helper**

```python
def _replace_paragraph_text(paragraph, text: str) -> None:
    paragraph.clear()
    paragraph.add_run(text)
```

```python
def convert_detected_numbering(document, analysis: DetectedNumberingAnalysis, numbering_config) -> None:
    num_ids = _register_numbering_definitions(document)
    config_map = {
        "level_1": (num_ids["level_1"], numbering_config.level_1, 0),
        "level_2": (num_ids["level_2"], numbering_config.level_2, 0),
        "bracket": (num_ids["bracket"], numbering_config.bracket, 0),
    }
    for item in analysis.convertible_items:
        num_id, level_config, ilvl = config_map[item.kind]
        _replace_paragraph_text(item.paragraph, item.text)
        _set_paragraph_numbering(item.paragraph, num_id, ilvl)
        _apply_numbering_paragraph_format(item.paragraph, level_config)
```

- [ ] **Step 4: Wire conversion into `format_document()` after current formatting passes**

```python
from .numbering import convert_detected_numbering, detect_numbering_groups


def format_document(source_path: Path, template_path: Path, overrides: dict) -> Path:
    document = Document(source_path)
    config = _resolved_config(template_path, overrides)
    apply_page_settings(document, config.page)
    apply_heading_formatting(document, config.headings)
    apply_body_formatting(document, config.body)
    apply_figure_table_formatting(document, config.figures)
    analysis = detect_numbering_groups(document, config.numbering)
    convert_detected_numbering(document, analysis, config.numbering)
    output_path = source_path.with_name(f"{source_path.stem}_formatted.docx")
    document.save(output_path)
    return output_path
```

- [ ] **Step 5: Add explicit rejection coverage for no-space bracket and orphan level-2 cases before finalizing logic**

```python
def test_convert_detected_numbering_handles_bracket_prefix_without_space():
    document = Document()
    document.add_paragraph("[1]文献1")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))
    analysis = detect_numbering_groups(document, config.numbering)

    convert_detected_numbering(document, analysis, config.numbering)

    assert document.paragraphs[0].text == "文献1"
    assert "w:numPr" in document.paragraphs[0]._p.xml


def test_format_document_keeps_orphan_level_2_text_unchanged(tmp_path):
    source = tmp_path / "orphan-level-2.docx"
    document = Document()
    document.add_paragraph("（2）孤立二级项")
    document.save(source)

    output = format_document(
        source_path=source,
        template_path=Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"),
        overrides={},
    )

    formatted = Document(output)
    assert formatted.paragraphs[0].text == "（2）孤立二级项"
    assert "w:numPr" not in formatted.paragraphs[0]._p.xml
```

- [ ] **Step 6: Run the conversion-focused tests to verify they pass**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py -v`
Expected: PASS for bracket conversion, no-space bracket conversion, safe rejection, and end-to-end format conversion.

- [ ] **Step 7: Commit conversion support**

```bash
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" add docx_formatter/numbering.py docx_formatter/pipeline.py tests/test_numbering.py tests/test_pipeline.py
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" commit -m "feat: convert handwritten numbering safely"
```

### Task 5: Strengthen sequencing, style, and sample verification

**Files:**
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py`
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py`
- Modify: `D:/2026project/docx_skill/.worktrees/docx-formatter/examples/thesis_full_sample.docx`

- [ ] **Step 1: Add failing regression tests for exact supported scenarios**

```python
def test_detect_numbering_groups_rejects_skipped_level_1_sequence():
    document = Document()
    document.add_paragraph("1. 第一项")
    document.add_paragraph("3. 第三项")
    config = load_template(Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"))

    analysis = detect_numbering_groups(document, config.numbering)

    assert {item.reason for item in analysis.rejected_items} == {"sequence_must_be_contiguous"}
```

```python
def test_generated_numbering_preserves_body_text_without_prefixes(tmp_path):
    output = create_document(
        output_path=tmp_path / "generated-numbering.docx",
        template_path=Path("D:/2026project/docx_skill/.worktrees/docx-formatter/templates/thesis.yaml"),
        paragraphs=[
            {"type": "numbered_level_1", "text": "第一项"},
            {"type": "numbered_level_1", "text": "第二项"},
            {"type": "numbered_bracket", "text": "参考文献1"},
            {"type": "numbered_bracket", "text": "参考文献2"},
        ],
        overrides={},
    )

    created = Document(output)
    assert [paragraph.text for paragraph in created.paragraphs] == ["第一项", "第二项", "参考文献1", "参考文献2"]
    assert all("w:numPr" in paragraph._p.xml for paragraph in created.paragraphs)
```

- [ ] **Step 2: Run the focused regression tests to verify they fail if gaps remain**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_numbering.py D:/2026project/docx_skill/.worktrees/docx-formatter/tests/test_pipeline.py -v`
Expected: FAIL only if contiguous-sequence or generated-text behavior is still incomplete.

- [ ] **Step 3: Tighten numbering logic if needed so regressions pass without widening scope**

```python
if candidate.number != expected:
    for item in candidates:
        rejected_items.append(
            RejectedNumberingItem(
                paragraph_index=item.paragraph_index,
                kind=item.kind,
                original_text=item.paragraph.text,
                text=item.text,
                reason="sequence_must_be_contiguous",
            )
        )
    return []
```

```python
paragraph = document.add_paragraph(item["text"])
_set_paragraph_numbering(paragraph, num_ids[config_key], ilvl)
_apply_numbering_paragraph_format(paragraph, getattr(numbering_config, config_key))
```

- [ ] **Step 4: Run the full test suite**

Run: `pytest D:/2026project/docx_skill/.worktrees/docx-formatter/tests -v`
Expected: PASS for all existing tests plus the new numbering coverage.

- [ ] **Step 5: Regenerate the sample document with numbering examples**

Run: `python D:/2026project/docx_skill/.worktrees/docx-formatter/scripts/generate_sample.py`
Expected: PASS and update `examples/thesis_full_sample.docx` to include level-1, level-2, and bracket numbering examples.

- [ ] **Step 6: Manually inspect the regenerated sample document**

Run: open `D:/2026project/docx_skill/.worktrees/docx-formatter/examples/thesis_full_sample.docx`
Expected: confirm visible Word numbering for `1.`, `（1）`, and `[1]` examples, correct continuation, and no handwritten prefixes in converted/generated content.

- [ ] **Step 7: Commit final tests and sample regeneration**

```bash
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" add tests/test_numbering.py tests/test_pipeline.py examples/thesis_full_sample.docx
git -C "D:/2026project/docx_skill/.worktrees/docx-formatter" commit -m "test: cover numbering generation and conversion"
```

## Self-Review Checklist

- Spec coverage checked:
  - config/template extension → Task 1
  - strict detection and rejection → Task 2
  - generated numbering in `create_document()` → Task 3
  - safe conversion in `format_document()` → Task 4
  - sample regeneration and full verification → Task 5
- Placeholder scan completed:
  - no `TODO` / `TBD`
  - every code-changing step includes concrete code blocks
  - every verification step includes exact commands and expected outcomes
- Type consistency checked:
  - `NumberingLevelConfig`, `NumberingConfig`, `DetectedNumberingAnalysis`, `NumberingCandidate`, and `RejectedNumberingItem` names are used consistently across tasks
  - `detect_numbering_groups`, `apply_generated_numbering`, and `convert_detected_numbering` signatures stay consistent across tasks
