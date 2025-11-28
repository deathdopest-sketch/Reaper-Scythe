"""
Math Utilities for REAPER

Mathematical functions and utilities.
"""

import math
from typing import List, Union


def min_value(values: List[Union[int, float]]) -> Union[int, float]:
    """
    Get minimum value from a list.
    
    Args:
        values: List of numbers
        
    Returns:
        Minimum value
    """
    if not values:
        raise ValueError("Cannot find minimum of empty list")
    return min(values)


def max_value(values: List[Union[int, float]]) -> Union[int, float]:
    """
    Get maximum value from a list.
    
    Args:
        values: List of numbers
        
    Returns:
        Maximum value
    """
    if not values:
        raise ValueError("Cannot find maximum of empty list")
    return max(values)


def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def lerp(a: Union[int, float], b: Union[int, float], t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def round_value(value: Union[int, float], decimals: int = 0) -> float:
    """
    Round a number to specified decimal places.
    
    Args:
        value: Value to round
        decimals: Number of decimal places (default: 0)
        
    Returns:
        Rounded value
    """
    return round(value, decimals)


def floor_value(value: Union[int, float]) -> int:
    """
    Get floor of a number.
    
    Args:
        value: Value to floor
        
    Returns:
        Floor value as integer
    """
    return int(math.floor(value))


def ceil_value(value: Union[int, float]) -> int:
    """
    Get ceiling of a number.
    
    Args:
        value: Value to ceil
        
    Returns:
        Ceiling value as integer
    """
    return int(math.ceil(value))


def sqrt_value(value: Union[int, float]) -> float:
    """
    Calculate square root.
    
    Args:
        value: Value to calculate square root of
        
    Returns:
        Square root
    """
    if value < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(value)


def pow_value(base: Union[int, float], exponent: Union[int, float]) -> float:
    """
    Calculate power.
    
    Args:
        base: Base value
        exponent: Exponent
        
    Returns:
        base raised to exponent
    """
    return math.pow(base, exponent)


def log_value(value: Union[int, float], base: Union[int, float] = math.e) -> float:
    """
    Calculate logarithm.
    
    Args:
        value: Value to calculate logarithm of
        base: Logarithm base (default: e)
        
    Returns:
        Logarithm value
    """
    if value <= 0:
        raise ValueError("Cannot calculate logarithm of non-positive number")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1")
    return math.log(value, base)


def sin_value(angle: Union[int, float]) -> float:
    """
    Calculate sine of angle in radians.
    
    Args:
        angle: Angle in radians
        
    Returns:
        Sine value
    """
    return math.sin(angle)


def cos_value(angle: Union[int, float]) -> float:
    """
    Calculate cosine of angle in radians.
    
    Args:
        angle: Angle in radians
        
    Returns:
        Cosine value
    """
    return math.cos(angle)


def tan_value(angle: Union[int, float]) -> float:
    """
    Calculate tangent of angle in radians.
    
    Args:
        angle: Angle in radians
        
    Returns:
        Tangent value
    """
    return math.tan(angle)

