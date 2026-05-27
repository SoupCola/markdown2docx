# Figure Style Reference

Use this reference for standalone structure figures. It preserves the learned style from the sample PPTX/SVG figures while avoiding presentation-deck drift.

## Core visual grammar

A strong figure uses three hierarchy levels:

1. Macro regions/stages: named containers such as Input, Hardware Platform, Sensor Information, Feature Extraction, Backbone, Fusion, Temporal Refinement, Neck, Head, Prediction Output.
2. Modules: repeated rounded rectangles, feature-map/cube blocks, stacks, or small panels inside each region.
3. Operations/connectors: small nodes and arrows that explain fusion, addition, multiplication, concatenation, convolution, alignment, or output flow.

Default flow is left-to-right for pipelines and architecture figures, with vertical stacks inside each stage. Use top-to-bottom only when the process is naturally sequential or the target canvas is narrow.

## Structure hierarchy rules

- Every figure should expose named macro regions or stages.
- Group boundaries should be visible through light tinted containers, dashed boxes, braces, or stage headers.
- Repeated modules must share shape, fill, stroke, size, and label style.
- Dense figures are acceptable when segmented; do not create free-floating blocks without grouping.
- If the diagram has repeated symbols, include a compact legend row or side legend.

## Module grammar

Recommended shape meanings:

- Rounded rectangle: module, layer, service, component, algorithm block.
- Feature-map/cube stack: tensor, feature, channel map, neural-network intermediate.
- Circle/ellipse: operation node such as `+`, `×`, `·`, `C`, concat, gate, or decision.
- Dashed container: optional branch, repeated pattern, attention/alignment sub-region, or auxiliary module.
- Thin connector arrow: data/control flow.
- Standalone block arrow/chevron: major phase transition only; avoid overuse.

Keep operation labels compact. Prefer symbols on nodes over long connector prose.

## Color system

Use muted Office/Visio-like semantic colors. Color encodes region or module type, not decoration.

Useful palette families:

- Blue: `#4472C4`, `#5B9BD5`, `#9CC3E5`, `#BDE0FB`
- Green: `#70AD47`, `#A9D18E`, `#C5E0B3`, `#E2EFD9`
- Orange/peach: `#ED7D31`, `#F4B183`, `#F7CBAC`, `#FBE5D6`
- Yellow: `#FFC000`, `#FEE599`, `#FFF2CC`
- Gray: `#A5A5A5`, `#D9D9D9`, `#F2F2F2`
- Purple: `#8064A2`, `#B4A7D6`, `#BEA7D0`

Use light fills with darker strokes for containers and stronger fills for important modules. Avoid saturated rainbow palettes, decorative gradients, and brand-only color schemes unless the user provides one.

## Typography

- Chinese labels: use a stack ending in `Microsoft YaHei`, `SimSun`, or `SimHei`.
- English/math-heavy labels: use a stack ending in `Arial`, `Times New Roman`, or another common installed font.
- Keep labels short, centered, and noun-heavy: module names, operation names, tensor dimensions, or stage titles.
- Avoid prose paragraphs inside figures. Move explanations to captions or surrounding text.
- Use 2-3 text levels: stage title, module label, small dimension/operator label.

## Connectors and spacing

- Use thin black or semantic-color connectors with simple arrowheads.
- Route flow orthogonally where possible; diagonal connectors are acceptable when they reduce crossings.
- Keep connector crossings rare and intentional.
- Place operation nodes directly on flow paths.
- Use strict grid alignment: same-size repeated blocks, aligned columns, consistent row gaps.
- Macro spacing between stages should be larger than micro spacing inside a stage.

## Canvas behavior

Do not inherit presentation defaults automatically.

- Use 16:9 only when the PPT carrier or user context calls for it.
- Use A4 landscape for paper/thesis-style balanced diagrams.
- Use wide canvases for long model/network pipelines.
- Fit the canvas to the figure density while preserving readable labels.

## Backend-friendly SVG constraints

Sample Visio SVGs are visual references only. Do not copy their exported markup.

Generated SVG should use:

- explicit `width`, `height`, and matching `viewBox`;
- a background rectangle;
- inline attributes only;
- HEX colors;
- semantic top-level `<g id="...">` groups;
- basic shapes, direct text, and supported marker arrows.

Avoid:

- `<style>`, `class`, external CSS;
- `foreignObject`, masks, scripts, animation, `@font-face`;
- group opacity, image opacity, `rgba(...)`;
- vendor-specific Visio extension nodes;
- decorative slide artifacts such as title bars, page numbers, agenda sections, or speaker-note logic.

## Anti-drift checklist

Before rendering or reporting, confirm:

- The artifact is a figure, not a deck.
- There is no cover/agenda/conclusion/Q&A page by default.
- The canvas was selected for figure fit, not forced 16:9/Bento.
- The style is technical Office/Visio structure style, not generic slide polish.
- The figure contains named regions, repeated module grammar, operation nodes, clean connectors, and compact labels.
