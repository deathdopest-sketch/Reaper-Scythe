"""
Collection Utilities for REAPER

Functions for working with lists, dictionaries, and other collections.
"""

from typing import List, Any, Callable, Optional, Dict


def filter_list(items: List[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """
    Filter list using a predicate function.
    
    Args:
        items: List to filter
        predicate: Function that returns True to keep item
        
    Returns:
        Filtered list
    """
    return [item for item in items if predicate(item)]


def map_list(items: List[Any], transform: Callable[[Any], Any]) -> List[Any]:
    """
    Map list using a transform function.
    
    Args:
        items: List to map
        transform: Function to transform each item
        
    Returns:
        Mapped list
    """
    return [transform(item) for item in items]


def reduce_list(items: List[Any], reducer: Callable[[Any, Any], Any], initial: Optional[Any] = None) -> Any:
    """
    Reduce list using a reducer function.
    
    Args:
        items: List to reduce
        reducer: Function that combines accumulator and item
        initial: Initial value (default: None, uses first item)
        
    Returns:
        Reduced value
    """
    if not items:
        return initial
    
    if initial is None:
        accumulator = items[0]
        start_index = 1
    else:
        accumulator = initial
        start_index = 0
    
    for i in range(start_index, len(items)):
        accumulator = reducer(accumulator, items[i])
    
    return accumulator


def find_item(items: List[Any], predicate: Callable[[Any], bool]) -> Optional[Any]:
    """
    Find first item matching predicate.
    
    Args:
        items: List to search
        predicate: Function that returns True for matching item
        
    Returns:
        First matching item or None
    """
    for item in items:
        if predicate(item):
            return item
    return None


def count_items(items: List[Any], predicate: Callable[[Any], bool]) -> int:
    """
    Count items matching predicate.
    
    Args:
        items: List to count
        predicate: Function that returns True for matching item
        
    Returns:
        Count of matching items
    """
    return sum(1 for item in items if predicate(item))


def reverse_list(items: List[Any]) -> List[Any]:
    """
    Reverse a list.
    
    Args:
        items: List to reverse
        
    Returns:
        Reversed list (new list)
    """
    return list(reversed(items))


def sort_list(items: List[Any], key: Optional[Callable[[Any], Any]] = None, reverse: bool = False) -> List[Any]:
    """
    Sort a list.
    
    Args:
        items: List to sort
        key: Optional key function for sorting
        reverse: If True, sort in reverse order
        
    Returns:
        Sorted list (new list)
    """
    return sorted(items, key=key, reverse=reverse)


def unique_items(items: List[Any]) -> List[Any]:
    """
    Get unique items from list (preserves order).
    
    Args:
        items: List to get unique items from
        
    Returns:
        List of unique items
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def flatten_list(nested: List[Any]) -> List[Any]:
    """
    Flatten a nested list.
    
    Args:
        nested: Nested list to flatten
        
    Returns:
        Flattened list
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

