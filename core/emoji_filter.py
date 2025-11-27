"""
Emoji Filter Utility

Automatically removes emojis from strings to prevent encoding issues on Windows.
"""

import re
import sys


def remove_emojis(text: str) -> str:
    """
    Remove all emojis and other Unicode symbols from text.
    
    Args:
        text: String that may contain emojis
        
    Returns:
        String with emojis removed
    """
    if not isinstance(text, str):
        return text
    
    # Pattern to match emojis and symbols
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002500-\U00002BEF"  # Chinese/Japanese/Korean chars
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "\u2705"  # checkmarks and symbols
        "\u2713"
        "\u2714"
        "\u274c"
        "\u274e"
        "]+", 
        flags=re.UNICODE
    )
    
    return emoji_pattern.sub('', text).strip()


def safe_print(*args, **kwargs):
    """
    Print function that automatically removes emojis.
    
    Usage same as regular print(), but filters emojis.
    """
    # Get encoding from kwargs or sys.stdout
    encoding = kwargs.pop('encoding', sys.stdout.encoding or 'utf-8')
    errors = kwargs.pop('errors', 'replace')
    
    # Process all arguments
    processed_args = []
    for arg in args:
        if isinstance(arg, str):
            # Remove emojis
            arg = remove_emojis(arg)
            # Encode to safe ASCII/UTF-8
            try:
                # Try to encode/decode to ensure compatibility
                arg_bytes = arg.encode(encoding, errors=errors)
                arg = arg_bytes.decode(encoding, errors=errors)
            except (UnicodeEncodeError, UnicodeDecodeError):
                # If encoding fails, use ASCII-safe replacement
                arg = arg.encode('ascii', errors='replace').decode('ascii')
        
        processed_args.append(arg)
    
    # Use regular print with processed args
    return print(*processed_args, **kwargs)


def safe_encode(text: str, encoding: str = 'utf-8', errors: str = 'replace') -> bytes:
    """
    Safely encode text, removing emojis first.
    
    Args:
        text: Text to encode
        encoding: Target encoding
        errors: Error handling strategy
        
    Returns:
        Encoded bytes
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove emojis first
    text = remove_emojis(text)
    
    try:
        return text.encode(encoding, errors=errors)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback to ASCII
        return text.encode('ascii', errors='replace')


def filter_for_windows(text: str) -> str:
    """
    Filter text for Windows compatibility.
    Removes problematic Unicode characters.
    
    Args:
        text: Text to filter
        
    Returns:
        Windows-compatible text
    """
    if sys.platform == 'win32':
        return remove_emojis(text)
    return text

