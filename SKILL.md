---
name: markdown2docx
description: Use when a user wants to convert Markdown content into a DOCX file, especially when the document includes Chinese thesis/report structure, headings, tables, images, references, or requires a DOCX template plus local formatting overrides.
---

# markdown2docx

## Overview

Use this skill when the task is to turn one or more Markdown files into a `.docx` document with the local `docx_formatter` workflow.

Core principle: keep content in Markdown, keep formatting in template/config, and generate a new DOCX without overwriting the source file.

## When to Use

- User asks to convert `.md` to `.docx`
- User provides a Markdown chapter, report, thesis section, or technical document
- The Markdown contains headings, body paragraphs, tables, images, formulas, or bibliography references
- The output should follow a thesis/report template or a format extracted from an existing `.docx`
- The user wants the result saved as a new `.docx` file for later manual review in Word

Do not use this skill for:
- Converting DOCX/PDF into Markdown
- Pure style-only editing of an existing DOCX without Markdown as source
- General writing tasks where no DOCX output is needed

## Inputs to Confirm

Before conversion, identify these inputs from the user request or local files:

1. **Markdown source**
   - Single `.md` file or multiple `.md` files
2. **Output path**
   - Target `.docx` file path
3. **Formatting source**
   - `template_path` for YAML template, or
   - `format_docx_path` for extracting format from an existing `.docx`
4. **Optional overrides**
   - Local heading/body/page tweaks if the user specifies them

If the user gives only a Markdown file and no formatting preference, use the repository's default thesis-style template when appropriate.

## Local Skill Runtime

This skill is self-contained under `C:\Users\Administrator\.claude\skills\markdown2docx`.

Standard entrypoint:

```bash
python "C:/Users/Administrator/.claude/skills/markdown2docx/run_markdown2docx.py" \
  "path/to/input.md" \
  "path/to/output.docx"
```

Optional formatting source:

```bash
python "C:/Users/Administrator/.claude/skills/markdown2docx/run_markdown2docx.py" \
  "path/to/input.md" \
  "path/to/output.docx" \
  --template-path "C:/Users/Administrator/.claude/skills/markdown2docx/templates/thesis.yaml" \
  --format-docx-path "path/to/format-source.docx"
```

The script calls `docx_formatter.pipeline.create_from_markdown(...)` internally.

## Supported Content Patterns

Based on the current `docx_formatter` pipeline, this workflow can handle:

- `# / ## / ###` headings
- Normal paragraphs
- Markdown tables
- Markdown images
- Formula-related blocks supported by the parser/pipeline
- Bibliography/citation patterns such as footnote-style and numbered references

Example source shape:

```markdown
# 4.5 系统测试

## 4.5.1 测试目标与测试思路

正文内容。

| 项目 | 配置情况 | 说明 |
| --- | --- | --- |
| GPU | RTX 3060 | 用于推理 |

![系统测试流程图](./docs/requirements/images/system-test-flow.png)
```

## Execution Checklist

1. Read the Markdown file first
2. Confirm or infer the formatting source
3. Run the local entry script
4. Save to a new `.docx` path
5. Verify the output file exists
6. Tell the user the generated file path
7. Mention any likely manual review points, such as image paths, table layout, or final Word field refresh

## Quick Reference

| Situation | Recommended action |
|---|---|
| Only Markdown provided | Use `create_from_markdown(..., template_path=...)` |
| Existing DOCX defines target format | Add `format_docx_path=...` |
| User requests small local style tweaks | Pass `overrides={...}` |
| Markdown contains images | Keep relative paths valid from the Markdown/document context |
| Markdown contains references | Let pipeline generate bibliography and REF-related output |

## Common Mistakes

- Forgetting `template_path` when `format_docx_path` is used
- Overwriting the original document instead of writing a new `.docx`
- Using image paths that are not resolvable at conversion time
- Assuming Word fields are fully refreshed visually before opening the file in Word
- Skipping post-generation review for tables, figures, and bibliography formatting

## Output Guidance

After running the conversion, report:

- The generated `.docx` path
- Which formatting source was used
- Whether the Markdown included tables/images/references that may need manual visual review in Word
