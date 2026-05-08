"""Figure task scanning and missing figure checking."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FigureTask:
    """A figure generation task declared in markdown."""

    name: str
    prompt: str
    drawio_source: str | None = None
    output_path: Path | None = None
    referenced_in: Path | None = None


# Pattern to match <!-- figure:key="value" --> or <!-- figure:key=value -->
_PROMPT_RE = re.compile(r'<!--\s*figure:prompt="([^"]+)"\s*-->')
_DRAWIO_RE = re.compile(r'<!--\s*figure:drawio=(\S+)\s*-->')
_IMG_RE = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')


def scan_figure_tasks(md_paths: list[Path], figures_dir: Path) -> list[FigureTask]:
    """Scan markdown files for figure generation tasks.

    Looks for blocks containing:
        <!-- figure:prompt="description" -->
        <!-- figure:drawio=source.drawio -->   (optional)
        ![alt](path/to/figure.png)

    Args:
        md_paths: Markdown files to scan.
        figures_dir: Base directory for figure outputs.

    Returns:
        List of FigureTask found in the markdown files.
    """
    tasks: list[FigureTask] = []

    for md_path in md_paths:
        if not md_path.is_file():
            continue

        content = md_path.read_text(encoding="utf-8")

        for block in content.split("\n\n"):
            prompt_match = _PROMPT_RE.search(block)
            if not prompt_match:
                continue

            img_match = _IMG_RE.search(block)
            if not img_match:
                continue

            prompt = prompt_match.group(1)
            img_ref = img_match.group(1)

            # Resolve image path relative to markdown file
            img_path = (md_path.parent / img_ref).resolve()
            name = img_path.stem

            # Optional drawio source
            drawio_match = _DRAWIO_RE.search(block)
            drawio_source = drawio_match.group(1) if drawio_match else None

            tasks.append(
                FigureTask(
                    name=name,
                    prompt=prompt,
                    drawio_source=drawio_source,
                    output_path=img_path,
                    referenced_in=md_path,
                )
            )

    return tasks


def check_missing_figures(tasks: list[FigureTask]) -> list[FigureTask]:
    """Return tasks whose output file does not exist."""
    return [t for t in tasks if t.output_path and not t.output_path.is_file()]


def emit_generation_plan(missing: list[FigureTask]) -> str:
    """Generate a human/AI-readable plan for creating missing figures."""
    if not missing:
        return "All figures present."

    lines: list[str] = []
    lines.append("## Missing Figures - Generation Plan\n")
    lines.append(f"Found {len(missing)} missing figure(s):\n")

    for i, task in enumerate(missing, 1):
        lines.append(f"### {i}. {task.name}")
        lines.append(f"- **Prompt**: {task.prompt}")
        lines.append(f"- **Output**: `{task.output_path}`")
        if task.drawio_source:
            lines.append(f"- **DrawIO source**: `{task.drawio_source}`")
        if task.referenced_in:
            lines.append(f"- **Referenced in**: `{task.referenced_in}`")
        lines.append("")

    lines.append("---")
    lines.append("### How to generate")
    lines.append("For each figure above:")
    lines.append("1. Use DrawIO MCP tool with the given prompt")
    lines.append("2. Save the .drawio source to `assets/drawio/`")
    lines.append("3. Export .png to the output path listed above")
    lines.append("4. Re-run `paper-workflow build-docx`")

    return "\n".join(lines)
