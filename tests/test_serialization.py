"""Tests for Content serialization and deserialization."""
import pytest
from pathlib import Path
from datetime import datetime
from src.content.models import Content, Summary, Section, Source, Format


@pytest.fixture
def sample_content():
    """Create a sample Content object for testing."""
    return Content(
        summary=Summary(
            abstract=Section(
                heading="Abstract",
                body="This is a test abstract."
            ),
            introduction=Section(
                heading="Introduction",
                body="This is a test introduction."
            ),
            chapters=[
                Section(heading="Chapter 1", body="Chapter 1 content"),
                Section(heading="Chapter 2", body="Chapter 2 content"),
            ],
            conclusion=Section(
                heading="Conclusion",
                body="This is a test conclusion."
            )
        ),
        raw="Raw content goes here",
        source=Source(
            author="Test Author",
            origin="https://example.com",
            link="https://example.com/test",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            format=Format.WEB
        ),
        metadata={"test_key": "test_value", "count": 42}
    )


def test_to_dict(sample_content: Content):
    """Test converting Content to dictionary."""
    data = sample_content.to_dict()

    assert isinstance(data, dict)
    assert "summary" in data
    assert "raw" in data
    assert "source" in data
    assert "metadata" in data
    assert data["raw"] == "Raw content goes here"


def test_from_dict(sample_content: Content):
    """Test creating Content from dictionary."""
    data = sample_content.to_dict()
    loaded_content = Content.from_dict(data)

    assert loaded_content.raw == sample_content.raw
    assert loaded_content.source.author == sample_content.source.author
    assert len(loaded_content.summary.chapters) == len(sample_content.summary.chapters)


def test_to_json_file(sample_content: Content, tmp_path: Path):
    """Test saving Content to JSON file."""
    json_file = tmp_path / "test_content.json"
    sample_content.to_json_file(json_file)

    assert json_file.exists()
    assert json_file.stat().st_size > 0


def test_from_json_file(sample_content: Content, tmp_path: Path):
    """Test loading Content from JSON file."""
    json_file = tmp_path / "test_content.json"
    sample_content.to_json_file(json_file)

    loaded_content = Content.from_json_file(json_file)

    assert loaded_content.raw == sample_content.raw
    assert loaded_content.source.author == sample_content.source.author
    assert loaded_content.source.format == sample_content.source.format
    assert len(loaded_content.summary.chapters) == len(sample_content.summary.chapters)
    assert loaded_content.metadata == sample_content.metadata


def test_roundtrip_serialization(sample_content: Content, tmp_path: Path):
    """Test full roundtrip: Content -> JSON -> Content."""
    json_file = tmp_path / "roundtrip.json"

    # Save
    sample_content.to_json_file(json_file)

    # Load
    loaded_content = Content.from_json_file(json_file)

    # Verify all fields match
    assert loaded_content.raw == sample_content.raw
    assert loaded_content.summary.abstract.body == sample_content.summary.abstract.body
    assert loaded_content.summary.introduction.body == sample_content.summary.introduction.body
    assert loaded_content.summary.conclusion.body == sample_content.summary.conclusion.body

    for original, loaded in zip(sample_content.summary.chapters, loaded_content.summary.chapters):
        assert loaded.heading == original.heading
        assert loaded.body == original.body

    assert loaded_content.source.author == sample_content.source.author
    assert loaded_content.source.origin == sample_content.source.origin
    assert loaded_content.source.link == sample_content.source.link
    assert loaded_content.source.format == sample_content.source.format
    assert loaded_content.metadata == sample_content.metadata


def test_from_json_file_not_found():
    """Test loading from non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        Content.from_json_file("nonexistent.json")


def test_to_json_file_creates_parent_dirs(sample_content: Content, tmp_path: Path):
    """Test that to_json_file creates parent directories if they don't exist."""
    json_file = tmp_path / "nested" / "dir" / "test.json"
    sample_content.to_json_file(json_file)

    assert json_file.exists()
    assert json_file.parent.exists()


def test_json_format_is_readable(sample_content: Content, tmp_path: Path):
    """Test that saved JSON is human-readable (indented)."""
    json_file = tmp_path / "readable.json"
    sample_content.to_json_file(json_file)

    content_text = json_file.read_text()
    # Check that it's indented (has newlines and spaces)
    assert "\n" in content_text
    assert "  " in content_text  # 2-space indent


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
