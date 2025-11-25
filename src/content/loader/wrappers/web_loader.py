from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


class WebContentLoader:
    """Wrapper for loading web content using LangChain's WebBaseLoader."""

    def __init__(self, url: str):
        """
        Initialize web content loader.

        Args:
            url: Web URL to load
        """
        self.url = url
        self.loader = WebBaseLoader(url)

    def load(self) -> List[Document]:
        """
        Load web content.

        Returns:
            List of Document objects containing the web page content
        """
        return self.loader.load()
