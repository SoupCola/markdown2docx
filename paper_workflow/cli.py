"""Paper workflow CLI entry point."""

import argparse
import sys
from pathlib import Path

from .config import load_thesis_config, validate_config
from .build import build_docx, full_build
from .figures import scan_figure_tasks, check_missing_figures, emit_generation_plan


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-workflow",
        description="Thesis paper workflow orchestration layer.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # build-docx command
    build_docx_parser = sub.add_parser(
        "build-docx",
        help="Build DOCX from existing markdown/images/config",
    )
    build_docx_parser.add_argument(
        "--config",
        "-c",
        default="thesis.config.yaml",
        help="Path to thesis.config.yaml (default: thesis.config.yaml)",
    )
    build_docx_parser.add_argument(
        "--project-root",
        "-r",
        help="Project root directory (default: config file parent)",
    )

    # full-build command
    full_build_parser = sub.add_parser(
        "full-build",
        help="Strict orchestration: check upstream generators, then build DOCX",
    )
    full_build_parser.add_argument(
        "--config",
        "-c",
        default="thesis.config.yaml",
        help="Path to thesis.config.yaml (default: thesis.config.yaml)",
    )
    full_build_parser.add_argument(
        "--project-root",
        "-r",
        help="Project root directory (default: config file parent)",
    )

    # make-figure command
    make_figure_parser = sub.add_parser(
        "make-figure",
        help="Scan markdown for figure tasks and report missing figures",
    )
    make_figure_parser.add_argument(
        "--config",
        "-c",
        default="thesis.config.yaml",
        help="Path to thesis.config.yaml (default: thesis.config.yaml)",
    )
    make_figure_parser.add_argument(
        "--project-root",
        "-r",
        help="Project root directory (default: config file parent)",
    )

    return parser


def _cmd_build_docx(args: argparse.Namespace) -> None:
    """Handle build-docx command."""
    config_path = Path(args.config).resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else config_path.parent

    try:
        config = load_thesis_config(config_path)
        errors = validate_config(config, project_root)
        if errors:
            print("Config validation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        result = build_docx(config, project_root)
        print(f"Built: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_full_build(args: argparse.Namespace) -> None:
    """Handle full-build command."""
    config_path = Path(args.config).resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else config_path.parent

    try:
        config = load_thesis_config(config_path)
        errors = validate_config(config, project_root)
        if errors:
            print("Config validation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        result = full_build(config, project_root)
        print(f"Built: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_make_figure(args: argparse.Namespace) -> None:
    """Handle make-figure command."""
    config_path = Path(args.config).resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else config_path.parent

    try:
        config = load_thesis_config(config_path)

        # Get content chapters from config
        content = config.get("content", {})
        chapters = content.get("chapters", [])
        md_paths = [project_root / ch for ch in chapters]

        # Get figures directory
        figures_config = config.get("figures", {})
        figures_dir = project_root / figures_config.get("output_dir", "assets/figures")

        # Scan and check
        tasks = scan_figure_tasks(md_paths, figures_dir)
        missing = check_missing_figures(tasks)

        if not tasks:
            print("No figure tasks found in markdown files.")
            print("Add <!-- figure:prompt=\"description\" --> before image references.")
            return

        print(f"Found {len(tasks)} figure task(s), {len(missing)} missing.\n")
        print(emit_generation_plan(missing))

        if missing:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for paper-workflow CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "build-docx":
        _cmd_build_docx(args)
    elif args.command == "full-build":
        _cmd_full_build(args)
    elif args.command == "make-figure":
        _cmd_make_figure(args)
    else:
        parser.print_help()
        sys.exit(1)
