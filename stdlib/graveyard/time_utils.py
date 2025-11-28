"""
Time Utilities for REAPER

Functions for working with time, dates, and timing operations.
"""

import time
from datetime import datetime
from typing import Optional, Callable, Any


def get_current_time() -> float:
    """
    Get current Unix timestamp.
    
    Returns:
        Current time as Unix timestamp (seconds since epoch)
    """
    return time.time()


def format_time(timestamp: Optional[float] = None, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp as a string.
    
    Args:
        timestamp: Unix timestamp (default: current time)
        format_string: Format string (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        Formatted time string
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_string)


def parse_time(time_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> float:
    """
    Parse a time string to Unix timestamp.
    
    Args:
        time_string: Time string to parse
        format_string: Format string (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        Unix timestamp
    """
    dt = datetime.strptime(time_string, format_string)
    return dt.timestamp()


def sleep(seconds: float) -> None:
    """
    Sleep for specified number of seconds.
    
    Args:
        seconds: Number of seconds to sleep
    """
    if seconds < 0:
        seconds = 0
    time.sleep(seconds)


def measure_time(func: Callable[[], Any]) -> tuple[Any, float]:
    """
    Measure execution time of a function.
    
    Args:
        func: Function to measure
        
    Returns:
        Tuple of (result, elapsed_time_in_seconds)
    """
    start = time.time()
    result = func()
    elapsed = time.time() - start
    return result, elapsed

