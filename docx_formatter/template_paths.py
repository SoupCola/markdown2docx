from __future__ import annotations

from pathlib import Path


_PACKAGE_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"


def resolve_template_path(template: str) -> Path:
    """Resolve a CLI/API template argument to a template file path."""
    path = Path(template)
    if path.is_absolute():
        return path

    candidate = _TEMPLATES_DIR / path.name
    if candidate.is_file():
        return candidate

    candidate = _TEMPLATES_DIR / f"{path.stem}.yaml"
    if candidate.is_file():
        return candidate

    return _TEMPLATES_DIR / path.name


def default_template_path() -> Path:
    return _TEMPLATES_DIR / "thesis.yaml"
