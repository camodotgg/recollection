from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


class TextContentLoader:
    """Wrapper for loading text files using LangChain's TextLoader."""

    def __init__(self, file_path: str):
        """
        Initialize text content loader.

        Args:
            file_path: Local path to text file
        """
        self.file_path = file_path
        self.loader = TextLoader(file_path)

    def load(self) -> List[Document]:
        """
        Load text file content.

        Returns:
            List of Document objects containing the text file content
        """
        return self.loader.load()
