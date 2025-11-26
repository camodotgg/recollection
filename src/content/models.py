from enum import Enum
from typing import Any, Dict, Sequence
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

class Format(str, Enum):
    PDF = "pdf"
    WEB = "web"
    YOUTUBE = "youtube"
    TEXT = "text"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"

class Section(BaseModel):
    heading: str
    body: str

class Summary(BaseModel):
    abstract: Section
    introduction: Section
    chapters: Sequence[Section]
    conclusion: Section 

class Source(BaseModel):
    author: str
    origin: str
    link: str
    created_at: datetime
    format: Format 

class Content(BaseModel):
    summary: Summary
    raw: str
    source: Source
    metadata: Dict[Any, Any]

    def to_json_file(self, file_path: Path | str) -> None:
        """
        Save Content object to a JSON file.

        Args:
            file_path: Path where to save the JSON file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_json_file(cls, file_path: Path | str) -> "Content":
        """
        Load Content object from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Content object loaded from file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return cls.model_validate_json(f.read())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Content object to a dictionary.

        Returns:
            Dictionary representation of the Content object
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Content":
        """
        Create Content object from a dictionary.

        Args:
            data: Dictionary containing content data

        Returns:
            Content object
        """
        return cls.model_validate(data)
    
    def render(self):
        s = self.summary
        src = self.source

        chapters_md = "\n".join(
            f"### Chapter {i+1}: {ch.heading}\n\n{ch.body}\n"
            for i, ch in enumerate(s.chapters)
        )

        metadata_md = "\n".join(f"- **{k}**: {v}" for k, v in self.metadata.items())

        return f"""# Content Summary

## Abstract
**{s.abstract.heading}**  
{s.abstract.body}

## Introduction
**{s.introduction.heading}**  
{s.introduction.body}

## Chapters
{chapters_md}

## Conclusion
**{s.conclusion.heading}**  
{s.conclusion.body}

# Source Information
- **Author**: {src.author}
- **Origin**: {src.origin}
- **Link**: {src.link}
- **Created At**: {src.created_at.isoformat()}
- **Format**: {src.format.value}

# Raw Content
{self.raw}

# Metadata
{metadata_md}
""".strip()


# ===

class Genre(str, Enum):
    TUTORIAL = "tutorial"
    COMMENTARY = "commentary"
    REVIEW = "review"
    NEWS = "news"
    ANALYSIS = "analysis"
    INTERVIEW = "interview"
    OPINION = "opinion"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    STORYTIME = "storytime"
    DEMONSTRATION = "demonstration"
    DOCUMENTARY = "documentary"
    UNKNOWN = "unknown"

class Topic(BaseModel):
    name: str
    description: str

class AnalysisComponent(BaseModel):
    pass

class AnalyzedContent(BaseModel):
    genre: Genre
    topics: Sequence[Topic]

    components: Dict[str, AnalysisComponent] = {}