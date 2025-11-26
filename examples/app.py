"""
Recollection TUI - Interactive terminal application for content learning.

A beautiful terminal interface for loading content, generating courses,
and managing your learning journey.
"""
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box
from rich.columns import Columns

from src.content.loader.magic import load
from src.content.models import Content
from src.course import generate_course
from src.course.models import Course
from src.config import get_config


console = Console()


class RecollectionApp:
    """Main TUI application for Recollection."""

    def __init__(self):
        self.console = console
        self.config = get_config()
        self.analysis_llm = None
        self.course_llm = None
        self.current_content: Optional[Content] = None
        self.current_course: Optional[Course] = None
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def initialize_llms(self):
        """Initialize LLM models."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Initializing AI models...", total=None)
            self.analysis_llm = self.config.create_llm("summarization")
            self.course_llm = self.config.create_llm("course_generation")

    def show_header(self):
        """Display application header."""
        header = Text()
        header.append("━" * 70 + "\n", style="bright_cyan")
        header.append("  🎓 RECOLLECTION", style="bold bright_cyan")
        header.append(" - Transform Content into Learning Courses\n", style="cyan")
        header.append("━" * 70, style="bright_cyan")

        self.console.print()
        self.console.print(Panel(
            header,
            border_style="bright_cyan",
            box=box.ROUNDED,
        ))
        self.console.print()

    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        menu = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        menu.add_column(style="cyan bold", width=4)
        menu.add_column(style="white")

        menu.add_row("1.", "📥 Load Content from URL")
        menu.add_row("2.", "📄 View Current Content")
        menu.add_row("3.", "🎓 Generate Course")
        menu.add_row("4.", "📖 View Current Course")
        menu.add_row("5.", "💾 Save Course to File")
        menu.add_row("6.", "📂 Load Course from File")
        menu.add_row("7.", "⚙️  Settings")
        menu.add_row("0.", "🚪 Exit")

        self.console.print(Panel(
            menu,
            title="[bold cyan]Main Menu[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        ))

        return Prompt.ask(
            "\n[cyan]Choose an option[/cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="1"
        )

    def load_content(self):
        """Load content from a URL."""
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]Load Content from URL[/bold cyan]\n\n"
            "Supported sources:\n"
            "  • 🌐 Web articles and blog posts\n"
            "  • 📄 PDF documents (local or remote)\n"
            "  • 🎥 YouTube videos (transcript)\n"
            "  • 📝 Text/Markdown files",
            border_style="cyan",
            box=box.ROUNDED,
        ))

        url = Prompt.ask("\n[cyan]Enter URL or file path[/cyan]")

        if not url:
            self.console.print("[yellow]No URL provided[/yellow]")
            return

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as progress:
                task = progress.add_task("Loading content...", total=3)

                # Load content
                progress.update(task, description="Detecting content type...")
                progress.advance(task)

                progress.update(task, description="Loading and analyzing...")
                self.current_content = load(self.analysis_llm, url)
                progress.advance(task)

                progress.update(task, description="Complete!")
                progress.advance(task)

            # Show success
            self.console.print()
            self.console.print(Panel(
                f"[green]✓ Content loaded successfully![/green]\n\n"
                f"[bold]Source:[/bold] {self.current_content.source.link}\n"
                f"[bold]Author:[/bold] {self.current_content.source.author}\n"
                f"[bold]Format:[/bold] {self.current_content.source.format.value}\n"
                f"[bold]Size:[/bold] {len(self.current_content.raw)} characters",
                border_style="green",
                box=box.ROUNDED,
            ))

            # Auto-save content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_file = self.output_dir / f"content_{timestamp}.json"
            self.current_content.to_json_file(content_file)
            self.console.print(f"[dim]Saved to: {content_file}[/dim]")

        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[red]✗ Error loading content[/red]\n\n{str(e)}",
                border_style="red",
                box=box.ROUNDED,
            ))

    def view_content(self):
        """View current loaded content."""
        if not self.current_content:
            self.console.print("[yellow]No content loaded. Load content first (option 1)[/yellow]")
            return

        content = self.current_content

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=8),
            Layout(name="summary", size=20),
        )

        # Header info
        header_text = Text()
        header_text.append(f"Source: ", style="bold cyan")
        header_text.append(f"{content.source.link}\n", style="white")
        header_text.append(f"Author: ", style="bold cyan")
        header_text.append(f"{content.source.author}\n", style="white")
        header_text.append(f"Format: ", style="bold cyan")
        header_text.append(f"{content.source.format.value}\n", style="white")

        layout["header"].update(Panel(
            header_text,
            title="[bold cyan]Content Information[/bold cyan]",
            border_style="cyan",
        ))

        # Summary
        summary_text = Text()
        summary_text.append("Abstract:\n", style="bold yellow")
        summary_text.append(f"{content.summary.abstract.body}\n\n", style="white")
        summary_text.append("Introduction:\n", style="bold yellow")
        summary_text.append(f"{content.summary.introduction.body}\n\n", style="white")

        if content.summary.chapters:
            summary_text.append(f"Chapters: {len(content.summary.chapters)}\n", style="bold yellow")
            for i, chapter in enumerate(content.summary.chapters[:3], 1):
                summary_text.append(f"  {i}. {chapter.heading}\n", style="cyan")

        layout["summary"].update(Panel(
            summary_text,
            title="[bold cyan]Summary[/bold cyan]",
            border_style="cyan",
        ))

        self.console.print()
        self.console.print(layout)

    def generate_course_ui(self):
        """Generate a course from current content."""
        if not self.current_content:
            self.console.print("[yellow]No content loaded. Load content first (option 1)[/yellow]")
            return

        self.console.print()
        self.console.print(Panel(
            "[bold cyan]Course Generation[/bold cyan]\n\n"
            "This will analyze your content and create a structured course with:\n"
            "  • 🎯 Smart lesson breakdown\n"
            "  • ✅ Learning objectives\n"
            "  • 🎓 Key takeaways\n"
            "  • 📚 Genre-specific strategies",
            border_style="cyan",
            box=box.ROUNDED,
        ))

        if not Confirm.ask("\n[cyan]Generate course?[/cyan]", default=True):
            return

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as progress:
                task = progress.add_task("Generating course...", total=5)

                progress.update(task, description="Analyzing content genre and topics...")
                progress.advance(task)

                progress.update(task, description="Selecting course strategy...")
                progress.advance(task)

                progress.update(task, description="Designing lesson structure with AI...")
                progress.advance(task)

                self.current_course = generate_course(
                    llm=self.course_llm,
                    contents=[self.current_content],
                )

                progress.update(task, description="Extracting key takeaways...")
                progress.advance(task)

                progress.update(task, description="Complete!")
                progress.advance(task)

            # Show success
            self.console.print()
            self.console.print(Panel(
                f"[green]✓ Course generated successfully![/green]\n\n"
                f"[bold]Title:[/bold] {self.current_course.title}\n"
                f"[bold]Genre:[/bold] {self.current_course.genre.value}\n"
                f"[bold]Lessons:[/bold] {len(self.current_course.lessons)}\n"
                f"[bold]Topics:[/bold] {len(self.current_course.topics)}\n"
                f"[bold]Duration:[/bold] {self.current_course.estimated_duration}",
                border_style="green",
                box=box.ROUNDED,
            ))

            # Auto-save course
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            course_file = self.output_dir / f"course_{timestamp}.json"
            self.current_course.to_json_file(course_file)
            self.console.print(f"[dim]Saved to: {course_file}[/dim]")

        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[red]✗ Error generating course[/red]\n\n{str(e)}",
                border_style="red",
                box=box.ROUNDED,
            ))
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")

    def view_course(self):
        """View current generated course."""
        if not self.current_course:
            self.console.print("[yellow]No course generated. Generate a course first (option 3)[/yellow]")
            return

        course = self.current_course

        # Course header
        header = Table.grid(padding=(0, 2))
        header.add_column(style="bold cyan")
        header.add_column(style="white")

        header.add_row("Title:", course.title)
        header.add_row("Genre:", course.genre.value)
        header.add_row("Difficulty:", course.difficulty_level.value)
        header.add_row("Duration:", str(course.estimated_duration))
        header.add_row("Lessons:", str(len(course.lessons)))

        self.console.print()
        self.console.print(Panel(
            header,
            title="[bold cyan]Course Overview[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        ))

        # Topics
        self.console.print()
        topics_text = Text()
        for i, topic in enumerate(course.topics, 1):
            topics_text.append(f"{i}. ", style="cyan bold")
            topics_text.append(f"{topic.name}\n", style="white")
            if topic.description:
                topics_text.append(f"   {topic.description}\n", style="dim")

        self.console.print(Panel(
            topics_text,
            title="[bold cyan]Topics Covered[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        ))

        # Lessons
        self.console.print()
        for i, lesson in enumerate(course.lessons, 1):
            lesson_info = Text()
            lesson_info.append(f"Duration: {lesson.estimated_duration}\n", style="yellow")
            lesson_info.append(f"{lesson.description}\n\n", style="white")
            lesson_info.append("Objectives:\n", style="bold cyan")
            for obj in lesson.objectives:
                lesson_info.append(f"  • {obj}\n", style="white")

            self.console.print(Panel(
                lesson_info,
                title=f"[bold cyan]Lesson {i}: {lesson.title}[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            ))

        # Takeaways
        self.console.print()
        takeaways_text = Text()
        for i, takeaway in enumerate(course.takeaways, 1):
            takeaways_text.append(f"{i}. {takeaway.name}\n", style="bold yellow")
            takeaways_text.append(f"   {takeaway.description}\n", style="white")
            takeaways_text.append(f"   [dim]Criteria: {takeaway.criteria}[/dim]\n\n", style="dim")

        self.console.print(Panel(
            takeaways_text,
            title="[bold cyan]Key Takeaways[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        ))

    def save_course(self):
        """Save course to a file."""
        if not self.current_course:
            self.console.print("[yellow]No course to save. Generate a course first (option 3)[/yellow]")
            return

        self.console.print()
        default_name = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filename = Prompt.ask(
            "[cyan]Enter filename[/cyan]",
            default=default_name
        )

        filepath = self.output_dir / filename
        self.current_course.to_json_file(filepath)

        self.console.print()
        self.console.print(Panel(
            f"[green]✓ Course saved successfully![/green]\n\n"
            f"[bold]Location:[/bold] {filepath}",
            border_style="green",
            box=box.ROUNDED,
        ))

    def load_course_from_file(self):
        """Load a course from a file."""
        self.console.print()

        # List available course files
        course_files = list(self.output_dir.glob("course_*.json"))

        if not course_files:
            self.console.print("[yellow]No saved courses found in output directory[/yellow]")
            filepath = Prompt.ask("[cyan]Enter course file path[/cyan]")
        else:
            table = Table(show_header=True, box=box.ROUNDED, border_style="cyan")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Filename", style="white")
            table.add_column("Modified", style="dim")

            for i, file in enumerate(course_files, 1):
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                table.add_row(
                    str(i),
                    file.name,
                    mtime.strftime("%Y-%m-%d %H:%M")
                )

            self.console.print(Panel(
                table,
                title="[bold cyan]Available Courses[/bold cyan]",
                border_style="cyan",
            ))

            choice = Prompt.ask(
                "\n[cyan]Enter course number or custom path[/cyan]",
                default="1"
            )

            if choice.isdigit() and 1 <= int(choice) <= len(course_files):
                filepath = course_files[int(choice) - 1]
            else:
                filepath = Path(choice)

        try:
            self.current_course = Course.from_json_file(filepath)

            self.console.print()
            self.console.print(Panel(
                f"[green]✓ Course loaded successfully![/green]\n\n"
                f"[bold]Title:[/bold] {self.current_course.title}\n"
                f"[bold]Lessons:[/bold] {len(self.current_course.lessons)}",
                border_style="green",
                box=box.ROUNDED,
            ))

        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[red]✗ Error loading course[/red]\n\n{str(e)}",
                border_style="red",
                box=box.ROUNDED,
            ))

    def show_settings(self):
        """Show current settings."""
        self.console.print()

        settings = Table.grid(padding=(0, 2))
        settings.add_column(style="bold cyan")
        settings.add_column(style="white")

        settings.add_row("Output Directory:", str(self.output_dir))
        settings.add_row("Available Models:", ", ".join(self.config.models.keys()))

        for task, model_config in self.config.models.items():
            settings.add_row("", "")
            settings.add_row(f"{task.title()} Model:", "")
            settings.add_row("  Model ID:", model_config.model_id)
            settings.add_row("  Temperature:", str(model_config.temperature))
            settings.add_row("  Max Tokens:", str(model_config.max_tokens))

        self.console.print(Panel(
            settings,
            title="[bold cyan]Settings[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        ))

    def run(self):
        """Run the main application loop."""
        self.show_header()

        # Initialize LLMs
        try:
            self.initialize_llms()
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error initializing AI models[/red]\n\n"
                f"{str(e)}\n\n"
                "Make sure you have set up your API keys in .env file",
                border_style="red",
                box=box.ROUNDED,
            ))
            return

        while True:
            self.console.print()
            choice = self.show_main_menu()

            if choice == "0":
                self.console.print()
                self.console.print(Panel(
                    "[cyan]Thanks for using Recollection! 🎓[/cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                ))
                break
            elif choice == "1":
                self.load_content()
            elif choice == "2":
                self.view_content()
            elif choice == "3":
                self.generate_course_ui()
            elif choice == "4":
                self.view_course()
            elif choice == "5":
                self.save_course()
            elif choice == "6":
                self.load_course_from_file()
            elif choice == "7":
                self.show_settings()

            # Pause before showing menu again
            if choice != "0":
                self.console.print()
                Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def main():
    """Entry point for the TUI application."""
    app = RecollectionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Application interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Unexpected error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    main()
