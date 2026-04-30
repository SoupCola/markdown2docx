from __future__ import annotations

import argparse
import atexit
import re
import tempfile
from pathlib import Path

from docx_formatter.pipeline import create_from_markdown


DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "templates" / "thesis.yaml"
IMAGE_PATTERN = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)')
TEMP_DIRS: list[tempfile.TemporaryDirectory[str]] = []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Markdown files to DOCX using the local markdown2docx skill.")
    parser.add_argument("md_paths", nargs="+", help="One or more Markdown source files.")
    parser.add_argument("output_path", help="Target DOCX file path.")
    parser.add_argument("--template-path", default=str(DEFAULT_TEMPLATE), help="YAML template path.")
    parser.add_argument("--format-docx-path", default=None, help="Optional DOCX file to extract formatting from.")
    return parser


def _rewrite_markdown_images(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        raw = match.group("path").strip()
        if raw.startswith(("http://", "https://")):
            return match.group(0)
        candidate = Path(raw)
        if candidate.is_absolute():
            return match.group(0)
        resolved = (md_path.parent / candidate).resolve()
        return f"![{match.group('alt')}]({resolved.as_posix()})"

    rewritten = IMAGE_PATTERN.sub(replace, text)
    temp_dir = tempfile.TemporaryDirectory()
    TEMP_DIRS.append(temp_dir)
    temp_path = Path(temp_dir.name) / md_path.name
    temp_path.write_text(rewritten, encoding="utf-8")
    return temp_path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source_paths = [Path(p).resolve() for p in args.md_paths]
    md_paths = [_rewrite_markdown_images(path) for path in source_paths]
    output_path = Path(args.output_path).resolve()
    template_path = Path(args.template_path).resolve()
    format_docx_path = Path(args.format_docx_path).resolve() if args.format_docx_path else None

    output_path.parent.mkdir(parents=True, exist_ok=True)

    created = create_from_markdown(
        output_path=output_path,
        md_paths=md_paths,
        template_path=template_path,
        format_docx_path=format_docx_path,
    )
    print(created)
    return 0


@atexit.register
def _cleanup_temp_dirs() -> None:
    while TEMP_DIRS:
        TEMP_DIRS.pop().cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
