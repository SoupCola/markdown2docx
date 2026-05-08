"""Tests for HTML comment filtering in markdown parser."""

import pytest
from pathlib import Path

from docx_formatter.md_parser import parse_markdown_files


def test_html_comments_are_filtered(tmp_path):
    """Test that HTML comments are not included in parsed output."""
    md_content = """# Test Heading

<!-- This is a comment -->

Some body text.

<!-- figure:prompt="test" -->
![image](test.png)
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")

    paragraphs, references = parse_markdown_files([md_file])

    # Should have: heading, body, image (no comments)
    types = [p["type"] for p in paragraphs]
    assert "heading_1" in types
    assert "body" in types
    assert "image" in types

    # Verify no comment text appears in body
    for p in paragraphs:
        if p["type"] == "body":
            assert "figure:prompt" not in p["text"]
            assert "<!--" not in p["text"]


def test_html_comments_multiline(tmp_path):
    """Test that multi-line HTML comments are handled."""
    md_content = """# Test

<!--
Multi-line
comment
-->

Body text here.
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")

    paragraphs, references = parse_markdown_files([md_file])

    # Should have: heading, body (no comment lines)
    assert len(paragraphs) == 2
    assert paragraphs[0]["type"] == "heading_1"
    assert paragraphs[1]["type"] == "body"
    assert "Multi-line" not in paragraphs[1]["text"]
