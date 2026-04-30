import pytest

from docx_formatter.utils import chars_to_pt, cn_size_to_pt, parse_distance, parse_line_spacing


@pytest.mark.parametrize(
    ("name", "expected"),
    [("三号", 16.0), ("小四", 12.0), ("五号", 10.5)],
)
def test_cn_size_to_pt_returns_point_values(name, expected):
    assert cn_size_to_pt(name) == expected


def test_chars_to_pt_uses_font_size_multiplier():
    assert chars_to_pt("2chars", 12.0) == 24.0


@pytest.mark.parametrize(
    ("value", "expected"),
    [("2.54cm", 2.54), ("24pt", 24.0), ("1in", 1.0)],
)
def test_parse_distance_preserves_unit_value_for_constructor_input(value, expected):
    unit, number = parse_distance(value)
    assert unit in {"cm", "pt", "in"}
    assert number == expected


def test_parse_line_spacing_multiple_lines():
    mode, value = parse_line_spacing("1.5lines")
    assert mode == "multiple"
    assert value == 1.5
