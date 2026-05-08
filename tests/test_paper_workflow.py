"""Tests for paper_workflow module."""

import pytest
import yaml
from pathlib import Path

from paper_workflow.config import load_thesis_config, validate_config
from paper_workflow.build import build_docx


def test_load_thesis_config(tmp_path):
    """Test loading thesis config from YAML file."""
    config_content = {
        "project": {"title": "Test", "language": "zh-CN"},
        "content": {"chapters": ["test.md"]},
        "format": {"template": "thesis", "output_docx": "output.docx"},
    }
    config_path = tmp_path / "thesis.config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    loaded = load_thesis_config(config_path)
    assert loaded["project"]["title"] == "Test"


def test_load_thesis_config_missing_file(tmp_path):
    """Test loading non-existent config file raises error."""
    config_path = tmp_path / "thesis.config.yaml"
    with pytest.raises(FileNotFoundError):
        load_thesis_config(config_path)


def test_validate_config_valid(tmp_path):
    """Test validation of valid config."""
    config_content = {
        "project": {"title": "Test", "language": "zh-CN"},
        "content": {"chapters": ["test.md"]},
        "format": {"template": "thesis", "output_docx": "output.docx"},
    }
    # Create the chapter file
    (tmp_path / "test.md").write_text("# Test")

    errors = validate_config(config_content, tmp_path)
    assert errors == []


def test_validate_config_missing_chapters(tmp_path):
    """Test validation catches missing chapter files."""
    config_content = {
        "project": {"title": "Test", "language": "zh-CN"},
        "content": {"chapters": ["test.md"]},
        "format": {"template": "thesis", "output_docx": "output.docx"},
    }
    errors = validate_config(config_content, tmp_path)
    assert any("not found" in e for e in errors)


def test_build_docx_integration(tmp_path):
    """Integration test for build-docx."""
    # Create config
    config_content = {
        "project": {"title": "Test", "language": "zh-CN"},
        "content": {"chapters": ["test.md"]},
        "format": {"template": "thesis", "output_docx": "output.docx"},
    }
    config_path = tmp_path / "thesis.config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    # Create chapter
    (tmp_path / "test.md").write_text("# Test Title\n\nTest content")

    config = load_thesis_config(config_path)
    result = build_docx(config, tmp_path)
    assert result.exists()
    assert result.suffix == ".docx"
