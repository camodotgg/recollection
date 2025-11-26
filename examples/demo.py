import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.content.loader.magic import load
from src.content.loader.detector import detect_content_type
from src.config import get_config


def main():
    print("Magic Loader Demo")
    print("=" * 50)

    # Example links to test
    test_links = [
        "https://example.com/article",
        "https://example.com/document.pdf",
        "https://youtube.com/watch?v=test",
        "sample.txt",
        "notes.md",
    ]

    print("\nTesting content type detection:")
    print("-" * 50)
    for link in test_links:
        format_type = detect_content_type(link)
        print(f"{link:<40} -> {format_type.value}")

    print("\n" + "=" * 50)
    print("\nTo test the full MagicLoader with LLM summarization:")
    print("1. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
    print("2. Run with a real URL as argument:")
    print("   python examples/demo.py <url>")
    print("\nExample:")
    print("   python examples/demo.py https://example.com/article")

    # If a URL is provided as argument, try to load it
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"\n\nLoading content from: {url}")
        print("-" * 50)

        try:
            # Get config and create LLM
            config = get_config()
            llm = config.create_llm()
            print(f"✓ LLM initialized: {config.summarization_model}")

            # Detect format
            format_type = detect_content_type(url)
            print(f"Detected format: {format_type.value}")

            # Load content
            content = load(llm, url)

            print("\n✓ Content loaded successfully!")
            print(f"\nSource: {content.source.origin}")
            print(f"Author: {content.source.author}")
            print(f"Format: {content.source.format.value}")
            print(f"\nAbstract:\n{content.summary.abstract.body}")
            print(f"\nIntroduction:\n{content.summary.introduction.body[:200]}...")
            print(f"\nChapters: {len(content.summary.chapters)}")
            for i, chapter in enumerate(content.summary.chapters, 1):
                print(f"  {i}. {chapter.heading}")
            print(f"\nRaw content length: {len(content.raw)} characters")

            # Show that the loader can be reused
            print("\n" + "=" * 50)
            print("Note: The same loader instance can load multiple URLs!")
            print("Example:")
            print("  loader = MagicLoader(llm)")
            print("  content1 = loader.load('url1')")
            print("  content2 = loader.load('url2')")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\nMake sure:")
            print("- ANTHROPIC_API_KEY or OPENAI_API_KEY is set")
            print("- The URL is valid and accessible")
            print("- config.yaml exists in the project root")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
