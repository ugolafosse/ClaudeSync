#!/usr/bin/env python3
"""
ExcaClean - A standalone tool to process Excalidraw data from markdown files
Requirements: pip install click rich pyperclip
"""

import click
import os
import re
import shutil
import pyperclip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()

def filter_excalidraw_data(text):
    """Remove Excalidraw data sections from the text."""
    pattern = r'#\s*Excalidraw Data[\s\S]*$'
    filtered_text = re.sub(pattern, '', text)
    return filtered_text

def process_file(file_path):
    """Process a single file to remove Excalidraw data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only process markdown files
        if not file_path.name.endswith('.md'):
            return content, False
        
        filtered_content = filter_excalidraw_data(content)
        has_excalidraw = filtered_content != content
        return filtered_content, has_excalidraw
    except Exception as e:
        console.print(f"[red]Error processing {file_path}: {str(e)}[/red]")
        return None, False

def process_directory(src_dir, dest_dir, progress):
    """Process all files in a directory, preserving structure."""
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    processed_files = 0
    excalidraw_found = 0
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Copy directory structure
    for dirpath, dirnames, filenames in os.walk(src_path):
        rel_path = Path(dirpath).relative_to(src_path)
        dest_dir = dest_path / rel_path
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in filenames:
            src_file = Path(dirpath) / filename
            dest_file = dest_dir / filename
            
            filtered_content, has_excalidraw = process_file(src_file)
            if filtered_content is not None:
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(filtered_content)
                processed_files += 1
                if has_excalidraw:
                    excalidraw_found += 1
                progress.update(task_id, advance=1, description=f"Processing: {rel_path / filename}")
    
    return processed_files, excalidraw_found

def concatenate_files(src_dir, progress):
    """Concatenate all files into one markdown string with headers."""
    src_path = Path(src_dir)
    result = []
    processed_files = 0
    excalidraw_found = 0
    
    for dirpath, dirnames, filenames in os.walk(src_path):
        rel_path = Path(dirpath).relative_to(src_path)
        
        for filename in filenames:
            src_file = Path(dirpath) / filename
            file_rel_path = rel_path / filename
            
            filtered_content, has_excalidraw = process_file(src_file)
            if filtered_content is not None:
                result.append(f"\n\n# File: {file_rel_path}\n\n{filtered_content}")
                processed_files += 1
                if has_excalidraw:
                    excalidraw_found += 1
                progress.update(task_id, advance=1, description=f"Processing: {file_rel_path}")
    
    return "\n".join(result), processed_files, excalidraw_found

@click.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--mode', '-m', type=click.Choice(['duplicate', 'noxk', 'concat']), 
              default='duplicate', help='Processing mode')
def main(source_dir, mode):
    """ExcaClean: Process Excalidraw data from markdown files in different ways.
    
    SOURCE_DIR: The directory containing your markdown files
    
    Modes:
    - duplicate: Create exact copy of directory structure without Excalidraw data (default)
    - noxk: Create new directory with -NoXK suffix
    - concat: Concatenate all files into one and copy to clipboard
    
    Example usage:
    ./excaclean.py ~/my-notes -m concat
    """
    source_dir = Path(source_dir)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        # Count total files for progress bar
        total_files = sum(1 for _ in source_dir.rglob('*') if _.is_file())
        global task_id  # Used in process functions
        task_id = progress.add_task("Processing...", total=total_files)
        
        if mode in ['duplicate', 'noxk']:
            # Determine destination directory
            if mode == 'duplicate':
                dest_dir = source_dir.parent / f"{source_dir.name}-clean"
            else:
                dest_dir = source_dir.parent / f"{source_dir.name}-NoXK"
            
            # Process files
            processed_files, excalidraw_found = process_directory(source_dir, dest_dir, progress)
            
            # Show results
            console.print(f"\n[green]✓[/green] Processed {processed_files} files")
            if excalidraw_found > 0:
                console.print(f"[yellow]🎨 Removed Excalidraw data from {excalidraw_found} files[/yellow]")
            console.print(f"[blue]📁 Output directory: {dest_dir}[/blue]")
            
        else:  # concat mode
            # Concatenate files
            result, processed_files, excalidraw_found = concatenate_files(source_dir, progress)
            
            # Copy to clipboard
            pyperclip.copy(result)
            
            # Show results
            console.print(f"\n[green]✓[/green] Processed {processed_files} files")
            if excalidraw_found > 0:
                console.print(f"[yellow]🎨 Removed Excalidraw data from {excalidraw_found} files[/yellow]")
            console.print("[blue]📋 Concatenated content copied to clipboard[/blue]")

if __name__ == '__main__':
    main() 