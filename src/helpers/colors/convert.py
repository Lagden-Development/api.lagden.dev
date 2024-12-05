"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for converting color formats.
"""

import re
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string

    Returns:
        Tuple of RGB values
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c + c for c in hex_color)
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def parse_rgb(rgb_str: str) -> Tuple[int, int, int]:
    """
    Parse RGB string to tuple.

    Args:
        rgb_str: RGB color string

    Returns:
        Tuple of RGB values

    Raises:
        ValueError: If RGB format is invalid or values are out of range
    """
    matches = re.findall(r"\d+", rgb_str)
    if len(matches) != 3:
        raise ValueError("Invalid RGB format")

    rgb = tuple(int(x) for x in matches)
    if not all(0 <= x <= 255 for x in rgb):
        raise ValueError("RGB values must be between 0 and 255")

    return rgb
