"""
Main CLI Interface for AI File Organization Agent
"""
import argparse
import os
import sys
import time
from pathlib import Path
from typing import List
import schedule
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from file_scanner import FileScanner
from categorizer import FileCategorizer
from duplicate_detector import DuplicateDetector
from organizer import FileOrganizer

console = Console()


class OrganizerAgent:
    """Main agent that coordinates all components"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.scanner = None
        self.categorizer = None
        self.duplicate_detector = None
        self.organizer = None
    
    def initialize(self):
        """Initialize all components"""
        try:
            self.categorizer = FileCategorizer()
            self.duplicate_detector = DuplicateDetector()
            self.organizer = FileOrganizer()
            console.print("[green]✓[/green] Components initialized")
        except Exception as e:
            console.print(f"[red]Error initializing: {e}[/red]")
            sys.exit(1)
    
    def scan_and_organize(self, directories: List[str], interactive: bool = True):
        """Main workflow: scan, categorize, detect duplicates, and organize"""
        console.print(Panel.fit("[bold blue]AI File Organization Agent[/bold blue]"))
        
        # Step 1: Scan files
        console.print("\n[cyan]Step 1:[/cyan] Scanning directories...")
        self.scanner = FileScanner(directories, compute_hash=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ):
            files = self.scanner.scan()
        
        console.print(f"[green]Found {len(files)} files[/green]")
        
        if not files:
            console.print("[yellow]No files found to organize[/yellow]")
            return
        
        # Step 2: Detect duplicates
        console.print("\n[cyan]Step 2:[/cyan] Detecting duplicates...")
        duplicates = self.duplicate_detector.find_duplicates(files)
        duplicate_summary = self.duplicate_detector.get_duplicate_summary()
        
        if duplicates:
            console.print(f"[yellow]Found {duplicate_summary['duplicate_groups']} duplicate groups[/yellow]")
            console.print(f"[yellow]Potential space savings: {duplicate_summary['total_wasted_space_mb']} MB[/yellow]")
            
            if interactive:
                self._handle_duplicates(duplicates)
        else:
            console.print("[green]No duplicates found[/green]")
        
        # Step 3: Categorize files
        console.print("\n[cyan]Step 3:[/cyan] Categorizing files with AI...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ):
            categorizations = self.categorizer.categorize_files(files)
        
        # Show categorization preview
        self._show_categorization_preview(categorizations)
        
        # Step 4: Organize files
        if interactive:
            if not self._confirm_organization(categorizations):
                console.print("[yellow]Organization cancelled by user[/yellow]")
                return
        
        console.print("\n[cyan]Step 4:[/cyan] Organizing files...")
        
        if self.dry_run:
            console.print("[yellow]DRY RUN MODE - No files will be moved[/yellow]")
            self._show_dry_run_preview(files, categorizations)
        else:
            moved_files = self.organizer.organize_by_category(
                files,
                categorizations,
                organize_by_date=True,
                organize_by_project=True
            )
            
            summary = self.organizer.get_organization_summary()
            console.print(f"\n[green]✓ Organized {summary['successful']} files successfully[/green]")
            if summary['failed'] > 0:
                console.print(f"[red]✗ Failed to organize {summary['failed']} files[/red]")
            
            console.print(f"[blue]Files organized to: {summary['organize_directory']}[/blue]")
    
    def _handle_duplicates(self, duplicates: dict):
        """Handle duplicate files with user interaction"""
        suggestions = self.duplicate_detector.suggest_cleanup(duplicates)
        
        table = Table(title="Duplicate Files")
        table.add_column("Keep", style="green")
        table.add_column("Remove", style="red")
        table.add_column("Reason")
        
        for suggestion in suggestions[:10]:  # Show first 10
            keep = suggestion["keep"]
            remove_list = suggestion["remove"]
            table.add_row(
                str(keep.path),
                "\n".join(str(r.path) for r in remove_list[:3]),
                suggestion["reason"]
            )
        
        console.print(table)
        
        response = console.input("\n[yellow]Would you like to remove duplicates? (y/n): [/yellow]")
        if response.lower() == 'y':
            # In a real implementation, you'd delete the files here
            console.print("[yellow]Duplicate removal not implemented in this version[/yellow]")
    
    def _show_categorization_preview(self, categorizations: dict):
        """Show preview of file categorizations"""
        # Count by category
        category_counts = {}
        for file, cat_info in categorizations.items():
            category = cat_info.get("category", "Other")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        table = Table(title="File Categorization Preview")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")
        
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            table.add_row(category, str(count))
        
        console.print(table)
    
    def _confirm_organization(self, categorizations: dict) -> bool:
        """Ask user to confirm organization"""
        console.print("\n[yellow]Ready to organize files. This will move files to organized folders.[/yellow]")
        response = console.input("[yellow]Continue? (y/n): [/yellow]")
        return response.lower() == 'y'
    
    def _show_dry_run_preview(self, files: List, categorizations: dict):
        """Show what would happen in dry run mode"""
        table = Table(title="Dry Run Preview - Files to be Organized")
        table.add_column("Source", style="cyan")
        table.add_column("Category", style="green")
        table.add_column("Destination", style="blue")
        
        for file, cat_info in list(categorizations.items())[:20]:  # Show first 20
            category = cat_info.get("category", "Other")
            dest = self.organizer.organize_dir / category / file.name
            table.add_row(str(file.path), category, str(dest))
        
        console.print(table)
        if len(categorizations) > 20:
            console.print(f"[dim]... and {len(categorizations) - 20} more files[/dim]")


def run_scheduled(directories: List[str], frequency: str):
    """Run organizer on a schedule"""
    agent = OrganizerAgent(dry_run=False)
    agent.initialize()
    
    def job():
        console.print(f"\n[cyan]Running scheduled organization at {time.strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")
        agent.scan_and_organize(directories, interactive=False)
    
    # Schedule based on frequency
    if frequency == "hourly":
        schedule.every().hour.do(job)
    elif frequency == "daily":
        schedule.every().day.at("02:00").do(job)
    elif frequency == "weekly":
        schedule.every().week.do(job)
    else:
        console.print(f"[red]Unknown frequency: {frequency}[/red]")
        return
    
    console.print(f"[green]Scheduled to run {frequency}[/green]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        console.print("\n[yellow]Scheduler stopped[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="AI File Organization Agent")
    parser.add_argument(
        "--scan",
        nargs="+",
        help="Directories to scan and organize",
        default=["Downloads", "Desktop"]
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with prompts"
    )
    parser.add_argument(
        "--schedule",
        choices=["hourly", "daily", "weekly"],
        help="Schedule automatic runs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--config",
        help="Path to config file (not implemented)"
    )
    
    args = parser.parse_args()
    
    # Convert directory names to full paths
    directories = []
    home = Path.home()
    
    for dir_name in args.scan:
        if Path(dir_name).is_absolute():
            directories.append(dir_name)
        else:
            # Try common locations (Windows and Unix)
            possible_paths = [
                home / dir_name,
                Path(dir_name),
                # Windows-specific paths
                Path(os.path.expanduser(f"~/{dir_name}")),
                # Try with capital first letter (Windows)
                home / dir_name.capitalize(),
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_paths = []
            for path in possible_paths:
                path_str = str(path)
                if path_str not in seen:
                    seen.add(path_str)
                    unique_paths.append(path)
            
            found = False
            for path in unique_paths:
                if path.exists() and path.is_dir():
                    directories.append(str(path))
                    found = True
                    break
            
            if not found:
                console.print(f"[yellow]Warning: Directory {dir_name} not found, skipping...[/yellow]")
    
    if not directories:
        console.print("[red]No valid directories to scan[/red]")
        sys.exit(1)
    
    # Run scheduled or one-time
    if args.schedule:
        run_scheduled(directories, args.schedule)
    else:
        agent = OrganizerAgent(dry_run=args.dry_run)
        agent.initialize()
        agent.scan_and_organize(directories, interactive=args.interactive or not args.dry_run)


if __name__ == "__main__":
    main()

