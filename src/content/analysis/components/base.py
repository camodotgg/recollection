from abc import ABC, abstractmethod

from src.content.models import AnalyzedContent


class BaseComponentAnalyzer(ABC):

    name: str

    @abstractmethod
    def analyze(self, analyzed_content: AnalyzedContent) -> AnalyzedContent:
        ...
