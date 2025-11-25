#!/usr/bin/env python3
"""
Simple script demonstrating Content serialization/deserialization.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.content.models import Content, Summary, Section, Source, Format


def create_sample_content() -> Content:
    """Create a sample Content object for demonstration."""
    return Content(
        summary=Summary(
            abstract=Section(
                heading="Abstract",
                body="This document explores the fundamentals of content serialization and its applications in data persistence."
            ),
            introduction=Section(
                heading="Introduction",
                body="Content serialization is a critical component of modern applications. It enables data to be stored, transmitted, and reconstructed across different systems and time periods."
            ),
            chapters=[
                Section(
                    heading="JSON Serialization",
                    body="JSON provides a human-readable format that is widely supported across programming languages and platforms."
                ),
                Section(
                    heading="Pydantic Integration",
                    body="Pydantic models offer built-in serialization with validation, making them ideal for type-safe data handling."
                ),
                Section(
                    heading="Best Practices",
                    body="Always validate data when deserializing, use semantic versioning for schema changes, and test roundtrip serialization."
                ),
            ],
            conclusion=Section(
                heading="Conclusion",
                body="Proper serialization enables reliable data persistence and exchange, forming the backbone of modern distributed systems."
            )
        ),
        raw="Full unprocessed content would go here...",
        source=Source(
            author="Example System",
            origin="https://example.com",
            link="https://example.com/serialization-guide",
            created_at=datetime.now(),
            format=Format.WEB
        ),
        metadata={
            "version": "1.0",
            "tags": ["serialization", "json", "pydantic"],
            "word_count": 150
        }
    )


def main():
    print("Content Serialization Demo")
    print("=" * 60)

    # Create sample content
    print("\n1️⃣  Creating sample content...")
    content = create_sample_content()
    print(f"   ✓ Content created")
    print(f"   - Author: {content.source.author}")
    print(f"   - Chapters: {len(content.summary.chapters)}")
    print(f"   - Metadata keys: {list(content.metadata.keys())}")

    # Save to JSON file
    print("\n2️⃣  Saving to JSON file...")
    output_dir = Path("output")
    output_file = output_dir / "sample_content.json"
    content.to_json_file(output_file)
    print(f"   ✓ Saved to: {output_file}")
    print(f"   - File size: {output_file.stat().st_size:,} bytes")

    # Load from JSON file
    print("\n3️⃣  Loading from JSON file...")
    loaded_content = Content.from_json_file(output_file)
    print(f"   ✓ Content loaded successfully")

    # Verify data integrity
    print("\n4️⃣  Verifying data integrity...")
    checks = [
        ("Author matches", loaded_content.source.author == content.source.author),
        ("Chapter count matches", len(loaded_content.summary.chapters) == len(content.summary.chapters)),
        ("Raw content matches", loaded_content.raw == content.raw),
        ("Metadata matches", loaded_content.metadata == content.metadata),
        ("Format matches", loaded_content.source.format == content.source.format),
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False

    # Convert to dictionary
    print("\n5️⃣  Converting to dictionary...")
    data_dict = content.to_dict()
    print(f"   ✓ Converted to dict")
    print(f"   - Top-level keys: {list(data_dict.keys())}")

    # Recreate from dictionary
    print("\n6️⃣  Recreating from dictionary...")
    recreated_content = Content.from_dict(data_dict)
    print(f"   ✓ Content recreated from dict")
    print(f"   - Author: {recreated_content.source.author}")

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Serialization working correctly.")
    else:
        print("❌ Some checks failed. Please review the output above.")

    print(f"\n📁 Output file available at: {output_file.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
