"""
Thanatos UI - Separate interface for the advanced AI security expert.

Accessible after unlocking through course completion.
"""

import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from .ai.thanatos import Thanatos
from .core import Necronomicon, ProgressTracker


class ThanatosUI:
    """Separate UI for Thanatos advanced AI assistant."""
    
    def __init__(self):
        """Initialize Thanatos UI."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Initialize Necronomicon for progress checking
        courses_dir = Path(__file__).parent / "lessons"
        data_dir = Path(__file__).parent / "data"
        
        self.necronomicon = Necronomicon(
            courses_dir=str(courses_dir),
            data_dir=str(data_dir)
        )
        
        # Initialize Thanatos
        self.thanatos = Thanatos()
        
        # Check unlock status
        self._check_unlock()
    
    def _check_unlock(self):
        """Check if Thanatos is unlocked."""
        unlocked, message = self.thanatos.check_unlock_status(
            self.necronomicon.progress_tracker
        )
        if not unlocked:
            self.locked_message = message
        else:
            self.locked_message = None
    
    def run(self):
        """Main Thanatos UI loop."""
        try:
            if not self.thanatos.unlocked:
                self.show_locked_screen()
                return
            
            self.show_main_chat()
        except KeyboardInterrupt:
            self.show_exit_message()
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_locked_screen(self):
        """Show locked screen if Thanatos is not unlocked."""
        if not RICH_AVAILABLE:
            print("\n" + "=" * 60)
            print("THANATOS - Advanced Security Expert")
            print("=" * 60)
            print()
            print("🔒 LOCKED")
            print()
            print(self.locked_message)
            print()
            print("Complete the basic course to unlock Thanatos.")
            print()
            input("Press Enter to return...")
            return
        
        self.console.clear()
        
        locked_panel = Panel(
            f"[bold red]🔒 THANATOS IS LOCKED[/bold red]\n\n"
            f"{self.locked_message}\n\n"
            f"[dim]Complete the 'basics_01_introduction' course to unlock advanced security expertise.[/dim]",
            title="[bold yellow]Access Denied[/bold yellow]",
            border_style="red"
        )
        self.console.print(locked_panel)
        
        Prompt.ask("\n[dim]Press Enter to return[/dim]", default="")
    
    def show_main_chat(self):
        """Display main chat interface with Thanatos."""
        if not RICH_AVAILABLE:
            self._show_main_chat_basic()
            return
        
        self.console.clear()
        
        # Header
        header = Panel(
            "[bold red]THANATOS[/bold red] - Advanced Security Expert\n[dim]Expert-level security guidance and penetration testing assistance[/dim]",
            border_style="red"
        )
        self.console.print(header)
        self.console.print()
        
        # Warning panel
        warning_panel = Panel(
            "[bold yellow]⚠️ ETHICAL USE ONLY[/bold yellow]\n\n"
            "Thanatos provides guidance for:\n"
            "- Authorized security testing only\n"
            "- Systems you own or have explicit permission to test\n"
            "- Educational and research purposes\n"
            "- Responsible disclosure practices\n\n"
            "[dim]Unauthorized access to computer systems is illegal.[/dim]",
            border_style="yellow"
        )
        self.console.print(warning_panel)
        self.console.print()
        
        # Chat loop
        while True:
            self.console.print()
            user_input = Prompt.ask("[bold red]You[/bold red] (or 'exit' to quit)")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            if not user_input.strip():
                continue
            
            # Show thinking indicator
            with self.console.status("[bold yellow]Thanatos is analyzing...[/bold yellow]"):
                response = self.thanatos.query(user_input)
            
            # Display response
            response_panel = Panel(
                Markdown(response),
                title="[bold red]Thanatos[/bold red]",
                border_style="red"
            )
            self.console.print(response_panel)
    
    def _show_main_chat_basic(self):
        """Fallback basic chat interface."""
        print("\n" + "=" * 60)
        print("THANATOS - Advanced Security Expert")
        print("=" * 60)
        print()
        print("⚠️ ETHICAL USE ONLY")
        print("Only use for authorized security testing!")
        print()
        print("Ask questions about security (type 'exit' to quit):\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            if not user_input:
                continue
            
            print("\nThanatos: ", end="")
            response = self.thanatos.query(user_input)
            print(response)
            print()
    
    def show_exit_message(self):
        """Show exit message."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold red]Thanatos has spoken. Farewell.[/bold red]\n")
        else:
            print("\nThanatos has spoken. Farewell.\n")
    
    def show_error(self, message: str):
        """Show error message."""
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold red]Error:[/bold red] {message}\n")
        else:
            print(f"\nError: {message}\n")


def main():
    """Entry point for Thanatos UI."""
    ui = ThanatosUI()
    ui.run()


if __name__ == "__main__":
    main()

