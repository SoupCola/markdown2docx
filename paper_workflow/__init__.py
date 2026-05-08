"""Paper workflow orchestration layer.

Provides lightweight coordination for thesis document assembly:
- build-docx: consume existing markdown/images/config for final DOCX build
- full-build: strict orchestration of upstream generators then final build
- make-figure: scan markdown for figure tasks and report missing figures
"""

from .config import load_thesis_config, validate_config
from .build import build_docx, full_build
from .figures import scan_figure_tasks, check_missing_figures, emit_generation_plan

__all__ = [
    "load_thesis_config",
    "validate_config",
    "build_docx",
    "full_build",
    "scan_figure_tasks",
    "check_missing_figures",
    "emit_generation_plan",
]
