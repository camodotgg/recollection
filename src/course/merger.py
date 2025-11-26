"""
Content merger for combining multiple Content objects for course generation.

This module provides functionality to merge multiple Content objects into a unified
representation suitable for course generation. It handles topic deduplication,
genre resolution, and content summary merging.
"""
from typing import Sequence, Dict, Any
from collections import Counter

from src.content.models import Content, Topic, Genre, AnalyzedContent
from src.course.models import ContentReference


class MergedContent:
    """
    Merged representation of multiple Content objects.

    Combines summaries, topics, and metadata from multiple content sources
    to create a unified view suitable for course generation.
    """

    def __init__(
        self,
        contents: Sequence[Content],
        combined_summary: str,
        topics: Sequence[Topic],
        primary_genre: Genre,
        source_references: Sequence[ContentReference],
    ):
        """
        Initialize merged content.

        Args:
            contents: Original Content objects
            combined_summary: Merged summary text from all content
            topics: Deduplicated list of topics
            primary_genre: Primary genre determined from all content
            source_references: All content references for traceability
        """
        self.contents = contents
        self.combined_summary = combined_summary
        self.topics = topics
        self.primary_genre = primary_genre
        self.source_references = source_references


def merge_contents(
    contents: Sequence[Content],
    analyzed_contents: Sequence[AnalyzedContent],
) -> MergedContent:
    """
    Merge multiple Content objects into a unified representation.

    This function:
    1. Combines summaries from all content into a unified text
    2. Deduplicates topics across all content
    3. Determines the primary genre
    4. Collects all source references for traceability

    Args:
        contents: Sequence of Content objects to merge
        analyzed_contents: Corresponding AnalyzedContent objects with genre/topics

    Returns:
        MergedContent object with combined information

    Raises:
        ValueError: If contents sequence is empty or lengths don't match

    Example:
        >>> content1 = Content.from_json_file("tutorial1.json")
        >>> content2 = Content.from_json_file("tutorial2.json")
        >>> analyzed1 = analyze(llm, content1)
        >>> analyzed2 = analyze(llm, content2)
        >>> merged = merge_contents([content1, content2], [analyzed1, analyzed2])
        >>> print(merged.primary_genre)
        Genre.TUTORIAL
    """
    if not contents:
        raise ValueError("Cannot merge empty sequence of contents")

    if len(contents) != len(analyzed_contents):
        raise ValueError(
            f"Number of contents ({len(contents)}) must match "
            f"number of analyzed contents ({len(analyzed_contents)})"
        )

    # If single content, return simplified merged view
    if len(contents) == 1:
        content = contents[0]
        analyzed = analyzed_contents[0]
        return MergedContent(
            contents=contents,
            combined_summary=_extract_summary_text(content),
            topics=analyzed.topics,
            primary_genre=analyzed.genre,
            source_references=[_create_content_reference(content, "Primary source")],
        )

    # Merge summaries
    combined_summary = _merge_summaries(contents)

    # Deduplicate topics
    merged_topics = _deduplicate_topics(analyzed_contents)

    # Determine primary genre
    primary_genre = _determine_primary_genre(analyzed_contents)

    # Collect all source references
    source_references = [
        _create_content_reference(content, f"Source {i+1}")
        for i, content in enumerate(contents)
    ]

    return MergedContent(
        contents=contents,
        combined_summary=combined_summary,
        topics=merged_topics,
        primary_genre=primary_genre,
        source_references=source_references,
    )


def _extract_summary_text(content: Content) -> str:
    """
    Extract summary text from a Content object.

    Combines abstract, introduction, chapters, and conclusion into a single text.

    Args:
        content: Content object to extract summary from

    Returns:
        Combined summary text
    """
    if not content.summary:
        return content.content_text or ""

    parts = []

    if content.summary.abstract:
        parts.append(f"# Abstract\n{content.summary.abstract}")

    if content.summary.introduction:
        parts.append(f"# Introduction\n{content.summary.introduction}")

    if content.summary.chapters:
        for i, chapter in enumerate(content.summary.chapters, 1):
            parts.append(f"# Chapter {i}: {chapter.title}\n{chapter.summary}")

    if content.summary.conclusion:
        parts.append(f"# Conclusion\n{content.summary.conclusion}")

    return "\n\n".join(parts) if parts else content.content_text or ""


def _merge_summaries(contents: Sequence[Content]) -> str:
    """
    Merge summaries from multiple Content objects.

    Creates a combined summary that includes content from all sources,
    organized by source.

    Args:
        contents: Sequence of Content objects

    Returns:
        Combined summary text
    """
    merged_parts = []

    for i, content in enumerate(contents, 1):
        summary_text = _extract_summary_text(content)

        # Add source header
        source_title = content.source.title or f"Source {i}"
        merged_parts.append(f"# Content from: {source_title}\n\n{summary_text}")

    return "\n\n---\n\n".join(merged_parts)


def _deduplicate_topics(analyzed_contents: Sequence[AnalyzedContent]) -> Sequence[Topic]:
    """
    Deduplicate topics across multiple AnalyzedContent objects.

    Combines topics from all analyzed content, removing duplicates based on topic name.
    When duplicate names are found, merges their descriptions.

    Args:
        analyzed_contents: Sequence of AnalyzedContent objects

    Returns:
        Deduplicated list of topics
    """
    # Collect all topics with their descriptions
    topic_map: Dict[str, list[str]] = {}

    for analyzed in analyzed_contents:
        if not analyzed.topics:
            continue

        for topic in analyzed.topics:
            if topic.name not in topic_map:
                topic_map[topic.name] = []
            if topic.description:
                topic_map[topic.name].append(topic.description)

    # Create deduplicated topics
    deduplicated = []
    for name, descriptions in topic_map.items():
        # Merge descriptions, removing duplicates
        unique_descriptions = list(dict.fromkeys(descriptions))  # Preserve order
        merged_description = " | ".join(unique_descriptions) if unique_descriptions else ""

        deduplicated.append(Topic(name=name, description=merged_description))

    return deduplicated


def _determine_primary_genre(analyzed_contents: Sequence[AnalyzedContent]) -> Genre:
    """
    Determine the primary genre from multiple AnalyzedContent objects.

    Uses the most common genre. If there's a tie, prefers more specific
    genres over UNKNOWN.

    Args:
        analyzed_contents: Sequence of AnalyzedContent objects

    Returns:
        Primary genre
    """
    # Collect all genres
    genres = []
    for analyzed in analyzed_contents:
        if analyzed.genre:
            genres.append(analyzed.genre)

    if not genres:
        return Genre.UNKNOWN

    # Count genre occurrences
    genre_counts = Counter(genres)

    # Get most common genre(s)
    max_count = max(genre_counts.values())
    most_common = [genre for genre, count in genre_counts.items() if count == max_count]

    # If single most common, return it
    if len(most_common) == 1:
        return most_common[0]

    # If tie, prefer non-UNKNOWN genres
    non_unknown = [g for g in most_common if g != Genre.UNKNOWN]
    if non_unknown:
        return non_unknown[0]

    return Genre.UNKNOWN


def _create_content_reference(content: Content, relevance: str) -> ContentReference:
    """
    Create a ContentReference from a Content object.

    Args:
        content: Content object to reference
        relevance: Description of how this content is relevant

    Returns:
        ContentReference object
    """
    return ContentReference(
        content_id=content.source.link,  # Use link as unique identifier
        link=content.source.link,
        relevance=relevance,
    )
