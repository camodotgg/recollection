#!/usr/bin/env python3
"""
Simple script to test loading a YouTube video and generating a summary.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.content.loader.magic import load
from src.content.models import Content
from src.config import get_config


def main():
    # Example YouTube URL - replace with any video
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Allow passing URL as argument
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]

    print("YouTube Video Loader Test")
    print("=" * 60)
    print(f"\nLoading: {youtube_url}")
    print("-" * 60)

    try:
        # Get config and create LLM
        config = get_config()
        print(f"✓ Config loaded")
        print(f"  Model: {config.summarization_model}")
        print(f"  Temperature: {config.temperature}")

        # Create LLM
        llm = config.create_llm()
        print(f"✓ LLM initialized")
        # Load the video
        print(f"\n⏳ Loading video and generating summary...")
        print("   (This may take a minute...)")
        content = load(llm, youtube_url)

        # Display results
        print("\n" + "=" * 60)
        print("✅ SUCCESS - Content loaded!")
        print("=" * 60)

        # Source information
        print(f"\n📺 SOURCE INFO")
        print(f"   Origin: {content.source.origin}")
        print(f"   Author: {content.source.author}")
        print(f"   Format: {content.source.format.value}")

        # Abstract
        print(f"\n📝 ABSTRACT")
        print(f"   {content.summary.abstract.body}")

        # Introduction
        print(f"\n📖 INTRODUCTION")
        intro_preview = content.summary.introduction.body
        if len(intro_preview) > 300:
            intro_preview = intro_preview[:300] + "..."
        print(f"   {intro_preview}")

        # Chapters
        print(f"\n📑 CHAPTERS ({len(content.summary.chapters)} total)")
        for i, chapter in enumerate(content.summary.chapters, 1):
            body_preview = chapter.body[:100] + "..." if len(chapter.body) > 100 else chapter.body
            print(f"   {i}. {chapter.heading}")
            print(f"      {body_preview}")

        # Conclusion
        print(f"\n🎯 CONCLUSION")
        conclusion_preview = content.summary.conclusion.body
        if len(conclusion_preview) > 300:
            conclusion_preview = conclusion_preview[:300] + "..."
        print(f"   {conclusion_preview}")

        # Stats
        print(f"\n📊 STATS")
        print(f"   Raw content length: {len(content.raw):,} characters")
        print(f"   Summary chapters: {len(content.summary.chapters)}")

        # Save to JSON file
        output_file = Path("output") / f"youtube_{content.source.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        content.to_json_file(output_file)
        print(f"\n💾 SAVED")
        print(f"   File: {output_file}")
        print(f"   Size: {output_file.stat().st_size:,} bytes")

        # Demonstrate loading it back
        print(f"\n🔄 TESTING DESERIALIZATION")
        loaded_content = Content.from_json_file(output_file)
        print(f"   ✓ Successfully loaded content from JSON")
        print(f"   ✓ Chapters match: {len(loaded_content.summary.chapters) == len(content.summary.chapters)}")
        print(f"   ✓ Raw content match: {loaded_content.raw == content.raw}")

        print("\n" + "=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure ANTHROPIC_API_KEY or OPENAI_API_KEY is set")
        print("  2. Check that the YouTube URL is valid and accessible")
        print("  3. Ensure config.yaml exists in the project root")
        print("  4. Install required dependencies: uv sync")

        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
