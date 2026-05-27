# ppt-builder Workflow

This workflow turns a topic, research context, thesis/report material, or bullet points into a presentation outline, slide plan, SVG pages, and final `.pptx` output through local `ppt-master/skills/ppt-master`.

## 1. Collect inputs

Required:

- PPT topic or working title.
- Page count or page range.
- Source content: thesis excerpt, report, Markdown, PDF/DOCX-derived text, bullet points, or conversation material.
- Background research context if available.

Optional but useful:

- Scenario: defense, class report, project review, business pitch, meeting, training.
- Audience: supervisor, committee, classmates, stakeholders, customers.
- Language and tone.
- Visual style: colors, logo, brand, academic/business/minimal, template path if explicitly provided.
- Desired output: outline only, SVG pages, PPTX, speaker notes, Q&A pages, snapshot fallback.

If required information is missing, ask concise follow-up questions. If the user wants quick progress, proceed with explicit assumptions and list them.

## 2. Generate the PPT outline

Use `references/outline-prompt.md` with these placeholders filled:

- `{{TOPIC}}`
- `{{CONTEXT}}`
- `{{PAGE_REQUIREMENT}}`
- `{{SOURCE_CONTENT}}`
- `{{SCENARIO}}`
- `{{AUDIENCE}}`

Output must be wrapped exactly:

```text
[PPT_OUTLINE]
{...valid JSON...}
[/PPT_OUTLINE]
```

Quality checks:

- Page count matches the requirement.
- The whole deck has one core message.
- Each page has one core message, not just a topic label.
- Page order follows a clear logic chain.
- Context/evidence fields do not invent facts.

## 3. Convert outline to slide content plan

For each slide, derive a concise implementation plan:

- page number and title;
- core message;
- content hierarchy;
- 1–5 key points;
- evidence or source snippets;
- visual strategy;
- Bento Grid card count and relative card sizes;
- suggested top-level SVG group names;
- optional speaker notes.

Recommended page patterns:

- Cover: title, subtitle, author/context, restrained visual hook.
- Agenda/structure: high-level roadmap.
- Section divider: one short statement and visual transition.
- Content: Bento Grid with one primary card and supporting cards.
- Data: large metric cards, chart, annotation callouts.
- Comparison: two-column/2×2 cards, clear labels.
- Process: horizontal timeline or step cards.
- Conclusion: concise takeaway and next action.
- Q&A: anticipated questions or defense backup pages.

## 4. Generate SVG pages

Use `references/svg-page-prompt.md` for each slide.

Hard constraints:

- One complete SVG per slide.
- `width="1280" height="720" viewBox="0 0 1280 720"`.
- Background rectangle included.
- Content pages use Bento Grid when appropriate.
- Preserve spacing, alignment, hierarchy, and readability.
- Avoid unsupported SVG features listed in `references/svg-page-prompt.md` and local `ppt-master/skills/ppt-master/references/shared-standards.md`.

Suggested file placement in a `ppt-master` project:

```text
<project_path>/svg_output/page_001.svg
<project_path>/svg_output/page_002.svg
...
<project_path>/notes/total.md
```

Do not batch-generate SVG by script unless the user explicitly changes the workflow. Page quality depends on per-page design decisions.

## 5. Prepare or use a local ppt-master project

The local backend path is:

```text
D:/2026project/thesis_workflow/ppt-master/skills/ppt-master
```

Recommended variable:

```bash
PPT_MASTER_SKILL="D:/2026project/thesis_workflow/ppt-master/skills/ppt-master"
```

Initialize a project if needed:

```bash
python3 "$PPT_MASTER_SKILL/scripts/project_manager.py" init <project_name> --format ppt169
```

If source files must be imported:

```bash
python3 "$PPT_MASTER_SKILL/scripts/project_manager.py" import-sources <project_path> <source_files...> --move
```

Do not clone or download upstream during this workflow. Use the local `ppt-master/` directory already present in the repository.

## 6. Speaker notes

If the deck includes notes, write a complete notes document before splitting:

```text
<project_path>/notes/total.md
```

Then run:

```bash
python3 "$PPT_MASTER_SKILL/scripts/total_md_split.py" <project_path>
```

If no notes are requested, skip note generation or keep notes minimal.

## 7. Finalize SVG and export PPTX

Run in order:

```bash
python3 "$PPT_MASTER_SKILL/scripts/finalize_svg.py" <project_path>
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path>
```

Primary target:

- Native/default PPTX, with supported SVG primitives/text converted to editable DrawingML shapes/text.

Useful variants:

```bash
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path> --merge-paragraphs
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path> --svg-snapshot
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path> --only native
python3 "$PPT_MASTER_SKILL/scripts/svg_to_pptx.py" <project_path> --only legacy
```

Use variants intentionally:

- `--merge-paragraphs`: when paragraph editability matters more than exact SVG line breaks.
- `--svg-snapshot`: when a visual-reference snapshot deck is useful alongside the native deck.
- `--only native`: strict native test.
- `--only legacy`: fallback/reference only.

## 8. Verify outputs

Light checks after export:

- Confirm `.pptx` file exists under the project's export/output location.
- Confirm no native export error was reported.
- If snapshot fallback was used, record why.
- If possible, ask the user to open the deck in PowerPoint/WPS and confirm visual fidelity and editability.

## 9. Final report template

Use this structure when reporting completion:

```markdown
## PPT Build Complete

### Inputs Used

- Topic: <topic>
- Scenario/Audience: <scenario and audience>
- Page count: <count>

### Files Created

- Outline: `<absolute path or conversation output>`
- SVG pages: `<absolute project svg path>`
- PPTX: `<absolute pptx path>`

### Output Mode

- Mode: Native editable / Snapshot / Mixed fallback
- Editability note: <what should remain editable, and any known limitations>

### Summary

1. Generated pyramid-principle outline.
2. Designed slide content plan and Bento Grid SVG pages.
3. Finalized SVG and exported PPTX through local `ppt-master/skills/ppt-master`.

### Caveats / Next Steps

- <missing info, unsupported effects, recommended manual review, or next refinements>
```
