import json
from typing import Dict, List
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from src.content.models import Content, AnalyzedContent, Genre, Topic, AnalysisComponent

from .components.registry import ComponentAnalyzerRegistry
from .components.base import BaseComponentAnalyzer


def analyze(llm: BaseChatModel, content: Content, component_analyzers: List[str] | None = None) -> AnalyzedContent:
    """
    Analyze content to extract genre, topics, and optional component-specific insights.

    This function performs a multi-stage analysis on the provided content:
    1. Infers the genre classification
    2. Extracts key topics with descriptions
    3. Optionally runs registered component analyzers for specialized analysis

    Args:
        llm: LangChain chat model instance to use for analysis
        content: Content object containing the material to analyze
        component_analyzers: Optional list of component analyzer names to run.
                           Must be registered in ComponentAnalyzerRegistry.

    Returns:
        AnalyzedContent object containing genre, topics, and component analysis results

    Raises:
        ValueError: If a specified component analyzer is not registered

    Example:
        >>> llm = create_llm("gpt-4o-mini", api_key="...")
        >>> content = Content.from_json_file("content.json")
        >>> analysis = analyze(llm, content, component_analyzers=["sentiment"])
        >>> print(analysis.genre)
        >>> print(analysis.topics)
    """
    partial_analyzed_content = AnalyzedContent(
        genre=_infer_genre(llm, content),
        topics=_infer_topics(llm, content)
    )

    if component_analyzers:
        partial_analyzed_content.components = _analyze_components(partial_analyzed_content, component_analyzers)

    return partial_analyzed_content


def _analyze_components(analyzed_content: AnalyzedContent, component_analyzers: List[str]) -> Dict[str, AnalysisComponent]:
    """
    Run registered component analyzers on the analyzed content.

    Component analyzers are pluggable analysis modules that perform specialized
    analysis tasks (e.g., sentiment analysis, research analysis, etc.). Each analyzer
    must be registered in the ComponentAnalyzerRegistry before use.

    Args:
        analyzed_content: AnalyzedContent object with genre and topics already inferred
        component_analyzers: List of component analyzer names to execute

    Returns:
        Dictionary mapping analyzer names to their AnalysisComponent results

    Raises:
        ValueError: If any specified analyzer is not registered in the registry
    """
    selected: Dict[str, BaseComponentAnalyzer] = {}
    for name in component_analyzers:
        analyzer = ComponentAnalyzerRegistry.get(name)
        if analyzer is None:
            raise ValueError(f"ComponentAnalyzer with name '{name}' is not registered.")
        selected[name] = analyzer

    components = {}
    for name, analyzer in selected.items():
        partial = analyzer.analyze(analyzed_content)
        components[name] = partial

    return components

def _infer_genre(llm: BaseChatModel, content: Content) -> Genre:
    """
    Infer the genre classification of the content using an LLM.

    Uses a prompt-based approach to classify content into one of the predefined
    Genre categories. The LLM is asked to select from a specific list of genres,
    and the response is matched against the Genre enum.

    Args:
        llm: LangChain chat model to use for classification
        content: Content object to classify

    Returns:
        Genre enum value representing the classified genre.
        Returns Genre.UNKNOWN if classification is uncertain or doesn't match
        any predefined genre.
    """
    genre_list = ", ".join(g.value for g in Genre)

    prompt_template = PromptTemplate(
        input_variables=["text"],
        template=(
            "Classify the genre of the following content.\n\n"
            "Return ONLY one of the following genres:\n"
            f"{genre_list}\n\n"
            "If you are not sure, return 'unknown'.\n\n"
            "Here is the Content:\n{text}"
        )
    )

    chain = prompt_template | llm | StrOutputParser()

    raw_output = chain.invoke({"text": content.render()}).strip().lower()

    for g in Genre:
        if raw_output == g.value.lower():
            return g

    return Genre.UNKNOWN


def _infer_topics(llm: BaseChatModel, content: Content) -> List[Topic]:
    """
    Extract key topics from the content using an LLM.

    Uses the LLM to identify and describe the main topics covered in the content.
    The LLM returns structured JSON data with topic names and descriptions, which
    are parsed into Topic objects.

    Args:
        llm: LangChain chat model to use for topic extraction
        content: Content object to analyze for topics

    Returns:
        List of Topic objects, each containing a name and description.
        Returns empty list if JSON parsing fails or no topics are found.
    """
    # TODO: use structured output
    prompt_template = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are an AI assistant. Extract the key topics from the following content.\n\n"
            "For each topic, provide:\n"
            "- a concise name (1-3 words)\n"
            "- a short description (1-2 sentences) explaining the topic\n\n"
            "Return the result ONLY as JSON in this format:\n"
            "[\n"
            "  {{\"name\": \"Topic Name\", \"description\": \"Short description.\"}},\n"
            "  ...\n"
            "]\n\n"
            "If you are unsure about any topic, skip it.\n\n"
            "Here is the content:\n{text}"
        )
    )

    chain = prompt_template | llm | StrOutputParser()

    raw_output = chain.invoke({"text": content.render()})

    try:
        topics_data = json.loads(raw_output)
        topics = [Topic(**t) for t in topics_data]
    except json.JSONDecodeError:
        topics = []

    return topics
    