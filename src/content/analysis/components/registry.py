from .base import BaseComponentAnalyzer

class ComponentAnalyzerRegistry:
    _registry = {}

    @classmethod
    def register(cls, analyzer: BaseComponentAnalyzer):
        cls._registry[analyzer.name] = analyzer

    @classmethod
    def get(cls, name: str):
        return cls._registry.get(name)

    @classmethod
    def all(cls):
        return cls._registry
