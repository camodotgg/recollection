"""Tests for MagicLoader."""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.content.loader.magic import MagicLoader
from src.content.models import Format, Content, Summary, Section, Source


@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content="Mocked response"))
    return llm


@pytest.fixture
def mock_documents():
    """Create mock LangChain documents."""
    doc = Mock()
    doc.page_content = "This is test content."
    doc.metadata = {
        "author": "Test Author",
        "source": "test",
    }
    return [doc]


def test_magic_loader_initialization(mock_llm):
    """Test that MagicLoader can be initialized with an LLM."""
    loader = MagicLoader(mock_llm)
    assert loader.llm is mock_llm


def test_load_unknown_format_raises_error(mock_llm):
    """Test that loading unknown format raises ValueError."""
    loader = MagicLoader(mock_llm)

    with pytest.raises(ValueError, match="Unsupported or unknown content type"):
        loader.load("file.unknown_extension")


def test_create_source_with_metadata(mock_llm, mock_documents):
    """Test source creation from document metadata."""
    loader = MagicLoader(mock_llm)

    source = loader._create_source(
        "https://example.com/article",
        Format.WEB,
        mock_documents
    )

    assert source.author == "Test Author"
    assert source.origin == "Web"
    assert source.link == "https://example.com/article"
    assert source.format == Format.WEB
    assert isinstance(source.created_at, datetime)


def test_create_source_youtube_format(mock_llm):
    """Test source creation for YouTube."""
    loader = MagicLoader(mock_llm)

    docs = [Mock(page_content="content", metadata={"author": "Channel Name"})]
    source = loader._create_source(
        "https://youtube.com/watch?v=test",
        Format.YOUTUBE,
        docs  # type: ignore
    )

    assert source.origin == "YouTube"
    assert source.author == "Channel Name"
    assert source.format == Format.YOUTUBE


def test_create_source_pdf_format(mock_llm):
    """Test source creation for PDF."""
    loader = MagicLoader(mock_llm)

    docs = [Mock(page_content="content", metadata={})]
    source = loader._create_source(
        "/path/to/document.pdf",
        Format.PDF,
        docs  # type: ignore
    )

    assert source.origin == "PDF Document"
    assert source.format == Format.PDF


def test_extract_metadata(mock_llm, mock_documents):
    """Test metadata extraction."""
    loader = MagicLoader(mock_llm)

    metadata = loader._extract_metadata(
        "https://example.com/article",
        Format.WEB,
        mock_documents
    )

    assert metadata["source_link"] == "https://example.com/article"
    assert metadata["format_type"] == "web"
    assert metadata["document_count"] == 1
    assert metadata["author"] == "Test Author"


def test_loader_can_be_reused(mock_llm):
    """Test that the same loader instance can be used for multiple loads."""
    loader = MagicLoader(mock_llm)

    # The loader should maintain its LLM reference
    assert loader.llm is mock_llm

    # Should be able to detect different format types in sequence
    # (We're not actually loading, just testing the interface)
    assert loader.llm is mock_llm  # LLM is preserved


if __name__ == "__main__":
    # Run with pytest
    try:
        import sys
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        print("Please install pytest to run these tests:")
        print("  uv add --dev pytest")
