---
name: ppt-builder
description: |
  Builds personal-style presentation workflows from topics, research context, thesis/report content, or bullet points.
  Use for narrative decks, defense/report slides, PPT outlines, notes, cover/agenda/Q&A pages, and full presentation workflows.
  Do not use for standalone architecture/module/model/network/workflow figures, structure figures, or PPTX-carried figure pages; route those to figure-builder.
---

# PPT Builder

Create personal-style presentation deliverables: context-aware outline, slide plan, 1280×720 SVG page designs, speaker notes, and `.pptx` export through local `ppt-master/skills/ppt-master`.

## When to Use

Use this skill when the user asks to:

- generate a defense/report/business presentation from a topic, thesis, report, research context, or bullet points;
- create a PPT outline, slide structure, speaker notes, cover/agenda pages, or Q&A pages;
- design high-quality 1280×720 SVG slides with Bento Grid layouts;
- produce an operable `.pptx` for a narrative presentation deck, preferably native editable where SVG features allow.

Do not use this skill for standalone architecture/module/model/network/workflow figures, structure figures, editable PowerPoint figure pages, or PPTX-carried figures; use `figure-builder` instead. Also do not use it for thesis writing/literature review (`bishe-guider`) or Markdown/DOCX conversion (`markdown2docx`). For broad end-to-end routing, start from `thesis-workflow`.

## Operating Procedure

1. Collect topic, audience/scenario, page count, source content, background context, and visual constraints.
2. Use `references/outline-prompt.md` to produce a strict `[PPT_OUTLINE]...[/PPT_OUTLINE]` JSON outline.
3. Turn the outline into a per-slide content plan: title, core message, hierarchy, visual strategy, Bento card structure, and notes.
4. Use `references/svg-page-prompt.md` to generate one 1280×720 SVG per slide, following native-PPTX-friendly SVG constraints.
5. Use local `ppt-master/skills/ppt-master` as the backend/tool source for project setup, SVG finalization, and PPTX export.
6. Prefer native/default PPTX output. Use snapshot/legacy output only as a fallback when unsupported SVG features prevent native export.
7. Report final paths and whether the deck is native editable, snapshot, or mixed/fallback.

## References

- `references/workflow.md` — complete input-to-output workflow and reporting template.
- `references/outline-prompt.md` — Chinese PPT structure architect prompt with placeholders.
- `references/svg-page-prompt.md` — Chinese 1280×720 SVG Bento Grid prompt plus PPTX-friendly constraints.
- `references/ppt-master.md` — local backend path, commands, dependencies, output modes, license note, and risks.
