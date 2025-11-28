"""
String Utilities for REAPER

String manipulation and utility functions.
"""

from typing import List, Optional


def trim(text: str) -> str:
    """
    Remove leading and trailing whitespace.
    
    Args:
        text: String to trim
        
    Returns:
        Trimmed string
    """
    return text.strip()


def upper_case(text: str) -> str:
    """
    Convert string to uppercase.
    
    Args:
        text: String to convert
        
    Returns:
        Uppercase string
    """
    return text.upper()


def lower_case(text: str) -> str:
    """
    Convert string to lowercase.
    
    Args:
        text: String to convert
        
    Returns:
        Lowercase string
    """
    return text.lower()


def starts_with(text: str, prefix: str) -> bool:
    """
    Check if string starts with prefix.
    
    Args:
        text: String to check
        prefix: Prefix to check for
        
    Returns:
        True if string starts with prefix
    """
    return text.startswith(prefix)


def ends_with(text: str, suffix: str) -> bool:
    """
    Check if string ends with suffix.
    
    Args:
        text: String to check
        suffix: Suffix to check for
        
    Returns:
        True if string ends with suffix
    """
    return text.endswith(suffix)


def contains(text: str, substring: str) -> bool:
    """
    Check if string contains substring.
    
    Args:
        text: String to check
        substring: Substring to search for
        
    Returns:
        True if string contains substring
    """
    return substring in text


def replace_all(text: str, old: str, new: str) -> str:
    """
    Replace all occurrences of old with new.
    
    Args:
        text: String to modify
        old: Substring to replace
        new: Replacement string
        
    Returns:
        Modified string
    """
    return text.replace(old, new)


def split_string(text: str, delimiter: str = " ") -> List[str]:
    """
    Split string by delimiter.
    
    Args:
        text: String to split
        delimiter: Delimiter to split on (default: space)
        
    Returns:
        List of substrings
    """
    return text.split(delimiter)


def join_strings(strings: List[str], delimiter: str = " ") -> str:
    """
    Join list of strings with delimiter.
    
    Args:
        strings: List of strings to join
        delimiter: Delimiter to join with (default: space)
        
    Returns:
        Joined string
    """
    return delimiter.join(strings)


def pad_left(text: str, width: int, pad_char: str = " ") -> str:
    """
    Pad string on the left.
    
    Args:
        text: String to pad
        width: Target width
        pad_char: Character to pad with (default: space)
        
    Returns:
        Padded string
    """
    return text.rjust(width, pad_char)


def pad_right(text: str, width: int, pad_char: str = " ") -> str:
    """
    Pad string on the right.
    
    Args:
        text: String to pad
        width: Target width
        pad_char: Character to pad with (default: space)
        
    Returns:
        Padded string
    """
    return text.ljust(width, pad_char)

