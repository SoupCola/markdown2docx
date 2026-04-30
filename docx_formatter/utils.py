from __future__ import annotations

from typing import Final

_PAGE_SIZE_TWIPS: Final[dict[str, tuple[int, int]]] = {
    "A4": (11906, 16838),
    "Letter": (12240, 15840),
}

_CN_SIZE_TO_PT: Final[dict[str, float]] = {
    "初号": 42.0,
    "小初": 36.0,
    "一号": 26.0,
    "小一": 24.0,
    "二号": 22.0,
    "小二": 18.0,
    "三号": 16.0,
    "小三": 15.0,
    "四号": 14.0,
    "小四": 12.0,
    "五号": 10.5,
    "小五": 9.0,
    "六号": 7.5,
    "小六": 6.5,
    "七号": 5.5,
    "八号": 5.0,
}


def cn_size_to_pt(name: str) -> float:
    return _CN_SIZE_TO_PT[name]


def chars_to_pt(value: str, font_size_pt: float) -> float:
    count = float(value.removesuffix("chars"))
    return count * font_size_pt


def parse_indent(value: str, font_size_pt: float) -> float:
    """Parse indent value supporting both 'Nchars' and 'Npt' units."""
    if value.endswith("pt"):
        return float(value.removesuffix("pt"))
    if value.endswith("chars"):
        return chars_to_pt(value, font_size_pt)
    raise ValueError(f"Unsupported indent unit: {value}")


def parse_distance(value: str) -> tuple[str, float]:
    for unit in ("cm", "pt", "in"):
        if value.endswith(unit):
            return unit, float(value.removesuffix(unit))
    raise ValueError(f"Unsupported distance unit: {value}")


def parse_line_spacing(value: str) -> tuple[str, float]:
    if value.endswith("lines"):
        return "multiple", float(value.removesuffix("lines"))
    raise ValueError(f"Unsupported line spacing value: {value}")


def cm_to_twips(cm: float) -> int:
    """Convert centimeters to twips (1 inch = 1440 twips, 1 inch = 2.54 cm)."""
    return int(cm * 1440 / 2.54)


def text_area_twips(page_size: str, left_margin_cm: float, right_margin_cm: float) -> int:
    """Return text area width in twips for tab stop calculations."""
    page_width = _PAGE_SIZE_TWIPS[page_size][0]
    return page_width - cm_to_twips(left_margin_cm) - cm_to_twips(right_margin_cm)
