"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for validating color strings.
"""

import re
from enum import Enum


class ColorFormat(str, Enum):
    """Valid color format types."""

    HEX = "hex"
    RGB = "rgb"


def validate_color(color: str, color_format: ColorFormat) -> bool:
    """
    Validate color string based on color_format.

    Args:
        color: Color string to validate
        color_format: Format to validate against (hex or rgb)

    Returns:
        bool: True if valid, False otherwise
    """
    if color_format == ColorFormat.HEX:
        hex_pattern = r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        return bool(re.match(hex_pattern, color))
    else:  # RGB
        rgb_pattern = r"^(?:rgb\()?\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)?$"
        return bool(re.match(rgb_pattern, color))
