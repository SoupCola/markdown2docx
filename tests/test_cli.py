from pathlib import Path

from docx_formatter.cli import _parse_overrides, _resolve_template


REPO_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = REPO_ROOT / "docx_formatter" / "templates"


def test_resolve_template_accepts_bundled_template_name():
    resolved = _resolve_template("thesis")

    assert resolved == TEMPLATES_DIR / "thesis.yaml"


def test_resolve_template_accepts_bundled_template_filename():
    resolved = _resolve_template("report.yaml")

    assert resolved == TEMPLATES_DIR / "report.yaml"


def test_resolve_template_accepts_absolute_path():
    absolute = TEMPLATES_DIR / "academic_paper.yaml"

    resolved = _resolve_template(str(absolute))

    assert resolved == absolute


def test_parse_overrides_builds_nested_dict():
    overrides = _parse_overrides([
        "body.size=小四",
        "headings.level_1.align=center",
        "page.margins.left=3cm",
    ])

    assert overrides == {
        "body": {"size": "小四"},
        "headings": {"level_1": {"align": "center"}},
        "page": {"margins": {"left": "3cm"}},
    }
