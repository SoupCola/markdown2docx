# Local ppt-master Backend Reference

`ppt-builder` is a personal-style wrapper skill. It stores the user's outline/SVG prompts and workflow, while using the locally downloaded `ppt-master` package as the PPTX backend/tool source.

## Local backend path

```text
D:/2026project/thesis_workflow/ppt-master/skills/ppt-master
```

Repo-relative path:

```text
ppt-master/skills/ppt-master
```

## Upstream and license

- Upstream repository: <https://github.com/hugohe3/ppt-master.git>
- License: MIT License, copyright 2025-2026 Hugo He.
- Version 1 of `ppt-builder` does not copy/vendor the full upstream code into `.claude/skills/ppt-builder`.
- If future work copies or adapts substantial upstream code or skill content, preserve the MIT license notice and copyright.

## Pipeline shape

`ppt-master` is SVG-first:

```text
source content → Markdown normalization → project init/import → SVG authoring → SVG finalization → PPTX export
```

For `ppt-builder`, the intended layer split is:

```text
ppt-builder: topic/context → outline JSON → slide content plan → personal-style SVG prompt
ppt-master: project structure → SVG finalization/checking → SVG-to-PPTX export
```

## Recommended local command path

Set a local variable when running commands manually:

```bash
PPT_MASTER_SKILL="D:/2026project/thesis_workflow/ppt-master/skills/ppt-master"
```

Common commands:

```bash
python3 "$PPT_MASTER_SKILL/scripts/project_manager.py" init <project_name> --format ppt169
python3 "$PPT_MASTER_SKILL/scripts/project_manager.py" import-sources <project_path> <source_files...> --move
python3 "$PPT_MASTER_SKILL/scripts/total_md_split.py" <project_path>
python3 "$PPT_MASTER_SKILL/scripts/finalize_svg.py" <project_path>
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path>
```

On Windows, if `python3` is unavailable, use `python` with the same script paths.

## Output modes

- **Native/default**: primary target. Converts supported SVG primitives/text to native PowerPoint DrawingML shapes/text. Best for editable PPTX.
- **`--merge-paragraphs`**: editability-first text mode for long body copy; may change line wrapping compared with the SVG.
- **`--svg-snapshot`**: additionally emits an SVG/PNG snapshot PPTX for visual reference; less editable.
- **`--only legacy`**: legacy image-based output; use only as fallback/reference when native conversion is not viable.
- **`--only native`**: native DrawingML path only, useful for strict editable-output checks.

When reporting final output, explicitly say whether the deck is native editable, snapshot, or mixed/fallback. Do not promise that every visual effect is editable.

## Dependencies by capability

Minimal/native PPTX export:

- Python runtime
- `python-pptx>=0.6.21`
- `ppt-master/skills/ppt-master/scripts/` standard-library tooling

Source conversion:

- PDF: `PyMuPDF`
- DOCX/HTML/EPUB/IPYNB: `mammoth`, `markdownify`, `ebooklib`, `nbconvert`
- Excel: `openpyxl`
- Web: `requests`, `beautifulsoup4`, optional `curl_cffi`
- Less common document formats may require `pandoc`

Snapshot/compatibility paths:

- CairoSVG preferred, or `svglib` + `reportlab`

Optional features:

- Image processing: `Pillow`, `numpy`
- AI image generation: provider packages/API credentials such as `google-genai` or OpenAI-compatible HTTP settings
- Narration: `edge-tts`, audio tooling, and `ffprobe` for duration probing
- SVG editor/live tooling: `flask`

Do not install or change dependencies unless the user explicitly requests it.

## Native-friendly SVG guidance

The local `ppt-master/skills/ppt-master/references/shared-standards.md` is the authority for detailed constraints. In `ppt-builder` prompts, prefer:

- 1280×720 canvas for 16:9 PPT: `viewBox="0 0 1280 720"`.
- Basic shapes, direct text, and explicit inline SVG attributes.
- Top-level semantic `<g id="...">` groups.
- XML-safe text and attributes.
- Fonts ending in common installed font families.

Avoid:

- `<style>`, CSS classes, external CSS.
- `<foreignObject>`, `<symbol>/<use>`, `textPath`, `@font-face`.
- SVG animation, scripts, event handlers, iframes.
- `mask`, group opacity, image opacity, and `rgba(...)`.
- Unsupported or visually complex effects when native editability is required.

## Risks

- Native SVG-to-PPTX conversion is strict. Unsupported SVG features can fail export rather than being silently rasterized.
- Snapshot/legacy output is visually useful but not equivalent to fully editable PowerPoint shapes.
- Text editability and exact SVG line layout can conflict; use `--merge-paragraphs` when editing long paragraphs matters more than exact line breaks.
- Local commands depend on `ppt-master/` staying in this repository. If the directory moves, update this reference and `thesis-workflow` routing notes.
- Upstream can change over time. Version 1 treats local `ppt-master/skills/ppt-master` as the current backend rather than cloning/downloading anything.
