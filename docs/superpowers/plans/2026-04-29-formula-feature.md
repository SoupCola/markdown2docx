# Formula Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add LaTeX formula support to docx_formatter with Times New Roman font, chapter-based numbering, and paragraph formatting.

**Architecture:** New `formulas.py` module handles LaTeX → MathML → OMML conversion, formula detection, formatting (center/no-indent/spacing), and chapter-based numbering. Integrated into existing pipeline alongside headings, body, figures, and numbering.

**Tech Stack:** `latex2mathml` (LaTeX → MathML), `mathml2omml` (MathML → OMML), `python-docx` XML manipulation

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `docx_formatter/formulas.py` | Create | Formula conversion, detection, formatting, numbering |
| `docx_formatter/config.py` | Modify | Add FormulaConfig dataclass |
| `docx_formatter/pipeline.py` | Modify | Integrate formula steps |
| `templates/thesis.yaml` | Modify | Add formulas section |
| `templates/report.yaml` | Modify | Add formulas section |
| `templates/academic_paper.yaml` | Modify | Add formulas section |
| `requirements.txt` | Modify | Add latex2mathml, mathml2omml |
| `tests/test_formulas.py` | Create | Formula module tests |
| `tests/test_pipeline.py` | Modify | Pipeline integration tests |

---

### Task 1: Add dependencies and FormulaConfig

**Files:**
- Modify: `requirements.txt`
- Modify: `docx_formatter/config.py`

- [ ] **Step 1: Update requirements.txt**

```txt
python-docx>=0.8.11
PyYAML>=6.0
pytest>=8.0
latex2mathml>=3.78
mathml2omml>=0.0.2
```

- [ ] **Step 2: Install dependencies**

Run: `pip install latex2mathml mathml2omml`

- [ ] **Step 3: Add FormulaConfig to config.py**

Add after `NumberingConfig`:

```python
@dataclass
class FormulaConfig:
    font_cn: str
    font_en: str
    size: str
    align: str
    space_before: str
    space_after: str
    numbering: str  # "chapter" or "continuous"
```

Update `FormatterConfig`:

```python
@dataclass
class FormatterConfig:
    name: str
    description: str
    page: PageConfig
    headings: HeadingsConfig
    body: BodyConfig
    figures: FiguresConfig
    numbering: NumberingConfig
    formulas: FormulaConfig
```

Update `_from_dict` — add formulas parsing:

```python
formulas=FormulaConfig(**data["formulas"]),
```

Update `merge_overrides` — add formulas to base dict:

```python
"formulas": deepcopy(config.formulas.__dict__),
```

- [ ] **Step 4: Run existing tests to verify no breakage**

Run: `conda activate base && pytest tests/test_config.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add requirements.txt docx_formatter/config.py
git commit -m "feat: add FormulaConfig and formula dependencies"
```

---

### Task 2: Update templates with formulas section

**Files:**
- Modify: `templates/thesis.yaml`
- Modify: `templates/report.yaml`
- Modify: `templates/academic_paper.yaml`

- [ ] **Step 1: Add formulas section to thesis.yaml**

Add after `numbering:` block:

```yaml
formulas:
  font_cn: "宋体"
  font_en: "Times New Roman"
  size: "小四"
  align: center
  space_before: 6pt
  space_after: 6pt
  numbering: chapter
```

- [ ] **Step 2: Add formulas section to report.yaml**

Same section as thesis.yaml.

- [ ] **Step 3: Add formulas section to academic_paper.yaml**

Same section as thesis.yaml.

- [ ] **Step 4: Run config tests**

Run: `conda activate base && pytest tests/test_config.py -v`
Expected: All pass (FormulaConfig parsed from templates)

- [ ] **Step 5: Commit**

```bash
git add templates/
git commit -m "feat: add formula config to templates"
```

---

### Task 3: TDD — LaTeX to OMML conversion

**Files:**
- Create: `tests/test_formulas.py`
- Create: `docx_formatter/formulas.py`

- [ ] **Step 1: Write failing tests for LaTeX conversion**

Create `tests/test_formulas.py`:

```python
from __future__ import annotations

from lxml import etree

from docx_formatter.formulas import latex_to_omml_element, set_formula_font


def test_latex_to_omml_simple():
    """Simple LaTeX x+y converts to OMML XML element."""
    el = latex_to_omml_element("x+y")
    assert el is not None
    omml_str = etree.tostring(el, encoding="unicode")
    assert "m:oMath" in omml_str


def test_latex_to_omml_fraction():
    """LaTeX fraction converts correctly."""
    el = latex_to_omml_element(r"\frac{1}{2}")
    assert el is not None
    omml_str = etree.tostring(el, encoding="unicode")
    assert "m:f" in omml_str  # OMML fraction element


def test_latex_to_omml_superscript():
    """LaTeX superscript converts correctly."""
    el = latex_to_omml_element("x^2")
    assert el is not None
    omml_str = etree.tostring(el, encoding="unicode")
    assert "m:sSup" in omml_str


def test_set_formula_font():
    """Font is set to Times New Roman on all m:r elements."""
    el = latex_to_omml_element("x+y")
    set_formula_font(el, "Times New Roman")
    omml_str = etree.tostring(el, encoding="unicode")
    assert "Times New Roman" in omml_str
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda activate base && pytest tests/test_formulas.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement latex_to_omml_element and set_formula_font**

Create `docx_formatter/formulas.py`:

```python
from __future__ import annotations

from lxml import etree

from docx.oxml.ns import qn


def latex_to_omml_element(latex_str: str) -> etree._Element:
    """Convert LaTeX string to OMML XML element via MathML."""
    import latex2mathml.converter
    import mathml2omml

    mathml = latex2mathml.converter.convert(latex_str)
    omml_str = mathml2omml.convert(mathml)
    return etree.fromstring(omml_str)


def set_formula_font(omml_element: etree._Element, font_en: str) -> None:
    """Set font on all m:r elements within an OMML element."""
    MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    for mr in omml_element.iter(f"{{{MATH_NS}}}r"):
        existing_rpr = mr.find(qn("m:rPr"))
        if existing_rpr is not None:
            mr.remove(existing_rpr)
        rpr = etree.SubElement(mr, qn("m:rPr"))
        rfonts = etree.SubElement(rpr, qn("m:rFonts"))
        rfonts.set(qn("m:ascii"), font_en)
        rfonts.set(qn("m:hAnsi"), font_en)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda activate base && pytest tests/test_formulas.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add tests/test_formulas.py docx_formatter/formulas.py
git commit -m "feat: LaTeX to OMML conversion with Times New Roman font"
```

---

### Task 4: TDD — Formula paragraph detection and insertion

**Files:**
- Modify: `tests/test_formulas.py`
- Modify: `docx_formatter/formulas.py`

- [ ] **Step 1: Write failing tests for detection and insertion**

Add to `tests/test_formulas.py`:

```python
from docx import Document

from docx_formatter.formulas import (
    insert_formula_paragraph,
    is_formula_paragraph,
    detect_formula_paragraphs,
)


def test_is_formula_paragraph_false():
    """Regular paragraph is not a formula paragraph."""
    doc = Document()
    p = doc.add_paragraph("Hello world")
    assert is_formula_paragraph(p) is False


def test_is_formula_paragraph_true():
    """Paragraph with inserted formula is detected."""
    doc = Document()
    p = insert_formula_paragraph(doc, "x+y", "Times New Roman")
    assert is_formula_paragraph(p) is True


def test_detect_formula_paragraphs():
    """Detects formula paragraphs among regular paragraphs."""
    doc = Document()
    doc.add_paragraph("Regular text 1")
    insert_formula_paragraph(doc, "x+y", "Times New Roman")
    doc.add_paragraph("Regular text 2")
    insert_formula_paragraph(doc, r"\frac{a}{b}", "Times New Roman")

    indices = detect_formula_paragraphs(doc)
    assert indices == [1, 3]


def test_insert_formula_paragraph_content():
    """Inserted paragraph contains OMML math element."""
    doc = Document()
    p = insert_formula_paragraph(doc, "E=mc^2", "Times New Roman")
    assert is_formula_paragraph(p) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda activate base && pytest tests/test_formulas.py::test_is_formula_paragraph_false tests/test_formulas.py::test_is_formula_paragraph_true tests/test_formulas.py::test_detect_formula_paragraphs tests/test_formulas.py::test_insert_formula_paragraph_content -v`
Expected: FAIL — functions not defined

- [ ] **Step 3: Implement detection and insertion**

Add to `docx_formatter/formulas.py`:

```python
from docx.oxml.ns import qn as _qn


def is_formula_paragraph(paragraph) -> bool:
    """Check if a paragraph contains m:oMath or m:oMathPara elements."""
    p = paragraph._p
    return (
        p.find(_qn("m:oMath")) is not None
        or p.find(_qn("m:oMathPara")) is not None
    )


def detect_formula_paragraphs(document) -> list[int]:
    """Return indices of paragraphs containing formulas."""
    return [
        i for i, p in enumerate(document.paragraphs) if is_formula_paragraph(p)
    ]


def insert_formula_paragraph(document, latex_str: str, font_en: str):
    """Add a new paragraph with formula from LaTeX, return the paragraph."""
    p = document.add_paragraph()
    omml = latex_to_omml_element(latex_str)
    set_formula_font(omml, font_en)
    p._p.append(omml)
    return p
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda activate base && pytest tests/test_formulas.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add tests/test_formulas.py docx_formatter/formulas.py
git commit -m "feat: formula paragraph detection and insertion"
```

---

### Task 5: TDD — Formula paragraph formatting

**Files:**
- Modify: `tests/test_formulas.py`
- Modify: `docx_formatter/formulas.py`

- [ ] **Step 1: Write failing tests for formula formatting**

Add to `tests/test_formulas.py`:

```python
from unittest.mock import MagicMock

from docx.shared import Pt


def _make_formula_config():
    """Create a mock FormulaConfig for testing."""
    config = MagicMock()
    config.font_en = "Times New Roman"
    config.size = "小四"
    config.align = "center"
    config.space_before = "6pt"
    config.space_after = "6pt"
    config.numbering = "chapter"
    return config


def test_apply_formula_formatting_center_align():
    """Formula paragraphs get center alignment."""
    from docx_formatter.formulas import apply_formula_formatting

    doc = Document()
    doc.add_paragraph("Regular text")
    insert_formula_paragraph(doc, "x+y", "Times New Roman")

    config = _make_formula_config()
    apply_formula_formatting(doc, config)

    assert doc.paragraphs[1].paragraph_format.alignment is not None


def test_apply_formula_formatting_no_indent():
    """Formula paragraphs have no first-line indent."""
    from docx_formatter.formulas import apply_formula_formatting

    doc = Document()
    doc.add_paragraph("Regular text")
    p = insert_formula_paragraph(doc, "x+y", "Times New Roman")

    config = _make_formula_config()
    apply_formula_formatting(doc, config)

    indent = p.paragraph_format.first_line_indent
    assert indent is None or indent == Pt(0)


def test_apply_formula_formatting_skips_regular():
    """Regular paragraphs are not affected by formula formatting."""
    from docx_formatter.formulas import apply_formula_formatting

    doc = Document()
    doc.add_paragraph("Regular text")

    config = _make_formula_config()
    apply_formula_formatting(doc, config)

    # Regular paragraph alignment should not be changed to center
    assert doc.paragraphs[0].paragraph_format.alignment is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda activate base && pytest tests/test_formulas.py::test_apply_formula_formatting -v`
Expected: FAIL — function not defined

- [ ] **Step 3: Implement apply_formula_formatting**

Add to `docx_formatter/formulas.py`:

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from .styles import ALIGNMENT_MAP
from .utils import cn_size_to_pt, parse_distance


def apply_formula_formatting(document, formula_config) -> None:
    """Apply formatting to all formula paragraphs."""
    for paragraph in document.paragraphs:
        if not is_formula_paragraph(paragraph):
            continue
        paragraph.paragraph_format.first_line_indent = Pt(0)
        paragraph.paragraph_format.alignment = ALIGNMENT_MAP[formula_config.align]
        before_unit, before_value = parse_distance(formula_config.space_before)
        after_unit, after_value = parse_distance(formula_config.space_after)
        if before_unit == "pt":
            paragraph.paragraph_format.space_before = Pt(before_value)
        if after_unit == "pt":
            paragraph.paragraph_format.space_after = Pt(after_value)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda activate base && pytest tests/test_formulas.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add tests/test_formulas.py docx_formatter/formulas.py
git commit -m "feat: formula paragraph formatting"
```

---

### Task 6: TDD — Formula numbering (chapter-based)

**Files:**
- Modify: `tests/test_formulas.py`
- Modify: `docx_formatter/formulas.py`

- [ ] **Step 1: Write failing tests for formula numbering**

Add to `tests/test_formulas.py`:

```python
def test_apply_formula_numbering_chapter():
    """Chapter-based numbering: (1-1), (1-2), (2-1)..."""
    from docx_formatter.formulas import apply_formula_numbering

    doc = Document()
    # Chapter 1
    doc.add_heading("Chapter 1", level=1)
    insert_formula_paragraph(doc, "x+y", "Times New Roman")  # (1-1)
    insert_formula_paragraph(doc, "a+b", "Times New Roman")  # (1-2)
    # Chapter 2
    doc.add_heading("Chapter 2", level=1)
    insert_formula_paragraph(doc, r"\frac{1}{2}", "Times New Roman")  # (2-1)
    # No chapter text
    doc.add_paragraph("Some text")

    config = _make_formula_config()
    config.numbering = "chapter"
    apply_formula_numbering(doc, config)

    # Formula paragraphs are at indices 1, 2, 4
    # After numbering, each should have a run with the number text
    p1 = doc.paragraphs[1]
    p2 = doc.paragraphs[2]
    p4 = doc.paragraphs[4]

    # Check that numbering runs were added
    texts = []
    for p in [p1, p2, p4]:
        for run in p.runs:
            if run.text.strip():
                texts.append(run.text.strip())
    assert "(1-1)" in texts
    assert "(1-2)" in texts
    assert "(2-1)" in texts


def test_apply_formula_numbering_continuous():
    """Continuous numbering: (1), (2), (3)..."""
    from docx_formatter.formulas import apply_formula_numbering

    doc = Document()
    doc.add_heading("Chapter 1", level=1)
    insert_formula_paragraph(doc, "x+y", "Times New Roman")
    doc.add_heading("Chapter 2", level=1)
    insert_formula_paragraph(doc, "a+b", "Times New Roman")

    config = _make_formula_config()
    config.numbering = "continuous"
    apply_formula_numbering(doc, config)

    p1 = doc.paragraphs[1]
    p2 = doc.paragraphs[3]

    texts = []
    for p in [p1, p2]:
        for run in p.runs:
            if run.text.strip():
                texts.append(run.text.strip())
    assert "(1)" in texts
    assert "(2)" in texts
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda activate base && pytest tests/test_formulas.py::test_apply_formula_numbering -v`
Expected: FAIL — function not defined

- [ ] **Step 3: Implement apply_formula_numbering**

Add to `docx_formatter/formulas.py`:

```python
def apply_formula_numbering(document, formula_config) -> None:
    """Add chapter-based or continuous numbering to formula paragraphs.

    Numbering is right-aligned using a right tab stop and tab character.
    """
    chapter_num = 0
    formula_count_in_chapter = 0
    continuous_count = 0

    for paragraph in document.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        if style_name.startswith("Heading 1"):
            chapter_num += 1
            formula_count_in_chapter = 0

        if not is_formula_paragraph(paragraph):
            continue

        if formula_config.numbering == "chapter":
            formula_count_in_chapter += 1
            label = f"({chapter_num}-{formula_count_in_chapter})"
        else:  # continuous
            continuous_count += 1
            label = f"({continuous_count})"

        # Add tab + number at end of paragraph
        tab_run = paragraph.add_run()
        tab_run._element.append(_make_tab_element())
        num_run = paragraph.add_run(label)
```

Add helper:

```python
def _make_tab_element():
    """Create a w:tab element."""
    from docx.oxml import OxmlElement
    tab = OxmlElement("w:tab")
    return tab
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda activate base && pytest tests/test_formulas.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add tests/test_formulas.py docx_formatter/formulas.py
git commit -m "feat: chapter-based formula numbering"
```

---

### Task 7: Integrate into pipeline

**Files:**
- Modify: `docx_formatter/pipeline.py`
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests for pipeline integration**

Add to `tests/test_pipeline.py`:

```python
def test_create_document_with_formula():
    """create_document supports formula type with LaTeX."""
    import tempfile
    from pathlib import Path
    from docx_formatter.pipeline import create_document

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "test_formula.docx"
        template = Path("templates/thesis.yaml")
        paragraphs = [
            {"type": "heading_1", "text": "第一章"},
            {"type": "formula", "latex": "E=mc^2"},
            {"type": "body", "text": "这是一段正文"},
        ]
        result = create_document(output, template, paragraphs, {})
        doc = Document(str(result))
        # Formula paragraph exists and is detected
        from docx_formatter.formulas import is_formula_paragraph
        formula_found = any(is_formula_paragraph(p) for p in doc.paragraphs)
        assert formula_found


def test_format_document_preserves_formulas():
    """format_document preserves formula content."""
    import tempfile
    from pathlib import Path
    from docx_formatter.pipeline import create_document, format_document

    with tempfile.TemporaryDirectory() as tmp:
        # First create a doc with formula
        source = Path(tmp) / "source.docx"
        template = Path("templates/thesis.yaml")
        paragraphs = [
            {"type": "heading_1", "text": "第一章"},
            {"type": "formula", "latex": "x^2 + y^2 = z^2"},
            {"type": "body", "text": "这是正文"},
        ]
        create_document(source, template, paragraphs, {})

        # Now format it
        result = format_document(source, template, {})

        from docx_formatter.formulas import is_formula_paragraph
        doc = Document(str(result))
        formula_found = any(is_formula_paragraph(p) for p in doc.paragraphs)
        assert formula_found
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda activate base && pytest tests/test_pipeline.py::test_create_document_with_formula tests/test_pipeline.py::test_format_document_preserves_formulas -v`
Expected: FAIL — formula type not handled

- [ ] **Step 3: Update pipeline.py**

Update imports:

```python
from .formulas import apply_formula_formatting, apply_formula_numbering, insert_formula_paragraph, is_formula_paragraph
```

Update `format_document` — add formula steps after numbering:

```python
def format_document(source_path: Path, template_path: Path, overrides: dict) -> Path:
    document = Document(source_path)
    config = _resolved_config(template_path, overrides)
    apply_page_settings(document, config.page)
    apply_heading_formatting(document, config.headings)
    apply_body_formatting(document, config.body)
    apply_figure_table_formatting(document, config.figures)
    analysis = detect_numbering_groups(document, config.numbering)
    convert_detected_numbering(document, analysis, config.numbering)
    for item in analysis.convertible_items:
        item.paragraph.paragraph_format.first_line_indent = Pt(0)
    apply_formula_formatting(document, config.formulas)
    apply_formula_numbering(document, config.formulas)
    output_path = source_path.with_name(f"{source_path.stem}_formatted.docx")
    document.save(output_path)
    return output_path
```

Update `create_document` — handle formula type:

```python
    formula_indices: set[int] = set()
    for item in paragraphs:
        if item["type"] == "heading_1":
            document.add_heading(item["text"], level=1)
            _flush_group()
        elif item["type"] == "heading_2":
            document.add_heading(item["text"], level=2)
            _flush_group()
        elif item["type"] == "heading_3":
            document.add_heading(item["text"], level=3)
            _flush_group()
        elif item["type"].startswith("numbered_"):
            document.add_paragraph(item["text"])
            current_group.append((len(document.paragraphs) - 1, item))
        elif item["type"] == "formula":
            insert_formula_paragraph(document, item["latex"], config.formulas.font_en)
            formula_indices.add(len(document.paragraphs) - 1)
            _flush_group()
        else:
            document.add_paragraph(item["text"])
            _flush_group()
```

Add formula formatting after body formatting:

```python
    apply_formula_formatting(document, config.formulas)
    apply_formula_numbering(document, config.formulas)
```

Also add formula indices to zero-indent:

```python
    for idx in numbered_indices | formula_indices:
        document.paragraphs[idx].paragraph_format.first_line_indent = Pt(0)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda activate base && pytest tests/ -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add docx_formatter/pipeline.py tests/test_pipeline.py
git commit -m "feat: integrate formula support into pipeline"
```

---

### Task 8: Update full_test.docx with formulas

**Files:**
- Modify: `examples/generate_test.py` or create inline

- [ ] **Step 1: Generate updated test document with formulas**

Create `examples/generate_formula_test.py`:

```python
"""Generate a test DOCX with formulas to verify formula formatting."""
from pathlib import Path
from docx_formatter import create_document

paragraphs = [
    {"type": "heading_1", "text": "第一章 理论基础"},
    {"type": "body", "text": "本章介绍基本理论公式。"},
    {"type": "formula", "latex": "E = mc^2"},
    {"type": "body", "text": "质能方程是物理学最著名的公式之一。"},
    {"type": "formula", "latex": r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"},
    {"type": "body", "text": "一元二次方程的求根公式。"},
    {"type": "heading_2", "text": "1.1 微积分"},
    {"type": "formula", "latex": r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"},
    {"type": "heading_1", "text": "第二章 实验设计"},
    {"type": "body", "text": "实验部分描述。"},
    {"type": "formula", "latex": r"\sum_{i=1}^{n} x_i^2"},
    {"type": "body", "text": "平方和公式。"},
]

output = Path("examples/formula_test.docx")
template = Path("templates/thesis.yaml")
create_document(output, template, paragraphs, {})
print(f"Generated: {output}")
```

- [ ] **Step 2: Run generation script**

Run: `conda activate base && python examples/generate_formula_test.py`

- [ ] **Step 3: Open and verify in Word**

Open `examples/formula_test.docx` in Word and check:
- Formulas render correctly (not as plain text)
- Formulas use Times New Roman font
- Formulas are centered
- Chapter numbering shows (1-1), (1-2), (1-3), (2-1)
- No first-line indent on formula paragraphs

- [ ] **Step 4: Commit**

```bash
git add examples/
git commit -m "test: add formula test document generator"
```
