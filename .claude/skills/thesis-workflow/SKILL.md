---
name: thesis-workflow
description: |
  Coordinates a thesis and academic deliverable workflow across specialized project skills.
  Use when the user asks for an end-to-end thesis workflow, is unsure which local skill to use,
  or wants to connect thesis writing, Markdown/DOCX production, standalone figure work, and PPT/defense materials.
---

# Thesis Workflow Coordinator

Coordinate thesis and academic deliverable work across specialized project skills. Keep this skill as a lightweight router and workflow index; do not duplicate the detailed instructions from downstream skills.

## When to Use

Use this skill when the user asks to:

- plan or manage an end-to-end thesis workflow;
- decide which project skill should handle a thesis, DOCX, standalone figure, or PPT-related request;
- move from thesis content to Word output, standalone figures, or presentation materials;
- coordinate writing, review, formatting, figures, and delivery steps.

Do not use this skill for a narrow task that clearly belongs to one specialized skill:

- Direct thesis writing, literature, humanization, or review tasks → use `bishe-guider`.
- Markdown-to-DOCX conversion, DOCX formatting, template configuration, or document build tasks → use `markdown2docx`.
- Standalone structure figures, architecture/module/model/network/workflow diagrams, SVG figures, or PPTX-carried figure pages → use `figure-builder`.
- Narrative PPT generation, slide outlines, speaker notes, SVG slide design for decks, cover/agenda/Q&A pages, or defense/report deck tasks → use `ppt-builder`, which uses local `ppt-master/skills/ppt-master` as the PPTX backend/tool source.

## Routing Rules

| User intent | Route to | Reason |
|---|---|---|
| Thesis topic, outline, chapter writing, academic style, literature, citations, blind-review checks | `bishe-guider` | Handles Chinese thesis writing and academic quality control |
| Markdown to DOCX, DOCX formatting, thesis template, captions, formulas, references, build commands | `markdown2docx` | Handles document production and Word formatting |
| Standalone structure figures, architecture/module/model/network/workflow diagrams, SVG figures, editable PPT figure pages, PPTX-carried figure pages | `figure-builder` | Handles figure-first diagrams where PPTX is an export carrier, not a presentation deck |
| Defense/report slides, presentation outline, speaker notes, cover/agenda/Q&A pages, narrative SVG slide design, PPT generation | `ppt-builder` | Handles personal-style narrative presentation production and uses local `ppt-master/skills/ppt-master` for SVG-first PPTX export |
| User wants the whole process or is unsure which skill applies | `thesis-workflow` first, then route | Clarify the stage and dispatch to the specialized skill |

## Routing Pressure Examples

Use these examples to keep ambiguous Chinese prompts on the intended route:

- `帮我写毕业论文第二章` → `bishe-guider`.
- `把这些 Markdown 转成论文 DOCX` → `markdown2docx`.
- `根据项目画模块结构图并导出 PPTX` → `figure-builder`; PPTX is only a figure carrier here.
- `画一个结构图/架构图/模块图/网络结构图/模型结构图/流程图并导出 SVG 或可编辑 PPT 图` → `figure-builder`.
- `做一份答辩 PPT，含封面目录和讲稿` → `ppt-builder`.

## End-to-End Workflow

Use this overview when the user wants a complete thesis delivery path:

1. Thesis planning
   - Clarify topic, research question, outline, chapter structure, and expected deliverables.
   - Route writing guidance to `bishe-guider`.

2. Literature and content drafting
   - Search, screen, cite, and summarize references.
   - Draft chapters and revise academic expression.
   - Route to `bishe-guider`.

3. Content refinement and review
   - Reduce AI-like writing traces, check logic, check blind-review compliance, and review figures/tables/citations.
   - Route to `bishe-guider`.

4. Document production
   - Convert Markdown to DOCX, apply thesis/report templates, format captions, formulas, references, headers, footers, and page layout.
   - Route to `markdown2docx`.

5. Figure and presentation production
   - Convert thesis/project content into standalone structure figures when the deliverable is an architecture/module/model/network/workflow diagram, SVG figure, editable PPT figure page, or PPTX-carried figure page.
   - Route standalone figures to `figure-builder`; PPTX output alone does not make a figure request a `ppt-builder` task.
   - Convert thesis content into defense or report slides, speaker notes, expected Q&A, cover/agenda pages, narrative SVG page designs, and `.pptx` output.
   - Route narrative presentation decks to `ppt-builder`; it uses local `ppt-master/skills/ppt-master` as the SVG-first PPTX backend/tool source.

6. Final delivery review
   - Check consistency across thesis content, DOCX formatting, figures, references, and slides.
   - Coordinate `bishe-guider`, `markdown2docx`, `figure-builder`, `ppt-builder`, and local `ppt-master/skills/ppt-master` for figure/deck PPTX generation.

## Operating Procedure

1. Identify the user's current stage: planning, writing, reviewing, document production, presentation production, or final delivery.
2. If the request maps cleanly to one specialized skill, invoke that skill directly.
3. If the request spans multiple stages, summarize the workflow and handle one stage at a time.
4. For standalone figure work, route to `figure-builder`; note that local `ppt-master/skills/ppt-master` is only the optional PPTX backend/tool source.
5. For presentation deck work, route to `ppt-builder`; note that local `ppt-master/skills/ppt-master` is the PPTX backend/tool source.
6. Keep responses concise and action-oriented.

## Boundaries

- Do not perform detailed thesis writing checks inside this coordinator; route to `bishe-guider`.
- Do not provide detailed DOCX CLI instructions inside this coordinator; route to `markdown2docx`.
- Do not duplicate detailed figure specifications, SVG constraints, or PPTX-carrier commands inside this coordinator; route standalone figure work to `figure-builder`.
- Do not duplicate detailed PPT prompts or backend commands inside this coordinator; route narrative presentation deck work to `ppt-builder`.
- Do not rename repository paths or Python packages as part of this skill.
