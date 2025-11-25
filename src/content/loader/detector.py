from pathlib import Path

from src.content.models import Format


def detect_content_type(link: str) -> Format:
    """
    Detect content type from URL or file path using pattern matching.

    Args:
        link: URL or file path to detect

    Returns:
        Format enum value indicating the content type
    """
    link_lower = link.lower().strip()

    # Check for YouTube URLs
    if "youtube.com/watch" in link_lower or "youtu.be/" in link_lower:
        return Format.YOUTUBE

    # Check for URLs
    if link_lower.startswith("http://") or link_lower.startswith("https://"):
        # Check if URL ends with .pdf
        if link_lower.endswith(".pdf"):
            return Format.PDF
        # Otherwise assume web content
        return Format.WEB

    # Check local file paths
    path = Path(link)

    # Get file extension
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return Format.PDF
    elif suffix in [".txt"]:
        return Format.TEXT
    elif suffix in [".md", ".markdown"]:
        return Format.MARKDOWN
    elif suffix == "":
        # No extension - might be a directory or file without extension
        if path.exists() and path.is_file():
            # Try to guess based on content or treat as text
            return Format.TEXT
        return Format.UNKNOWN

    # Unknown format
    return Format.UNKNOWN
