"""
Necronomicon Text-Based User Interface

Implements a professional text-based UI using the Rich library for the
Necronomicon learning system. All processing happens locally, no network required.
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: Rich library not available. Install with: pip install rich")
    # Fallback to basic print
    Console = None

from .core import Necronomicon, Course, Lesson, Challenge, LessonStatus
from .ai.benjamin import HackBenjamin


class NecronomiconUI:
    """Text-based user interface for Necronomicon learning system."""
    
    def __init__(self):
        """Initialize UI with Rich console."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Initialize Necronomicon system
        courses_dir = Path(__file__).parent / "lessons"
        data_dir = Path(__file__).parent / "data"
        
        self.necronomicon = Necronomicon(
            courses_dir=str(courses_dir),
            data_dir=str(data_dir)
        )
        
        # Initialize Hack Benjamin AI assistant
        self.benjamin = HackBenjamin()
        
        self.current_course: Optional[Course] = None
        self.current_lesson: Optional[Lesson] = None
        self.running = True
    
    def run(self):
        """Main UI loop."""
        try:
            while self.running:
                self.show_main_menu()
        except KeyboardInterrupt:
            self.show_exit_message()
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_main_menu(self):
        """Display main menu and handle user selection."""
        if not RICH_AVAILABLE:
            self._show_main_menu_basic()
            return
        
        self.console.clear()
        
        # Create header
        header = Panel(
            "[bold cyan]NECRONOMICON[/bold cyan]\n[dim]The Reaper Learning System[/dim]",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print()
        
        # Main menu options
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_row("[bold]1.[/bold]", "Browse Courses")
        menu_table.add_row("[bold]2.[/bold]", "Continue Learning")
        menu_table.add_row("[bold]3.[/bold]", "Progress Dashboard")
        menu_table.add_row("[bold]4.[/bold]", "Ask Hack Benjamin (AI Tutor)")
        menu_table.add_row("[bold]5.[/bold]", "Help & Documentation")
        menu_table.add_row("[bold]6.[/bold]", "Exit")
        
        self.console.print(menu_table)
        self.console.print()
        
        choice = Prompt.ask(
            "[bold cyan]Select an option[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        if choice == "1":
            self.show_course_browser()
        elif choice == "2":
            self.show_continue_learning()
        elif choice == "3":
            self.show_progress_dashboard()
        elif choice == "4":
            self.show_benjamin_chat()
        elif choice == "5":
            self.show_help()
        elif choice == "6":
            self.running = False
            self.show_exit_message()
    
    def _show_main_menu_basic(self):
        """Fallback basic menu without Rich."""
        print("\n" + "=" * 60)
        print("NECRONOMICON - The Reaper Learning System")
        print("=" * 60)
        print("1. Browse Courses")
        print("2. Continue Learning")
        print("3. Progress Dashboard")
        print("4. Ask Hack Benjamin (AI Tutor)")
        print("5. Help & Documentation")
        print("6. Exit")
        print()
        choice = input("Select an option [1-6]: ").strip()
        
        if choice == "1":
            self.show_course_browser()
        elif choice == "2":
            self.show_continue_learning()
        elif choice == "3":
            self.show_progress_dashboard()
        elif choice == "4":
            self.show_benjamin_chat()
        elif choice == "5":
            self.show_help()
        elif choice == "6":
            self.running = False
    
    def show_course_browser(self):
        """Display available courses."""
        if not RICH_AVAILABLE:
            self._show_course_browser_basic()
            return
        
        self.console.clear()
        
        courses = self.necronomicon.list_courses()
        
        if not courses:
            self.console.print("[yellow]No courses available yet.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
            return
        
        # Course list table
        table = Table(title="[bold cyan]Available Courses[/bold cyan]")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Difficulty", style="yellow")
        table.add_column("Duration", style="green")
        table.add_column("Progress", style="blue")
        
        for course in courses:
            progress = self.necronomicon.progress_tracker.get_course_progress(course.id)
            table.add_row(
                course.id,
                course.title,
                course.difficulty,
                f"{course.estimated_duration} min",
                f"{progress:.0f}%"
            )
        
        self.console.print(table)
        self.console.print()
        
        choices = [str(i+1) for i in range(len(courses))] + ["b"]
        choice = Prompt.ask(
            "[bold cyan]Select a course[/bold cyan] (or 'b' to go back)",
            choices=choices,
            default="b"
        )
        
        if choice != "b" and choice.isdigit():
            course_idx = int(choice) - 1
            if 0 <= course_idx < len(courses):
                self.current_course = courses[course_idx]
                self.show_course_detail()
        elif choice == "b":
            pass  # Return to main menu
    
    def _show_course_browser_basic(self):
        """Fallback basic course browser."""
        courses = self.necronomicon.list_courses()
        
        if not courses:
            print("\nNo courses available yet.\n")
            input("Press Enter to continue...")
            return
        
        print("\n" + "=" * 60)
        print("Available Courses")
        print("=" * 60)
        
        for i, course in enumerate(courses, 1):
            progress = self.necronomicon.progress_tracker.get_course_progress(course.id)
            print(f"{i}. {course.title} ({course.difficulty}) - {progress:.0f}%")
        
        print("\n0. Back")
        choice = input("Select: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(courses):
            self.current_course = courses[int(choice) - 1]
            self.show_course_detail()
    
    def show_course_detail(self):
        """Show course details and lessons."""
        if not self.current_course:
            return
        
        if not RICH_AVAILABLE:
            self._show_course_detail_basic()
            return
        
        self.console.clear()
        
        # Course header
        header = Panel(
            f"[bold cyan]{self.current_course.title}[/bold cyan]\n\n"
            f"[dim]{self.current_course.description}[/dim]",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print()
        
        # Lessons table
        lessons_table = Table(title="[bold cyan]Lessons[/bold cyan]")
        lessons_table.add_column("#", style="cyan", width=4)
        lessons_table.add_column("Title", style="magenta")
        lessons_table.add_column("Time", style="yellow")
        lessons_table.add_column("Status", style="green")
        
        for lesson in self.current_course.lessons:
            status = self.necronomicon.progress_tracker.get_lesson_status(lesson.id)
            status_text = {
                LessonStatus.LOCKED: "[red]🔒 Locked[/red]",
                LessonStatus.AVAILABLE: "[yellow]📖 Available[/yellow]",
                LessonStatus.IN_PROGRESS: "[blue]▶ In Progress[/blue]",
                LessonStatus.COMPLETED: "[green]✅ Completed[/green]"
            }.get(status, "[dim]Unknown[/dim]")
            
            lessons_table.add_row(
                str(lesson.order),
                lesson.title,
                f"{lesson.estimated_time} min",
                status_text
            )
        
        self.console.print(lessons_table)
        self.console.print()
        
        choices = [str(i+1) for i in range(len(self.current_course.lessons))] + ["b", "s"]
        choice = Prompt.ask(
            "[bold cyan]Select a lesson[/bold cyan] (or 'b' to go back, 's' to start course)",
            choices=choices,
            default="b"
        )
        
        if choice.isdigit():
            lesson_idx = int(choice) - 1
            if 0 <= lesson_idx < len(self.current_course.lessons):
                self.current_lesson = self.current_course.lessons[lesson_idx]
                self.show_lesson()
        elif choice == "s":
            # Start from first available lesson
            for lesson in self.current_course.lessons:
                status = self.necronomicon.progress_tracker.get_lesson_status(lesson.id)
                if status != LessonStatus.LOCKED:
                    self.current_lesson = lesson
                    self.show_lesson()
                    break
    
    def _show_course_detail_basic(self):
        """Fallback basic course detail."""
        if not self.current_course:
            return
        
        print("\n" + "=" * 60)
        print(self.current_course.title)
        print("=" * 60)
        print(self.current_course.description)
        print()
        print("Lessons:")
        
        for i, lesson in enumerate(self.current_course.lessons, 1):
            status = self.necronomicon.progress_tracker.get_lesson_status(lesson.id)
            print(f"  {i}. {lesson.title} ({lesson.estimated_time} min) - {status.value}")
        
        print("\n0. Back")
        choice = input("Select lesson: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(self.current_course.lessons):
            self.current_lesson = self.current_course.lessons[int(choice) - 1]
            self.show_lesson()
    
    def show_lesson(self):
        """Display lesson content and handle interaction."""
        if not self.current_lesson:
            return
        
        if not RICH_AVAILABLE:
            self._show_lesson_basic()
            return
        
        self.console.clear()
        
        # Lesson header
        header = Panel(
            f"[bold cyan]{self.current_lesson.title}[/bold cyan]\n\n"
            f"[dim]{self.current_lesson.description}[/dim]",
            border_style="cyan"
        )
        self.console.print(header)
        self.console.print()
        
        # Lesson content (markdown)
        if self.current_lesson.content:
            content = Markdown(self.current_lesson.content)
            self.console.print(content)
            self.console.print()
        
        # Code example
        if self.current_lesson.code_example:
            code_panel = Panel(
                self.current_lesson.code_example,
                title="[bold]Example Code[/bold]",
                border_style="green"
            )
            self.console.print(code_panel)
            self.console.print()
        
        # Challenge if available
        if self.current_lesson.challenge:
            challenge_panel = Panel(
                f"[bold yellow]{self.current_lesson.challenge.description}[/bold yellow]\n\n"
                f"[dim]Type: {self.current_lesson.challenge.type.value}[/dim]",
                title="[bold]Challenge[/bold]",
                border_style="yellow"
            )
            self.console.print(challenge_panel)
            self.console.print()
            
            if Confirm.ask("[bold cyan]Try the challenge?[/bold cyan]"):
                self.show_challenge()
        
        # Navigation
        choices = ["n", "p", "b"]
        choice = Prompt.ask(
            "[bold cyan]Next (n) | Previous (p) | Back (b)[/bold cyan]",
            choices=choices,
            default="b"
        )
        
        if choice == "n":
            self._next_lesson()
        elif choice == "p":
            self._previous_lesson()
        elif choice == "b":
            self.show_course_detail()
    
    def _show_lesson_basic(self):
        """Fallback basic lesson display."""
        if not self.current_lesson:
            return
        
        print("\n" + "=" * 60)
        print(self.current_lesson.title)
        print("=" * 60)
        print(self.current_lesson.description)
        print()
        print(self.current_lesson.content)
        print()
        
        if self.current_lesson.code_example:
            print("Example Code:")
            print("-" * 60)
            print(self.current_lesson.code_example)
            print()
        
        if self.current_lesson.challenge:
            print("Challenge:")
            print(self.current_lesson.challenge.description)
            print()
            if input("Try challenge? (y/n): ").lower() == "y":
                self.show_challenge()
        
        input("\nPress Enter to continue...")
    
    def show_challenge(self):
        """Display and handle code challenge."""
        if not self.current_lesson or not self.current_lesson.challenge:
            return
        
        challenge = self.current_lesson.challenge
        
        if not RICH_AVAILABLE:
            self._show_challenge_basic()
            return
        
        self.console.clear()
        
        # Challenge description
        challenge_panel = Panel(
            Markdown(challenge.description),
            title="[bold yellow]Challenge[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(challenge_panel)
        self.console.print()
        
        # Starter code
        if challenge.starter_code:
            starter_panel = Panel(
                challenge.starter_code,
                title="[bold]Starter Code[/bold]",
                border_style="green"
            )
            self.console.print(starter_panel)
            self.console.print()
        
        # Get user code input
        self.console.print("[bold cyan]Enter your code (end with blank line):[/bold cyan]")
        user_code_lines = []
        while True:
            line = input()
            if line.strip() == "" and user_code_lines:
                break
            user_code_lines.append(line)
        
        user_code = "\n".join(user_code_lines)
        
        # Validate challenge
        passed, feedback, score = self.necronomicon.validate_challenge(challenge, user_code)
        
        # Show results
        if passed:
            result_panel = Panel(
                f"[bold green]✅ Challenge Passed![/bold green]\n\n"
                f"Score: {score:.0f}%\n\n"
                f"{feedback}",
                border_style="green"
            )
        else:
            result_panel = Panel(
                f"[bold red]❌ Challenge Failed[/bold red]\n\n"
                f"Score: {score:.0f}%\n\n"
                f"{feedback}",
                border_style="red"
            )
        
        self.console.print(result_panel)
        
        if passed:
            # Mark lesson as completed
            self.necronomicon.progress_tracker.mark_lesson_completed(
                self.current_lesson.id,
                self.current_course.id,
                score
            )
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def _show_challenge_basic(self):
        """Fallback basic challenge display."""
        challenge = self.current_lesson.challenge
        
        print("\n" + "=" * 60)
        print("Challenge")
        print("=" * 60)
        print(challenge.description)
        print()
        
        if challenge.starter_code:
            print("Starter Code:")
            print("-" * 60)
            print(challenge.starter_code)
            print()
        
        print("Enter your code (end with blank line):")
        user_code_lines = []
        while True:
            line = input()
            if line.strip() == "" and user_code_lines:
                break
            user_code_lines.append(line)
        
        user_code = "\n".join(user_code_lines)
        
        passed, feedback, score = self.necronomicon.validate_challenge(challenge, user_code)
        
        if passed:
            print(f"\n✅ Challenge Passed! Score: {score:.0f}%")
            self.necronomicon.progress_tracker.mark_lesson_completed(
                self.current_lesson.id,
                self.current_course.id,
                score
            )
        else:
            print(f"\n❌ Challenge Failed. Score: {score:.0f}%")
            print(feedback)
        
        input("\nPress Enter to continue...")
    
    def show_progress_dashboard(self):
        """Display progress dashboard."""
        if not RICH_AVAILABLE:
            print("\nProgress Dashboard")
            print("=" * 60)
            print("Feature coming soon...\n")
            input("Press Enter to continue...")
            return
        
        self.console.clear()
        
        # Progress table
        table = Table(title="[bold cyan]Your Progress[/bold cyan]")
        table.add_column("Course", style="magenta")
        table.add_column("Progress", style="blue")
        table.add_column("Status", style="green")
        
        courses = self.necronomicon.list_courses()
        for course in courses:
            progress = self.necronomicon.progress_tracker.get_course_progress(course.id)
            status = "✅ Completed" if progress >= 100 else "📖 In Progress" if progress > 0 else "🔒 Not Started"
            table.add_row(
                course.title,
                f"{progress:.0f}%",
                status
            )
        
        self.console.print(table)
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def show_continue_learning(self):
        """Show courses/lessons in progress."""
        if not RICH_AVAILABLE:
            print("\nContinue Learning")
            print("=" * 60)
            print("Feature coming soon...\n")
            input("Press Enter to continue...")
            return
        
        self.console.print("[yellow]Continue Learning feature coming soon...[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def show_benjamin_chat(self):
        """Display chat interface with Hack Benjamin."""
        if not RICH_AVAILABLE:
            self._show_benjamin_chat_basic()
            return
        
        self.console.clear()
        
        # Header
        header = Panel(
            "[bold cyan]Hack Benjamin[/bold cyan] - Your AI Tutor\n[dim]Ask me anything about Reaper![/dim]",
            border_style="cyan"
        )
        self.console.print(header)
        self.console.print()
        
        # Set context for Benjamin
        if self.current_course:
            self.benjamin.set_context("current_course", self.current_course.title)
        if self.current_lesson:
            self.benjamin.set_context("current_lesson", self.current_lesson.title)
        
        # Chat loop
        while True:
            self.console.print()
            user_input = Prompt.ask("[bold green]You[/bold green] (or 'exit' to go back)")
            
            if user_input.lower() in ['exit', 'quit', 'back', 'b']:
                break
            
            if not user_input.strip():
                continue
            
            # Show thinking indicator
            with self.console.status("[bold yellow]Benjamin is thinking...[/bold yellow]"):
                response = self.benjamin.query(user_input)
            
            # Display response
            response_panel = Panel(
                response,
                title="[bold cyan]Hack Benjamin[/bold cyan]",
                border_style="cyan"
            )
            self.console.print(response_panel)
    
    def _show_benjamin_chat_basic(self):
        """Fallback basic chat interface."""
        print("\n" + "=" * 60)
        print("Hack Benjamin - Your AI Tutor")
        print("=" * 60)
        print("Ask me anything about Reaper! (type 'exit' to go back)\n")
        
        if self.current_course:
            self.benjamin.set_context("current_course", self.current_course.title)
        if self.current_lesson:
            self.benjamin.set_context("current_lesson", self.current_lesson.title)
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'back']:
                break
            
            if not user_input:
                continue
            
            print("\nBenjamin: ", end="")
            response = self.benjamin.query(user_input)
            print(response)
            print()
    
    def show_help(self):
        """Display help and documentation."""
        help_text = """
# Necronomicon Help

## Navigation
- Use number keys or type commands to navigate
- Press 'b' to go back
- Press Ctrl+C to exit

## Features
- **Courses**: Structured learning paths
- **Lessons**: Step-by-step tutorials
- **Challenges**: Practice with code exercises
- **Progress Tracking**: Monitor your learning journey

## Getting Help
- Each lesson includes examples and explanations
- Challenges have hints available
- Use the AI assistant (Hack Benjamin) for additional help
        """
        
        if RICH_AVAILABLE:
            self.console.clear()
            self.console.print(Markdown(help_text))
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
        else:
            print("\n" + help_text)
            input("Press Enter to continue...")
    
    def _next_lesson(self):
        """Navigate to next lesson."""
        if not self.current_course or not self.current_lesson:
            return
        
        current_idx = self.current_course.lessons.index(self.current_lesson)
        if current_idx < len(self.current_course.lessons) - 1:
            self.current_lesson = self.current_course.lessons[current_idx + 1]
            self.show_lesson()
    
    def _previous_lesson(self):
        """Navigate to previous lesson."""
        if not self.current_course or not self.current_lesson:
            return
        
        current_idx = self.current_course.lessons.index(self.current_lesson)
        if current_idx > 0:
            self.current_lesson = self.current_course.lessons[current_idx - 1]
            self.show_lesson()
    
    def show_exit_message(self):
        """Show exit message."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold green]Thank you for using Necronomicon![/bold green]")
            self.console.print("[dim]Keep learning, keep coding![/dim]\n")
        else:
            print("\nThank you for using Necronomicon!")
            print("Keep learning, keep coding!\n")
    
    def show_error(self, message: str):
        """Show error message."""
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold red]Error:[/bold red] {message}\n")
        else:
            print(f"\nError: {message}\n")


def main():
    """Entry point for Necronomicon UI."""
    ui = NecronomiconUI()
    ui.run()


if __name__ == "__main__":
    main()

