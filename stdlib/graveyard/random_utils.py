"""
Random Utilities for REAPER

Random number generation and random operations.
"""

import random
from typing import List, Any, Union


def random_int(min_val: int = 0, max_val: int = 100) -> int:
    """
    Generate random integer.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Random integer
    """
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return random.randint(min_val, max_val)


def random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Generate random float.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (exclusive)
        
    Returns:
        Random float
    """
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return random.uniform(min_val, max_val)


def random_choice(items: List[Any]) -> Any:
    """
    Choose random item from list.
    
    Args:
        items: List to choose from
        
    Returns:
        Random item
        
    Raises:
        ValueError: If list is empty
    """
    if not items:
        raise ValueError("Cannot choose from empty list")
    return random.choice(items)


def shuffle_list(items: List[Any]) -> List[Any]:
    """
    Shuffle a list (returns new list).
    
    Args:
        items: List to shuffle
        
    Returns:
        Shuffled list (new list)
    """
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled

