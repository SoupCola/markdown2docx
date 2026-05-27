# Figure Builder Workflow

This workflow turns source content, project/code structure, thesis model descriptions, or sample diagrams into one standalone technical figure or a small explicitly requested figure set. The default deliverable is a single high-density SVG figure; PPTX is an optional carrier/export format.

## 1. Confirm scope

Proceed when the artifact is a standalone figure:

- project/system architecture, module map, component relationship, or workflow diagram;
- thesis/model/network structure figure;
- Chinese requests such as `结构图`, `架构图`, `模块图`, `网络结构图`, `模型结构图`, or `流程图`;
- PPTX-carried figure page where the `.pptx` is used for editing/sharing the figure, including `可编辑 PPT 图` or `PPTX 承载的图`.

Route to `ppt-builder` when the request is a presentation deck: cover, agenda, section slides, narrative sequence, speaker notes, defense/report PPT, Q&A pages, or slide outline.

## 2. Collect inputs

Required:

- Figure type and purpose.
- Source material: text description, thesis excerpt, model/module list, code/package notes, or existing sample path.
- Desired output: SVG only, PPTX carrier, or both.
- Language of labels.

Useful options:

- Audience/context: paper figure, thesis defense handout, project documentation, engineering review.
- Canvas preference: 16:9 carrier, A4 landscape, wide architecture canvas, or custom size.
- Editability target: native PowerPoint shapes/text vs visual snapshot.
- Style sample path or style notes.

If the figure type is ambiguous, default to a thesis/model structure figure rather than a project architecture figure; ask only when the distinction changes the artifact.

If key structure is missing, ask concise questions. If moving quickly, state explicit assumptions and mark unknowns in the figure specification.

## 3. Produce a figure specification before SVG

Do not render directly from vague text. First write a compact figure spec:

```markdown
[FIGURE_SPEC]
Title/filename: <working name>
Purpose: <what the figure explains>
Canvas: <width x height, ratio, reason>
Macro regions/stages: <ordered named groups>
Module grammar:
  - <module type>: shape, color, label rule
  - <operation type>: node/symbol rule
Flow/connectors: <data/control direction, branch/merge rules>
Legend: <needed/not needed and entries>
Inputs/outputs: <left/top entry and right/bottom exit points>
Assumptions/unknowns: <only if any>
Output target: <SVG/PPTX/both; editability expectation>
[/FIGURE_SPEC]
```

Quality bar for the spec:

- Macro regions/stages are named, not just implied by placement.
- Repeated semantic modules share shape, size, fill, stroke, and typography.
- Connectors have explicit direction and avoid avoidable crossings.
- Operation nodes and legend entries are defined when symbols repeat.
- Canvas choice is justified by figure density, not inherited from slide defaults.

## 4. Choose a figure-fit canvas

Use the smallest canvas that preserves readability and export intent:

- `1280 x 720`: only when a 16:9 PPT carrier or presentation-compatible page is explicitly useful.
- `1240 x 877` or similar A4 landscape ratio: paper/thesis figures and balanced architecture diagrams.
- `1780 x 506`, `1920 x 540`, or similar wide canvas: long pipelines, neural/model architectures, or many stages.
- Custom dimensions are acceptable for SVG-only output if width, height, and viewBox match exactly.

For native/editable PPTX export, a PowerPoint page is still a page container. When using `project_manager.py init`, choose one of the backend-supported formats; note that the backend `a4` format is portrait, not A4 landscape. For A4 landscape, wide, or custom figure-fit canvases, use matching SVG `width`, `height`, and `viewBox`; if direct export infers custom dimensions, validate strictly and report the caveat instead of implying a built-in carrier preset. Keep the conceptual artifact as one figure page; do not add slide chrome or deck scaffolding.

## 5. Generate SVG

Before final SVG generation or PPTX export, consult `ppt-master/skills/ppt-master/references/shared-standards.md` for detailed SVG/PPTX constraints. Create one SVG per figure page. Follow these constraints:

- Include explicit `width`, `height`, matching `viewBox`, and a background `<rect>`.
- Use inline SVG attributes; no `<style>`, `class`, external CSS, `foreignObject`, masks, scripts, animation, or `@font-face`.
- Use semantic top-level groups such as `figure-background`, `stage-input`, `stage-backbone`, `connectors`, `legend`.
- Prefer rounded rectangles, feature-map/cube motifs, simple circles/ellipses for operations, dashed group boxes, and thin connector lines.
- Use HEX colors and per-element opacity attributes only when needed.
- Keep labels compact and centered; use multiline text sparingly.
- Use supported arrow markers or simple standalone arrow shapes.

Suggested file layout inside a local export project:

```text
<project_path>/svg_output/page_001.svg
```

Do not add notes files unless the user explicitly changed scope to a deck workflow.

## 6. Optional PPTX carrier export

When the user wants `.pptx`, use local `ppt-master/skills/ppt-master` as the backend/tool source. Treat export as a mechanical carrier step:

1. Place the SVG in `svg_output/`.
2. Run available SVG quality checks if the backend environment supports them.
3. Finalize SVG and export to PPTX with the local backend scripts.
4. Report whether the output is native editable, snapshot, or mixed/fallback.

Do not clone upstream, install dependencies, or copy `ppt-master` workflow/vendor code into this skill.

## 7. Validate and report

Before final response, check:

- The figure spec matches the generated figure.
- Macro regions/stages are visible and named.
- Repeated modules use consistent grammar.
- Connectors are legible and directionally clear.
- Labels are concise and readable.
- Canvas is figure-fit and not accidentally a generic slide.
- SVG avoids backend-hostile constructs.
- Output paths and editability caveats are reported.

Use this completion format:

```markdown
## Figure Build Complete

### Files Created

- SVG: `<absolute path>`
- PPTX: `<absolute path if any>`

### Figure Summary

- Type: <architecture/model/workflow/module figure>
- Canvas: <dimensions and reason>
- Structure: <macro regions/stages>

### Output Mode

- Mode: Native editable / SVG source / Snapshot / Mixed fallback
- Caveats: <known limitations or manual checks>
```
