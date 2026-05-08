"""Command-line interface for docx_formatter.

Provides two subcommands:
  convert  -- Markdown files to DOCX
  format   -- Existing DOCX to formatted DOCX
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .template_paths import resolve_template_path


def _resolve_template(template: str) -> Path:
    return resolve_template_path(template)


def _parse_overrides(pairs: list[str] | None) -> dict:
    """Parse ``key=value`` override strings into a nested dict.

    Dotted keys like ``body.size`` are expanded into ``{"body": {"size": value}}``.
    """
    overrides: dict = {}
    if not pairs:
        return overrides
    for pair in pairs:
        if "=" not in pair:
            print(f"Error: override '{pair}' is not in key=value format", file=sys.stderr)
            sys.exit(1)
        key, value = pair.split("=", 1)
        parts = key.split(".")
        d = overrides
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value
    return overrides


# -- sub-command handlers -------------------------------------------------

def _cmd_convert(args: argparse.Namespace) -> None:
    from .pipeline import create_from_markdown

    md_paths = [Path(p).resolve() for p in args.inputs]
    output_path = Path(args.output).resolve() if args.output else Path("output.docx").resolve()
    template_path = _resolve_template(args.template) if args.template else None
    overrides = _parse_overrides(args.override)
    format_docx_path = Path(args.format_docx).resolve() if args.format_docx else None

    if template_path is None and format_docx_path is None:
        print("Error: --template (-t) is required for convert", file=sys.stderr)
        sys.exit(1)

    result = create_from_markdown(
        output_path=output_path,
        md_paths=md_paths,
        format_docx_path=format_docx_path,
        template_path=template_path,
        overrides=overrides,
    )
    print(f"Created: {result}")


def _cmd_format(args: argparse.Namespace) -> None:
    from .pipeline import format_document

    source_path = Path(args.input).resolve()
    template_path = _resolve_template(args.template) if args.template else None
    overrides = _parse_overrides(args.override)

    if template_path is None:
        print("Error: --template (-t) is required for format", file=sys.stderr)
        sys.exit(1)

    result = format_document(
        source_path=source_path,
        template_path=template_path,
        overrides=overrides,
    )
    print(f"Created: {result}")


# -- argument parser ------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docx_formatter",
        description="Convert Markdown to formatted DOCX, or re-format an existing DOCX.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # -- convert -----------------------------------------------------------
    convert_p = sub.add_parser(
        "convert",
        help="Convert Markdown file(s) to a formatted DOCX",
        description="Convert one or more Markdown files into a single formatted DOCX document.",
    )
    convert_p.add_argument(
        "inputs",
        nargs="+",
        metavar="INPUT",
        help="Markdown file path(s) to convert",
    )
    convert_p.add_argument(
        "-o", "--output",
        default=None,
        help="Output DOCX path (default: output.docx)",
    )
    convert_p.add_argument(
        "-t", "--template",
        default=None,
        help="Template name (e.g. thesis) or absolute path to YAML template",
    )
    convert_p.add_argument(
        "--override",
        action="append",
        default=None,
        metavar="KEY=VALUE",
        help="Format override in dotted key=value form (repeatable)",
    )
    convert_p.add_argument(
        "--format-docx",
        default=None,
        metavar="DOCX",
        help="Reference DOCX to extract formatting from",
    )
    convert_p.set_defaults(func=_cmd_convert)

    # -- format ------------------------------------------------------------
    format_p = sub.add_parser(
        "format",
        help="Apply template formatting to an existing DOCX",
        description="Apply a template's formatting rules to an existing DOCX file.",
    )
    format_p.add_argument(
        "input",
        metavar="INPUT",
        help="DOCX file to format",
    )
    format_p.add_argument(
        "-t", "--template",
        default=None,
        help="Template name (e.g. thesis) or absolute path to YAML template",
    )
    format_p.add_argument(
        "--override",
        action="append",
        default=None,
        metavar="KEY=VALUE",
        help="Format override in dotted key=value form (repeatable)",
    )
    format_p.set_defaults(func=_cmd_format)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
