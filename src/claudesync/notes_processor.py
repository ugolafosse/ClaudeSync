import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def filter_excalidraw_data(text):
    """
    Remove Excalidraw data sections from the text.
    
    This function removes everything from '# Excalidraw Data' heading to the end of the file.
    
    Args:
        text (str): The text to filter
        
    Returns:
        str: The filtered text with Excalidraw data and everything after it removed
    """
    logger.debug("Original text length: %d", len(text))
    # Pattern to match '# Excalidraw Data' and everything that follows until the end of the file
    pattern = r'#\s*Excalidraw Data[\s\S]*$'
    filtered_text = re.sub(pattern, '', text)
    logger.debug("Filtered text length: %d", len(filtered_text))
    if filtered_text != text:
        logger.info("\033[33m🎨 Excalidraw data found and removed from text\033[0m")  # Yellow color
    return filtered_text

def process_note_file(file_path):
    """
    Process a single note file to remove Excalidraw data.
    
    Args:
        file_path (str or Path): Path to the note file
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
        
    # Read the original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Filter out Excalidraw data
    filtered_content = filter_excalidraw_data(original_content)
    
    # If content changed, save it back
    if filtered_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(filtered_content)
        logger.info(f"\033[33m🎨 Removed Excalidraw data from {file_path}\033[0m")  # Yellow color
        return True
    return False 