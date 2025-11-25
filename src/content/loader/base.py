from abc import ABC, abstractmethod

from src.content.models import Content


class BaseLoader(ABC):
    """Base class for content loaders."""

    @abstractmethod
    def load(self, link: str) -> Content:
        """
        Load content from a link.

        Args:
            link: URL or file path to load content from

        Returns:
            Content object with summary, raw content, source, and metadata
        """
        ...
