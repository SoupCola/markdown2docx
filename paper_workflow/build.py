"""Build commands for paper workflow."""

from pathlib import Path
from typing import Any

from docx_formatter import create_from_markdown
from docx_formatter.template_paths import resolve_template_path
from .figures import scan_figure_tasks, check_missing_figures


def _check_bishe_guider_available(project_root: Path) -> bool:
    """Check if bishe-guider skill is available."""
    # Check in .claude/skills/ directory
    skill_path = project_root / ".claude" / "skills" / "bishe-guider"
    if skill_path.is_dir():
        return True

    # Check in parent directory (for projects that share skills)
    parent_skill_path = project_root.parent / ".claude" / "skills" / "bishe-guider"
    if parent_skill_path.is_dir():
        return True

    return False


def _check_drawio_mcp_available() -> bool:
    """Check if DrawIO MCP is available."""
    # This is a placeholder - actual check would require MCP protocol
    return True


def _check_chapters_exist(config: dict[str, Any], project_root: Path) -> tuple[list[Path], list[str]]:
    """Check which chapters exist and return (existing, missing)."""
    content = config.get("content", {})
    chapters = content.get("chapters", [])

    existing: list[Path] = []
    missing: list[str] = []

    for chapter in chapters:
        chapter_path = project_root / chapter
        if chapter_path.is_file():
            existing.append(chapter_path)
        else:
            missing.append(chapter)

    return existing, missing


def build_docx(config: dict[str, Any], project_root: Path) -> Path:
    """Build DOCX from existing markdown/images/config."""
    fmt = config["format"]
    output_path = project_root / fmt["output_docx"]

    # Resolve template
    template = fmt.get("template")
    template_path = resolve_template_path(template) if template else None

    # Resolve reference docx
    format_docx_path = None
    if "reference_docx" in fmt:
        ref_path = project_root / fmt["reference_docx"]
        if ref_path.is_file():
            format_docx_path = ref_path

    # Collect markdown files
    content = config.get("content", {})
    md_paths: list[Path] = []

    for chapter in content.get("chapters", []):
        chapter_path = project_root / chapter
        if chapter_path.is_file():
            md_paths.append(chapter_path)

    if not md_paths:
        raise ValueError("No markdown chapters found")

    # Call docx_formatter
    result = create_from_markdown(
        output_path=output_path,
        md_paths=md_paths,
        format_docx_path=format_docx_path,
        template_path=template_path,
        overrides=fmt.get("overrides", {}),
    )

    return result


def full_build(config: dict[str, Any], project_root: Path) -> Path:
    """Strict orchestration: check upstream generators, then build DOCX."""
    workflow = config.get("workflow", {})
    figures_config = config.get("figures", {})
    content = config.get("content", {})

    # Step 1: Check figures
    print("Step 1: Checking figures...")
    md_paths = [project_root / ch for ch in content.get("chapters", [])]
    figures_dir = project_root / figures_config.get("output_dir", "assets/figures")

    figure_tasks = scan_figure_tasks(md_paths, figures_dir)
    missing_figures = check_missing_figures(figure_tasks)

    if figure_tasks:
        print(f"  Found {len(figure_tasks)} figure task(s), {len(missing_figures)} missing")
        if missing_figures:
            print("  [!!] Missing figures:")
            for task in missing_figures:
                print(f"    - {task.name}: {task.prompt}")
            if workflow.get("mode") == "strict":
                raise RuntimeError(
                    f"Missing {len(missing_figures)} figure(s). "
                    "Run 'make-figure' to see generation plan."
                )
    else:
        print("  No figure tasks declared")

    # Step 2: Check chapters
    print("Step 2: Checking chapters...")
    existing_chapters, missing_chapters = _check_chapters_exist(config, project_root)

    if existing_chapters:
        print(f"  [OK] Found {len(existing_chapters)} chapter(s)")
        for ch in existing_chapters:
            print(f"    - {ch.name}")

    if missing_chapters:
        print(f"  [!!] Missing {len(missing_chapters)} chapter(s):")
        for ch in missing_chapters:
            print(f"    - {ch}")
        if workflow.get("mode") == "strict":
            raise RuntimeError(
                f"Missing {len(missing_chapters)} chapter(s). "
                "Use bishe-guider to generate chapters first."
            )

    # Step 3: Check capabilities
    print("Step 3: Checking capabilities...")

    bishe_available = _check_bishe_guider_available(project_root)
    print(f"  [{'OK' if bishe_available else '!!'}] bishe-guider: {'available' if bishe_available else 'not found'}")

    if figures_config.get("generate_with"):
        drawio_available = _check_drawio_mcp_available()
        print(f"  [{'OK' if drawio_available else '!!'}] {figures_config['generate_with']}: {'available' if drawio_available else 'not available'}")

    # Step 4: Build DOCX
    print("Step 4: Building DOCX...")
    result = build_docx(config, project_root)
    print(f"  [OK] Built: {result}")

    return result
