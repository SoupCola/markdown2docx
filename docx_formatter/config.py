from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class HeadingLevelConfig:
    font_cn: str
    font_en: str
    size: str
    bold: bool
    align: str
    space_before: str
    space_after: str


@dataclass
class HeadingsConfig:
    level_1: HeadingLevelConfig
    level_2: HeadingLevelConfig
    level_3: HeadingLevelConfig


@dataclass
class BodyConfig:
    font_cn: str
    font_en: str
    size: str
    first_line_indent: str
    line_spacing: str
    line_spacing_rule: str
    align: str
    space_before: str
    space_after: str


@dataclass
class HeaderConfig:
    content: str
    font_cn: str
    font_en: str
    size: str


@dataclass
class FooterConfig:
    content: str


@dataclass
class PageNumberConfig:
    position: str
    format: str
    start: int


@dataclass
class PageMarginsConfig:
    top: str
    bottom: str
    left: str
    right: str


@dataclass
class PageConfig:
    size: str
    margins: PageMarginsConfig
    header: HeaderConfig
    footer: FooterConfig
    page_number: PageNumberConfig


@dataclass
class FiguresConfig:
    caption_font_cn: str
    caption_font_en: str
    caption_size: str
    caption_bold: bool
    figure_caption_position: str
    table_caption_position: str
    numbering: str
    table_style: str


@dataclass
class NumberingLevelConfig:
    style: str
    align: str
    first_line_indent: str
    hanging_indent: str
    font_cn: str
    font_en: str
    size: str
    line_spacing: str
    space_before: str
    space_after: str


@dataclass
class NumberingConfig:
    strict_mode: bool
    level_1: NumberingLevelConfig
    level_2: NumberingLevelConfig
    bracket: NumberingLevelConfig


@dataclass
class FormulaConfig:
    font_cn: str
    font_en: str
    size: str
    align: str
    space_before: str
    space_after: str
    numbering: str  # "chapter" or "continuous"


@dataclass
class ReferencesConfig:
    title: str
    title_font_cn: str
    title_font_en: str
    title_size: str
    title_bold: bool
    title_align: str
    font_cn: str
    font_en: str
    size: str
    align: str
    hanging_indent: str
    number_style: str  # "bracket" ([1]), "paren" ((1)), "dot" (1.)


@dataclass
class FormatterConfig:
    name: str
    description: str
    page: PageConfig
    headings: HeadingsConfig
    body: BodyConfig
    figures: FiguresConfig
    numbering: NumberingConfig
    formulas: FormulaConfig
    references: ReferencesConfig


def _heading(data: dict[str, Any]) -> HeadingLevelConfig:
    return HeadingLevelConfig(**data)


def _numbering_level(data: dict[str, Any]) -> NumberingLevelConfig:
    return NumberingLevelConfig(**data)


def _from_dict(data: dict[str, Any]) -> FormatterConfig:
    return FormatterConfig(
        name=data["name"],
        description=data["description"],
        page=PageConfig(
            size=data["page"]["size"],
            margins=PageMarginsConfig(**data["page"]["margins"]),
            header=HeaderConfig(**data["page"]["header"]),
            footer=FooterConfig(**data["page"]["footer"]),
            page_number=PageNumberConfig(**data["page"]["page_number"]),
        ),
        headings=HeadingsConfig(
            level_1=_heading(data["headings"]["level_1"]),
            level_2=_heading(data["headings"]["level_2"]),
            level_3=_heading(data["headings"]["level_3"]),
        ),
        body=BodyConfig(**data["body"]),
        figures=FiguresConfig(**data["figures"]),
        numbering=NumberingConfig(
            strict_mode=data["numbering"].get("strict_mode", True),
            level_1=_numbering_level(data["numbering"]["level_1"]),
            level_2=_numbering_level(data["numbering"]["level_2"]),
            bracket=_numbering_level(data["numbering"]["bracket"]),
        ),
        formulas=FormulaConfig(**data["formulas"]),
        references=ReferencesConfig(**data["references"]),
    )


def load_template(path: Path) -> FormatterConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _from_dict(raw)


def merge_overrides(config: FormatterConfig, overrides: dict[str, Any]) -> FormatterConfig:
    base = {
        "name": config.name,
        "description": config.description,
        "page": {
            "size": config.page.size,
            "margins": deepcopy(config.page.margins.__dict__),
            "header": deepcopy(config.page.header.__dict__),
            "footer": deepcopy(config.page.footer.__dict__),
            "page_number": deepcopy(config.page.page_number.__dict__),
        },
        "headings": {
            "level_1": deepcopy(config.headings.level_1.__dict__),
            "level_2": deepcopy(config.headings.level_2.__dict__),
            "level_3": deepcopy(config.headings.level_3.__dict__),
        },
        "body": deepcopy(config.body.__dict__),
        "figures": deepcopy(config.figures.__dict__),
        "numbering": {
            "strict_mode": config.numbering.strict_mode,
            "level_1": deepcopy(config.numbering.level_1.__dict__),
            "level_2": deepcopy(config.numbering.level_2.__dict__),
            "bracket": deepcopy(config.numbering.bracket.__dict__),
        },
        "formulas": deepcopy(config.formulas.__dict__),
        "references": deepcopy(config.references.__dict__),
    }

    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            for nested_key, nested_value in value.items():
                if isinstance(nested_value, dict) and isinstance(base[key].get(nested_key), dict):
                    base[key][nested_key].update(nested_value)
                else:
                    base[key][nested_key] = nested_value
        else:
            base[key] = value

    return _from_dict(base)
