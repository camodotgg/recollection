from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFContentLoader:
    """Wrapper for loading PDF content using LangChain's PyPDFLoader."""

    def __init__(self, path_or_url: str):
        """
        Initialize PDF content loader.
        Works with both local file paths and remote URLs.

        Args:
            path_or_url: Local file path or URL to PDF
        """
        self.path_or_url = path_or_url
        self.loader = PyPDFLoader(path_or_url)

    def load(self) -> List[Document]:
        """
        Load PDF content.

        Returns:
            List of Document objects containing the PDF content (one per page)
        """
        return self.loader.load()
