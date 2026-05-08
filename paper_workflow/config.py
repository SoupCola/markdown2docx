"""Thesis config loading and validation."""

from pathlib import Path
from typing import Any

import yaml


def load_thesis_config(config_path: Path) -> dict[str, Any]:
    """Load thesis.config.yaml from the given path."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError(f"Config must be a YAML mapping, got {type(config).__name__}")

    return config


def validate_config(config: dict[str, Any], project_root: Path) -> list[str]:
    """Validate thesis config and return list of missing required files."""
    errors: list[str] = []

    # Required sections
    for section in ["project", "content", "format"]:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    if "content" in config:
        content = config["content"]
        if "chapters" in content:
            for chapter in content["chapters"]:
                chapter_path = project_root / chapter
                if not chapter_path.is_file():
                    errors.append(f"Chapter file not found: {chapter}")

    if "format" in config:
        fmt = config["format"]
        if "template" not in fmt:
            errors.append("Missing format.template")
        if "output_docx" not in fmt:
            errors.append("Missing format.output_docx")

    return errors


def get_content_generation_config(config: dict[str, Any]) -> dict[str, Any]:
    """Get content generation configuration from thesis config."""
    workflow = config.get("workflow", {})
    return workflow.get("content_generation", {})
