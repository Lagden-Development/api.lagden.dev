# /src/helpers/colors/convert.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for converting color formats.
"""

# Python Standard Library Imports
from typing import Tuple
import re


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


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex color.

    Args:
        rgb: Tuple of RGB values

    Returns:
        Hex color string
    """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


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


if __name__ == "__main__":
    # Test the hex_to_rgb function
    assert hex_to_rgb("#ffffff") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#ff0000") == (255, 0, 0)
    assert hex_to_rgb("#00ff00") == (0, 255, 0)
    assert hex_to_rgb("#0000ff") == (0, 0, 255)

    # Test the rgb_to_hex function
    assert rgb_to_hex((255, 255, 255)) == "#ffffff"
    assert rgb_to_hex((0, 0, 0)) == "#000000"
    assert rgb_to_hex((255, 0, 0)) == "#ff0000"
    assert rgb_to_hex((0, 255, 0)) == "#00ff00"
    assert rgb_to_hex((0, 0, 255)) == "#0000ff"

    # Test the parse_rgb function
    assert parse_rgb("255, 255, 255") == (255, 255, 255)
    assert parse_rgb("0, 0, 0") == (0, 0, 0)
    assert parse_rgb("255, 0, 0") == (255, 0, 0)
    assert parse_rgb("0, 255, 0") == (0, 255, 0)
    assert parse_rgb("0, 0, 255") == (0, 0, 255)

    # Test the parse_rgb function with invalid values
    try:
        parse_rgb("256, 255, 255")
    except ValueError as e:
        assert str(e) == "RGB values must be between 0 and 255"

    print("All tests passed!")
