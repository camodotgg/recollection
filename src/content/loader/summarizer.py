from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel

from src.content.models import Summary, Section


def generate_summary(documents: List[Document], llm: BaseChatModel) -> Summary:
    """
    Generate a structured summary from documents using LLM.

    Args:
        documents: List of Document objects to summarize
        llm: Configured ChatAnthropic instance

    Returns:
        Summary object with abstract, introduction, chapters, and conclusion
    """
    # Combine all documents into a single text
    full_text = "\n\n".join([doc.page_content for doc in documents])

    # Create prompt for structured summarization
    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="""Analyze the following content and create a structured summary with these sections:

1. ABSTRACT: A 2-3 sentence overview of the main points
2. INTRODUCTION: 1-2 paragraphs providing context and main themes
3. CHAPTERS: Break the content into 3-5 logical sections, each with a heading and summary
4. CONCLUSION: 1-2 paragraphs with key takeaways and final thoughts

Content to summarize:
{text}

Please format your response exactly as follows:

ABSTRACT:
[Your abstract here]

INTRODUCTION:
[Your introduction here]

CHAPTERS:
## [Chapter 1 Heading]
[Chapter 1 summary]

## [Chapter 2 Heading]
[Chapter 2 summary]

## [Additional chapters as needed...]

CONCLUSION:
[Your conclusion here]
""")

    # Generate summary using LLM
    chain = prompt_template | llm
    response = chain.invoke({"text": full_text[:15000]})  # Limit to prevent token overflow

    # Parse the response
    summary_dict = _parse_summary_response(response.content)

    return Summary(
        abstract=Section(
            heading="Abstract",
            body=summary_dict["abstract"]
        ),
        introduction=Section(
            heading="Introduction",
            body=summary_dict["introduction"]
        ),
        chapters=[
            Section(heading=chapter["heading"], body=chapter["body"])
            for chapter in summary_dict["chapters"]
        ],
        conclusion=Section(
            heading="Conclusion",
            body=summary_dict["conclusion"]
        )
    )


def _parse_summary_response(response: str) -> dict:
    """
    Parse the LLM response into structured sections.

    Args:
        response: Raw LLM response text

    Returns:
        Dictionary with abstract, introduction, chapters, and conclusion
    """
    sections = {
        "abstract": "",
        "introduction": "",
        "chapters": [],
        "conclusion": ""
    }

    # Split by main sections
    lines = response.strip().split("\n")
    current_section = None
    current_chapter_heading = None
    current_chapter_body = []
    buffer = []

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("ABSTRACT:"):
            current_section = "abstract"
            buffer = []
        elif line_stripped.startswith("INTRODUCTION:"):
            if current_section == "abstract":
                sections["abstract"] = "\n".join(buffer).strip()
            current_section = "introduction"
            buffer = []
        elif line_stripped.startswith("CHAPTERS:"):
            if current_section == "introduction":
                sections["introduction"] = "\n".join(buffer).strip()
            current_section = "chapters"
            buffer = []
        elif line_stripped.startswith("CONCLUSION:"):
            # Save any pending chapter
            if current_chapter_heading:
                sections["chapters"].append({
                    "heading": current_chapter_heading,
                    "body": "\n".join(current_chapter_body).strip()
                })
                current_chapter_heading = None
                current_chapter_body = []
            current_section = "conclusion"
            buffer = []
        elif current_section == "chapters" and line_stripped.startswith("##"):
            # New chapter
            if current_chapter_heading:
                sections["chapters"].append({
                    "heading": current_chapter_heading,
                    "body": "\n".join(current_chapter_body).strip()
                })
            current_chapter_heading = line_stripped.lstrip("#").strip()
            current_chapter_body = []
        elif current_section == "chapters" and current_chapter_heading:
            if line_stripped:
                current_chapter_body.append(line)
        else:
            if line_stripped:
                buffer.append(line)

    # Save final section
    if current_section == "conclusion":
        sections["conclusion"] = "\n".join(buffer).strip()
    elif current_section == "chapters" and current_chapter_heading:
        sections["chapters"].append({
            "heading": current_chapter_heading,
            "body": "\n".join(current_chapter_body).strip()
        })

    # Ensure we have at least one chapter
    if not sections["chapters"]:
        sections["chapters"] = [{
            "heading": "Main Content",
            "body": "Summary not available"
        }]

    return sections
