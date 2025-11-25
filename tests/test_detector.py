"""Tests for content type detection."""
import pytest
from src.content.loader.detector import detect_content_type
from src.content.models import Format


def test_detect_youtube_urls():
    """Test YouTube URL detection."""
    assert detect_content_type("https://youtube.com/watch?v=test") == Format.YOUTUBE
    assert detect_content_type("https://www.youtube.com/watch?v=test") == Format.YOUTUBE
    assert detect_content_type("https://youtu.be/test") == Format.YOUTUBE
    assert detect_content_type("HTTPS://YOUTUBE.COM/WATCH?V=TEST") == Format.YOUTUBE


def test_detect_pdf_urls():
    """Test PDF URL detection."""
    assert detect_content_type("https://example.com/document.pdf") == Format.PDF
    assert detect_content_type("http://example.com/paper.PDF") == Format.PDF


def test_detect_web_urls():
    """Test web URL detection."""
    assert detect_content_type("https://example.com/article") == Format.WEB
    assert detect_content_type("http://blog.com/post") == Format.WEB
    assert detect_content_type("https://news.site.com/article.html") == Format.WEB


def test_detect_local_pdf():
    """Test local PDF file detection."""
    assert detect_content_type("/path/to/document.pdf") == Format.PDF
    assert detect_content_type("document.pdf") == Format.PDF
    assert detect_content_type("./folder/file.PDF") == Format.PDF


def test_detect_text_files():
    """Test text file detection."""
    assert detect_content_type("notes.txt") == Format.TEXT
    assert detect_content_type("/path/to/file.txt") == Format.TEXT
    assert detect_content_type("README.TXT") == Format.TEXT


def test_detect_markdown_files():
    """Test markdown file detection."""
    assert detect_content_type("README.md") == Format.MARKDOWN
    assert detect_content_type("notes.markdown") == Format.MARKDOWN
    assert detect_content_type("/docs/guide.MD") == Format.MARKDOWN


def test_detect_unknown_format():
    """Test unknown format detection."""
    assert detect_content_type("file.xyz") == Format.UNKNOWN
    assert detect_content_type("unknown") == Format.UNKNOWN


def test_case_insensitive_detection():
    """Test that detection is case-insensitive."""
    assert detect_content_type("FILE.PDF") == Format.PDF
    assert detect_content_type("NOTES.TXT") == Format.TEXT
    assert detect_content_type("README.MD") == Format.MARKDOWN
    assert detect_content_type("HTTPS://EXAMPLE.COM/ARTICLE") == Format.WEB


if __name__ == "__main__":
    # Run with pytest when available
    try:
        import sys
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        print("pytest not installed. Running basic tests...")
        test_detect_youtube_urls()
        print("✓ test_detect_youtube_urls passed")
        test_detect_pdf_urls()
        print("✓ test_detect_pdf_urls passed")
        test_detect_web_urls()
        print("✓ test_detect_web_urls passed")
        test_detect_local_pdf()
        print("✓ test_detect_local_pdf passed")
        test_detect_text_files()
        print("✓ test_detect_text_files passed")
        test_detect_markdown_files()
        print("✓ test_detect_markdown_files passed")
        test_detect_unknown_format()
        print("✓ test_detect_unknown_format passed")
        test_case_insensitive_detection()
        print("✓ test_case_insensitive_detection passed")
        print("\nAll tests passed!")
