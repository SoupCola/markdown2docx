# Local ppt-master Backend Reference for Figure Builder

`figure-builder` owns the figure concept, specification, and visual grammar. Local `ppt-master/skills/ppt-master` is only the backend/tool reference for inspecting PPTX/SVG samples, checking SVG compatibility, finalizing SVG, and exporting PPTX.

## Local backend path

Repo-relative:

```text
ppt-master/skills/ppt-master
```

Absolute in this checkout:

```text
/d/2026project/thesis_workflow/ppt-master/skills/ppt-master
```

Use the local copy already present in this repository. Do not clone upstream, vendor code into `.claude/skills/figure-builder`, or copy the full `ppt-master` workflow.

## Useful scripts

```bash
PPT_MASTER_SKILL="/d/2026project/thesis_workflow/ppt-master/skills/ppt-master"
```

Sample/source inspection:

```bash
python3 "$PPT_MASTER_SKILL/scripts/source_to_md/ppt_to_md.py" <source.pptx>
```

Project setup for native/editable PPTX carrier export:

```bash
python3 "$PPT_MASTER_SKILL/scripts/project_manager.py" init <project_name> --format <supported_format>
```

Choose `<supported_format>` from the local backend's supported canvas formats, not from the figure wish-list. Use `ppt169` only when the figure specification selects a 16:9 carrier.

SVG quality and export:

```bash
python3 "$PPT_MASTER_SKILL/scripts/svg_quality_checker.py" <project_path>
python3 "$PPT_MASTER_SKILL/scripts/finalize_svg.py" <project_path>
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path>
```

On Windows, use `python` instead of `python3` if needed. Do not install or change dependencies unless the user explicitly asks.

## Canvas and carrier boundary

- SVG-only figures may use custom figure-fit dimensions when the SVG `width`, `height`, and `viewBox` match.
- Native/editable PPTX carrier export through `project_manager.py init` should use a canvas format supported by the local backend project setup. Direct export may infer dimensions from SVG viewBox when no named format matches; validate this path before promising editability.
- Use `ppt169` only for a 16:9 figure carrier. For A4 landscape, wide, square, or other custom canvases, select a supported backend format only if it matches the figure intent; otherwise use matching SVG dimensions with explicit caveats, or provide SVG source rather than promising guaranteed native PPTX export.
- Backend examples include `ppt169`, `ppt43`, `wechat`, `xiaohongshu`, `moments`, `story`, `banner`, and `a4`, but verify against the local `CANVAS_FORMATS` before export. The current backend `a4` preset is portrait (`1240 x 1754`), so do not treat it as the A4 landscape figure preset.

## Layer boundary

```text
figure-builder: input/source analysis -> figure spec -> figure-fit SVG design -> figure validation
ppt-master: optional project shell -> SVG technical checks/finalization -> PPTX export
```

Do not import `ppt-master` presentation assumptions into figures:

- no outline JSON;
- no speaker notes;
- no cover/agenda/Q&A pages;
- no mandatory Bento Grid;
- no mandatory 1280 x 720 unless selected as a carrier canvas.

## SVG export expectations

Before final SVG generation or PPTX export, consult `ppt-master/skills/ppt-master/references/shared-standards.md` for the detailed SVG/PPTX constraints. For native/editable PPTX, prefer SVG primitives that map cleanly to PowerPoint:

- basic `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<path>`, `<polygon>`, and `<text>`;
- semantic top-level `<g id="...">` groups for stages, modules, connectors, and legend;
- inline attributes and HEX colors;
- supported `marker-start` / `marker-end` arrowheads, or standalone arrow polygons for chunky arrows;
- font-family stacks ending in installed fonts.

Avoid unsupported constructs: `<style>`, CSS `class`, `foreignObject`, masks, scripts, animations, `@font-face`, group opacity, `rgba(...)`, and vendor-specific Visio nodes.

## Output reporting

When PPTX export is used, report:

- SVG source path;
- PPTX export path;
- whether the output is native editable, snapshot, or mixed/fallback;
- any known caveat, such as custom canvas limitations, text reflow risk, unsupported effect fallback, or need for manual PowerPoint/WPS visual review.
