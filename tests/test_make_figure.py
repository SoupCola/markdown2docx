"""Tests for make-figure functionality."""

import pytest
from pathlib import Path

from paper_workflow.figures import scan_figure_tasks, check_missing_figures, emit_generation_plan, FigureTask


def test_scan_figure_tasks_basic(tmp_path):
    """Test scanning markdown for figure tasks."""
    md_content = """# Test

<!-- figure:prompt="系统架构图" -->
![架构图](assets/figures/architecture.png)

Some text here.

<!-- figure:prompt="数据流程图" -->
<!-- figure:drawio=dataflow.drawio -->
![数据流](assets/figures/dataflow.png)
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")

    figures_dir = tmp_path / "assets" / "figures"
    tasks = scan_figure_tasks([md_file], figures_dir)

    assert len(tasks) == 2
    assert tasks[0].name == "architecture"
    assert tasks[0].prompt == "系统架构图"
    assert tasks[0].drawio_source is None
    assert tasks[1].name == "dataflow"
    assert tasks[1].prompt == "数据流程图"
    assert tasks[1].drawio_source == "dataflow.drawio"


def test_scan_figure_tasks_no_tasks(tmp_path):
    """Test scanning markdown with no figure tasks."""
    md_content = """# Test

Just some text without figure declarations.

![image](image.png)
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")

    tasks = scan_figure_tasks([md_file], tmp_path)
    assert len(tasks) == 0


def test_check_missing_figures(tmp_path):
    """Test checking for missing figures."""
    # Create one existing figure
    existing = tmp_path / "existing.png"
    existing.write_text("fake image")

    tasks = [
        FigureTask(name="existing", prompt="test", output_path=existing),
        FigureTask(name="missing", prompt="test", output_path=tmp_path / "missing.png"),
    ]

    missing = check_missing_figures(tasks)
    assert len(missing) == 1
    assert missing[0].name == "missing"


def test_emit_generation_plan():
    """Test generation plan output."""
    tasks = [
        FigureTask(
            name="arch",
            prompt="系统架构图",
            drawio_source="arch.drawio",
            output_path=Path("/project/assets/figures/arch.png"),
            referenced_in=Path("/project/content/intro.md"),
        ),
    ]

    plan = emit_generation_plan(tasks)
    assert "系统架构图" in plan
    assert "arch.drawio" in plan
    assert "DrawIO MCP" in plan


def test_emit_generation_plan_empty():
    """Test generation plan with no missing figures."""
    plan = emit_generation_plan([])
    assert "All figures present" in plan
