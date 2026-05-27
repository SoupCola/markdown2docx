---
name: markdown2docx
description: |
  Converts Markdown files to formatted DOCX files and re-formats existing DOCX files with configurable templates.
  Use for Chinese thesis, academic paper, and report document production, including page layout, headings,
  body text, figure/table captions, formulas, references, and DOCX build workflows.
---

# Markdown to DOCX Formatter

Convert Markdown to formatted DOCX, or re-format an existing DOCX document using local templates and overrides.

## When to Use

Use this skill when the user asks to:

- convert one or more Markdown files into a DOCX;
- format or re-format an existing DOCX;
- apply thesis, academic paper, or report templates;
- configure margins, headings, body text, captions, formulas, references, headers, footers, or page numbers;
- run a config-driven thesis document build.

Do not use this skill for thesis content creation, literature search, academic writing review, reducing AI-like writing traces, standalone structure figures, SVG figures, or PPTX-carried figure pages. Route writing requests to `bishe-guider`, figure-first requests to `figure-builder`, or start from `thesis-workflow` when the user needs the full workflow.

## Primary CLI Commands

```bash
# Convert markdown to docx
python -m docx_formatter convert chapter1.md chapter2.md -o paper.docx -t thesis
python -m docx_formatter convert *.md -o paper.docx -t thesis --override body.size=小四
python -m docx_formatter convert draft.md -o paper.docx -t thesis --format-docx reference.docx

# Format existing docx
python -m docx_formatter format draft.docx -t thesis

# Installed script entry
docx-format convert chapter1.md -o paper.docx -t thesis

# Config-driven thesis document workflow
python -m paper_workflow build-docx -c thesis.config.yaml -r /path/to/project
python -m paper_workflow full-build -c thesis.config.yaml -r /path/to/project
# Legacy/configured asset pipeline only; do not use for new standalone structure figures.
# Route new architecture/module/model/network/workflow diagrams, SVG figures, or PPTX-carried figure pages to figure-builder.
python -m paper_workflow make-figure -c thesis.config.yaml -r /path/to/project
```

For longer workflow examples, read `references/workflow.md`.

## Available Templates

| Template | File | Description |
|---|---|---|
| thesis | `templates/thesis.yaml` | Chinese thesis formatting |
| academic_paper | `templates/academic_paper.yaml` | Academic paper formatting |
| report | `templates/report.yaml` | General report formatting |

`--template` accepts either an absolute YAML path or one of the bundled template names.

## Key Features

- Heading formatting for multiple levels.
- Body text with first-line indent and line spacing.
- Figure and table caption numbering.
- Formula rendering and numbering.
- Bibliography and cross-reference support.
- Page layout including margins, headers, footers, and page numbers.
- Format extraction from existing DOCX via `--format-docx`.

## Operating Procedure

1. Identify whether the input is Markdown, an existing DOCX, or a thesis project config.
2. Confirm the output path and template name or template file.
3. Confirm local formatting overrides if the user requested them.
4. Run the relevant CLI command or explain the command if the user only wants guidance.
5. Report the generated or formatted DOCX path.

## Handoffs

- If the user needs thesis writing, literature search, academic style revision, or final thesis quality review, use `bishe-guider`.
- If the user asks for standalone structure figures, architecture/module/model/network/workflow diagrams, SVG figures, editable PowerPoint figure pages, or PPTX-carried figure outputs, route to `figure-builder`.
- If the user wants an end-to-end thesis delivery path that includes writing, DOCX, figures, and PPT, start from `thesis-workflow`.
- If the user asks for narrative slides, slide outlines, speaker notes, cover/agenda/Q&A pages, or defense/report deck materials, route to `ppt-builder`, which uses local `ppt-master/skills/ppt-master` as the PPTX backend/tool source.
