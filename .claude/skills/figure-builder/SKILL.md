---
name: figure-builder
description: |
  Use for standalone structure figures: architecture/module/model/network/workflow figures; 结构图, 架构图, 模块图, 网络结构图, 模型结构图, 流程图; 可编辑 PPT 图 or PPTX 承载的图.
  Builds figure-first SVG/PPTX artifacts with named regions, module grammar, clean connectors, and Office/Visio-like technical styling.
  Do not use for full narrative decks, defense/report PPTs, slide outlines, notes, cover/agenda/Q&A pages, or full presentation workflows; route those to ppt-builder.
---

# Figure Builder

Create standalone technical figures as image-like visual artifacts. A `.pptx` may be produced, but it is a carrier/export format for one or a small number of figure pages, not a presentation deck workflow.

## When to Use

Use this skill when the user asks to create, learn, revise, or export:

- architecture diagrams, system structure diagrams, project module maps, or component dependency figures;
- thesis/model structure figures, neural-network diagrams, data-flow/model-flow diagrams, or network architecture figures;
- workflow/process figures where the deliverable is a standalone diagram, not a slide sequence;
- PPTX-carried figure outputs, editable PowerPoint figure pages, or SVG figures intended for PPTX export;
- Chinese figure requests such as `结构图`, `架构图`, `模块图`, `网络结构图`, `模型结构图`, `流程图`, `可编辑 PPT 图`, or `PPTX 承载的图`;
- style extraction from structure-figure samples such as Visio/PPTX/SVG diagrams.

Routing examples: `画一个模型结构图并导出可编辑 PPT` -> `figure-builder`; `把系统模块画成 PPTX 承载的图` -> `figure-builder`; `做一份答辩 PPT，含封面目录和讲稿` -> `ppt-builder`.

Do not use this skill for full presentation production. If the user asks for defense slides, report decks, slide outlines, speaker notes, cover/agenda/conclusion/Q&A pages, or a narrative sequence of slides, use `ppt-builder` instead.

## Operating Procedure

1. Confirm the artifact is a figure, not a deck. If the request mixes both, separate the standalone figure work from the presentation work.
2. Collect the minimum inputs: figure purpose, source content/code/model description, intended audience/context, output format, language, and any sample/style constraints.
3. If the request is ambiguous, default to a thesis/model structure figure rather than a project architecture figure; ask only when the distinction changes the artifact.
4. Read `references/workflow.md` and produce an intermediate figure specification before rendering. Do not jump straight to a generic slide.
5. Apply `references/figure-style.md`: named macro regions/stages, consistent module grammar, semantic muted colors, compact labels, operation nodes, clean connectors, optional legend row, and figure-fit canvas selection.
6. Before final SVG generation or PPTX export, consult `ppt-master/skills/ppt-master/references/shared-standards.md` for detailed SVG/PPTX constraints.
7. Generate backend-friendly SVG when an editable `.pptx` is desired: inline attributes, explicit canvas/background, semantic `<g id="...">` groups, supported markers, and no CSS/classes/foreignObject/masks.
8. Use `references/ppt-master.md` only for local backend/tool commands and SVG/PPTX constraints. Do not copy the full `ppt-master` workflow or vendor upstream code into this skill.
9. Validate the figure against the specification: hierarchy, alignment, repeated module consistency, connector readability, label compactness, output paths, and PPTX export/editability notes.

## Drift Guards

- PPTX request does not imply `ppt-builder`; standalone structure figures stay here.
- Do not add cover pages, agenda pages, speaker notes, slide outline JSON, defense Q&A, or presentation narration unless the user explicitly switches to `ppt-builder` scope.
- Do not force 16:9 or Bento Grid layouts. Choose a figure-fit canvas: 16:9 carrier, A4 landscape, wide architecture canvas, or custom dimensions as appropriate.
- Do not treat sample figures as chat-only inspiration. Extract reusable grammar and persist/use it through the references.
- Do not copy Visio-exported SVG markup with `<style>`, classes, masks, or vendor extension nodes. Rebuild clean SVG primitives.

## References

- `references/workflow.md` — figure-first workflow, input checklist, figure specification, generation and validation steps.
- `references/figure-style.md` — sample-derived structure-figure style grammar and anti-drift rules.
- `references/ppt-master.md` — local backend/tool reference for sample inspection, SVG validation, and PPTX export.
