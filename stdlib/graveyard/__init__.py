"""
Graveyard Standard Library

A collection of utility functions for common operations in REAPER.
The graveyard is where useful tools rest, ready to be summoned when needed.
"""

from .time_utils import (
    get_current_time,
    format_time,
    parse_time,
    sleep,
    measure_time,
)

from .math_utils import (
    min_value,
    max_value,
    clamp,
    lerp,
    round_value,
    floor_value,
    ceil_value,
    sqrt_value,
    pow_value,
    log_value,
    sin_value,
    cos_value,
    tan_value,
)

from .string_utils import (
    trim,
    upper_case,
    lower_case,
    starts_with,
    ends_with,
    contains,
    replace_all,
    split_string,
    join_strings,
    pad_left,
    pad_right,
)

from .collection_utils import (
    filter_list,
    map_list,
    reduce_list,
    find_item,
    count_items,
    reverse_list,
    sort_list,
    unique_items,
    flatten_list,
)

from .random_utils import (
    random_int,
    random_float,
    random_choice,
    shuffle_list,
)

__all__ = [
    # Time utilities
    'get_current_time',
    'format_time',
    'parse_time',
    'sleep',
    'measure_time',
    # Math utilities
    'min_value',
    'max_value',
    'clamp',
    'lerp',
    'round_value',
    'floor_value',
    'ceil_value',
    'sqrt_value',
    'pow_value',
    'log_value',
    'sin_value',
    'cos_value',
    'tan_value',
    # String utilities
    'trim',
    'upper_case',
    'lower_case',
    'starts_with',
    'ends_with',
    'contains',
    'replace_all',
    'split_string',
    'join_strings',
    'pad_left',
    'pad_right',
    # Collection utilities
    'filter_list',
    'map_list',
    'reduce_list',
    'find_item',
    'count_items',
    'reverse_list',
    'sort_list',
    'unique_items',
    'flatten_list',
    # Random utilities
    'random_int',
    'random_float',
    'random_choice',
    'shuffle_list',
]

