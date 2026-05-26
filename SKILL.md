---
name: markdown2docx
description: "Convert Markdown files to formatted DOCX or re-format existing DOCX documents using configurable templates. Supports Chinese thesis, academic paper, and report templates with full page layout, heading, body, figure/table caption, formula, and bibliography formatting."
---

# markdown2docx

Convert Markdown files to formatted DOCX, or apply template formatting to an existing DOCX document.

Use this skill for Chinese thesis/report/paper workflows that need deterministic Word output from Markdown source, including headings, paragraphs, tables, images, formulas, references, captions, and page layout.

## When to Use

Use this skill when the user wants to:

- Convert one or more Markdown files into a `.docx`
- Apply a Chinese thesis, academic paper, or report template
- Format an existing `.docx` using a template
- Build a thesis/report from a config-driven project
- Preserve academic structure such as figure captions, table captions, formulas, citations, and bibliography
- Use a reference DOCX as a formatting source via `--format-docx`

Do not use this skill for:

- Converting DOCX/PDF back into Markdown
- Pure writing or proofreading tasks with no DOCX output
- Uploading local Claude configuration such as `.claude/`

## Core Principles

- Keep content in Markdown and formatting in YAML templates or a reference DOCX.
- Generate a new DOCX path; do not overwrite source Markdown.
- Prefer bundled template names (`thesis`, `academic_paper`, `report`) unless the user provides a custom YAML path.
- Keep image paths resolvable from the Markdown/project context.
- Treat generated DOCX as final-output draft; recommend manual visual review in Word for tables, figures, formulas, and fields.

## CLI Usage

### Convert Markdown to DOCX

```bash
python -m docx_formatter convert chapter1.md chapter2.md -o paper.docx -t thesis
python -m docx_formatter convert draft.md -o paper.docx -t thesis --override body.size=小四
python -m docx_formatter convert draft.md -o paper.docx -t thesis --format-docx reference.docx
```

Installed script entry:

```bash
docx-format convert chapter1.md -o paper.docx -t thesis
```

### Format Existing DOCX

```bash
python -m docx_formatter format draft.docx -t thesis
python -m docx_formatter format draft.docx -t academic_paper --override page.margins.left=3cm
```

Installed script entry:

```bash
docx-format format draft.docx -t thesis
```

### Show Help

```bash
python -m docx_formatter --help
python -m docx_formatter convert --help
python -m docx_formatter format --help
```

## Python API

```python
from pathlib import Path
from docx_formatter import create_from_markdown, format_document

create_from_markdown(
    output_path=Path("output.docx"),
    md_paths=[Path("chapter1.md"), Path("chapter2.md")],
    template_path=Path("docx_formatter/templates/thesis.yaml"),
    overrides={"body": {"size": "小四"}},
)

format_document(
    source_path=Path("draft.docx"),
    template_path=Path("docx_formatter/templates/thesis.yaml"),
    overrides={},
)
```

## Available Templates

| Template | File | Purpose |
|---|---|---|
| `thesis` | `docx_formatter/templates/thesis.yaml` | Chinese thesis formatting |
| `academic_paper` | `docx_formatter/templates/academic_paper.yaml` | Academic paper formatting |
| `report` | `docx_formatter/templates/report.yaml` | General report formatting |

`--template` accepts either a bundled template name or an absolute YAML path.

## Supported Markdown Patterns

Use these content patterns directly in Markdown:

```markdown
# 第四章 系统实现

## 4.1 系统架构

正文段落，支持 **加粗文本** 和安全的行内公式 $g_i \in (0, 1)$。

![系统架构图](assets/figures/architecture.png)

表4.2 题库表（question）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |

$$
E = mc^2
$$

正文引用文献[1]，并引用图4.1或表4.2。

[1] Smith J. Deep Learning. Nature, 2024.
```

Supported features include:

- Heading levels 1-3, with level-4 Markdown headings mapped to level 3 for thesis-style subsections
- Body paragraphs with configurable Chinese/English fonts, indentation, spacing, and line height
- Markdown tables, including explicit table captions above tables such as `表4.2 题库表（question）`
- Markdown images and automatic figure caption numbering
- Display formulas and safe inline LaTeX formulas
- Inline bold text in paragraphs and table cells
- Bibliography generation from numbered Markdown references
- Natural figure/table/reference cross-reference placeholders and Word REF fields
- Standalone horizontal rule filtering

## Thesis Project Workflow

Use `paper_workflow` when the document is managed as a project with `thesis.config.yaml`.

```bash
python -m paper_workflow build-docx -c thesis.config.yaml -r /path/to/project
python -m paper_workflow full-build -c thesis.config.yaml -r /path/to/project
python -m paper_workflow make-figure -c thesis.config.yaml -r /path/to/project
```

Installed script entry:

```bash
paper-workflow build-docx -c thesis.config.yaml
paper-workflow full-build -c thesis.config.yaml
paper-workflow make-figure -c thesis.config.yaml
```

Use `make-figure` to scan figure tasks declared before image references:

```markdown
<!-- figure:prompt="系统架构图，包含前端、后端、数据库三层" -->
![系统架构](assets/figures/architecture.png)
```

## Execution Checklist

1. Identify Markdown input files or existing DOCX input.
2. Identify the output `.docx` path.
3. Choose `convert`, `format`, or `paper_workflow` based on the request.
4. Choose the template or reference DOCX formatting source.
5. Run the command with explicit paths.
6. Verify that the output file exists.
7. Report the generated path and mention any manual Word review points.

## Common Mistakes

- Do not upload or package local `.claude/` configuration when preparing the skill for GitHub.
- Do not overwrite the source Markdown or original DOCX unless explicitly requested.
- Do not assume image paths resolve if the Markdown was moved.
- Do not duplicate a manual bibliography heading; the pipeline generates one when references exist.
- Do not assume Word fields are visually refreshed until the document is opened/refreshed in Word.
