from typing import List, Dict, Any
from datetime import datetime
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel

from src.content.models import Content, Source, Format
from src.content.loader.detector import detect_content_type
from src.content.loader.summarizer import generate_summary
from src.content.loader.wrappers import (
    WebContentLoader,
    PDFContentLoader,
    YouTubeContentLoader,
    TextContentLoader,
)


def load(llm: BaseChatModel, link: str) -> Content:
    """
    Load content from the link, detect type, and generate summary.

    Args:
        link: URL or file path to load content from

    Returns:
        Content object with summary, raw content, source, and metadata

    Raises:
        ValueError: If content type is unsupported or unknown
    """
    # 1. Detect content type
    format_type = detect_content_type(link)

    if format_type == Format.UNKNOWN:
        raise ValueError(f"Unsupported or unknown content type for link: {link}")

    # 2. Load raw content using appropriate wrapper
    raw_docs = _load_raw_content(link, format_type)

    if not raw_docs:
        raise ValueError(f"No content could be loaded from: {link}")

    # 3. Extract source metadata
    source = _create_source(link, format_type, raw_docs)

    # 4. Generate summary using LLM
    summary = generate_summary(raw_docs, llm)

    # 5. Combine all document content
    raw_content = "\n\n".join([doc.page_content for doc in raw_docs])

    # 6. Extract metadata
    metadata = _extract_metadata(link, format_type, raw_docs)

    # 7. Create and return Content model
    return Content(
        summary=summary,
        raw=raw_content,
        source=source,
        metadata=metadata
    )

def _load_raw_content(link: str, format_type: Format) -> List[Document]:
    """
    Load raw content using the appropriate loader wrapper.

    Args:
        link: URL or file path to load
        format_type: Detected format type

    Returns:
        List of Document objects from LangChain loader

    Raises:
        ValueError: If format type is unsupported
    """
    if format_type == Format.WEB:
        loader = WebContentLoader(link)
    elif format_type == Format.PDF:
        loader = PDFContentLoader(link)
    elif format_type == Format.YOUTUBE:
        loader = YouTubeContentLoader(link)
    elif format_type in [Format.TEXT, Format.MARKDOWN]:
        loader = TextContentLoader(link)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")

    return loader.load()

def _create_source(link: str, format_type: Format, documents: List[Document]) -> Source:
    """
    Create Source object from document metadata.

    Args:
        link: Source link or path
        format_type: Detected format type
        documents: List of Document objects

    Returns:
        Source object with metadata
    """
    # Extract metadata from first document
    metadata = documents[0].metadata if documents else {}

    # Try to extract author
    author = metadata.get("author", "Unknown")
    if isinstance(author, list) and author:
        author = author[0]

    # Determine origin
    origin = "Unknown"
    if format_type == Format.WEB:
        origin = "Web"
    elif format_type == Format.PDF:
        origin = "PDF Document"
    elif format_type == Format.YOUTUBE:
        origin = "YouTube"
        # YouTube loader provides author as 'author' in metadata
        if "author" in metadata:
            author = metadata["author"]
    elif format_type in [Format.TEXT, Format.MARKDOWN]:
        origin = "Text File"

    # Get creation time
    created_at = datetime.now()
    if "publish_date" in metadata:
        # Try to parse publish date if available
        try:
            created_at = datetime.fromisoformat(str(metadata["publish_date"]))
        except (ValueError, TypeError):
            pass

    return Source(
        author=str(author),
        origin=origin,
        link=link,
        created_at=created_at,
        format=format_type
    )

def _extract_metadata(link: str, format_type: Format, documents: List[Document]) -> Dict[Any, Any]:
    """
    Extract and combine metadata from all documents.

    Args:
        link: Source link or path
        format_type: Detected format type
        documents: List of Document objects

    Returns:
        Dictionary of metadata
    """
    combined_metadata = {}

    for doc in documents:
        if doc.metadata:
            combined_metadata.update(doc.metadata)

    # TODO: add more metadata if needed
    combined_metadata["source_link"] = link
    combined_metadata["format_type"] = format_type.value
    combined_metadata["document_count"] = len(documents)

    return combined_metadata
