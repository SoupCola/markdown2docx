# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

This project treats local Claude skills under `.claude/skills/` as executable workflow contracts when they route project work or define repeatable document/build behavior. Skill changes should keep routing boundaries explicit, preserve referenced backend constraints, and remain trackable in git when they affect project behavior.

---

## Forbidden Patterns

### Don't: Let broad skill triggers compete silently

**Problem**: A broad skill description such as “PPTX generation” can capture requests that belong to a more specific skill, such as standalone figure generation.

**Why it's bad**: Future agents may route work to the nearest broad workflow and inherit wrong assumptions, such as narrative decks, 16:9 slides, speaker notes, or Bento layouts.

**Instead**: Update both sides of the boundary. The specialized skill should state its positive triggers, and the broader neighboring skill should state the negative boundary and route to the specialized skill.

```text
Wrong: ppt-builder handles all PPTX output.
Correct: ppt-builder handles narrative decks; figure-builder handles standalone structure figures and PPTX-carried figure pages.
```

### Don't: Ignore routing-critical local skills

**Problem**: Ignoring all of `.claude/` can hide project-specific skills from git even when they define workflow behavior.

**Why it's bad**: A new skill may work in one local session but disappear for future sessions or collaborators.

**Instead**: Keep local state ignored, but unignore routing-critical skill directories/files that are part of the project contract.

---

## Required Patterns

### Local skill routing boundary updates

**What**: When adding or changing a local skill that overlaps an existing skill, update all affected skill descriptions and coordinator routing tables.

**Why**: Skill selection is metadata-driven. Positive triggers in the new skill are not enough if an older skill still advertises the same broad intent.

**Example**:

```text
figure-builder:
  Use for standalone structure figures, architecture/module/model/network/workflow figures, and PPTX-carried figure pages.

ppt-builder:
  Use for narrative decks and full presentation workflows.
  Do not use for standalone structure figures; route those to figure-builder.

thesis-workflow:
  Route figure pages to figure-builder and defense/report decks to ppt-builder.
```

### Backend constraint references

**What**: Wrapper skills that use local backend tools should link to the backend's authoritative constraint file before generation/export.

**Why**: Copying a short subset of backend rules drifts over time and misses edge cases.

**Example**:

```text
Before final SVG generation or PPTX export, consult:
ppt-master/skills/ppt-master/references/shared-standards.md
```

### Mixed-canvas figure PPTX carriers

**What**: When a standalone figure set mixes canvas sizes or ratios, export one PPTX carrier per figure unless the backend is explicitly validated to preserve each page's canvas.

**Why**: A combined PPTX export may infer all slide dimensions from the first SVG and distort wide or custom-canvas figures.

**Example**:

```text
Wrong: Export 1240x877 and 1780x560 figures into one PPTX and assume every slide keeps its source canvas.
Correct: Export per-figure PPTX carriers, then report any combined export as secondary/validation-only if canvases differ.
```

### SVG marker color consistency

**What**: Arrow markers should match the connector stroke color for every semantic connector family.

**Why**: Reusing a gray marker on a green or orange connector creates visual inconsistency and can make exported PowerPoint shapes harder to inspect.

**Example**:

```text
Wrong: stroke="#70AD47" marker-end="url(#arrowGray)".
Correct: stroke="#70AD47" marker-end="url(#arrowGreen)" with marker fill="#70AD47".
```

---

## Testing Requirements

<!-- What level of testing is expected -->

(To be filled by the team)

---

## Code Review Checklist

<!-- What reviewers should check -->

(To be filled by the team)
