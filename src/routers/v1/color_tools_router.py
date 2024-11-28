"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

import re
from enum import Enum
from typing import Tuple

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


router = APIRouter(
    tags=["Color Tools"],
)


class ColorFormat(str, Enum):
    """Valid color format types."""

    HEX = "hex"
    RGB = "rgb"


class ColorBrightnessResponse(BaseModel):
    """
    Response model for color brightness check API.

    Attributes:
        ok (bool): Indicates if the request was successful.
        status (int): HTTP status code of the response.
        message (str): Description or message about the response.
        data (dict): Dictionary containing the brightness analysis data.
    """

    ok: bool
    status: int
    message: str
    data: dict


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


def calculate_brightness(r: int, g: int, b: int) -> float:
    """
    Calculate perceived brightness using the formula:
    (0.299*R + 0.587*G + 0.114*B)/255

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        float: Brightness value between 0 and 1
    """
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


@router.get(
    "/check_brightness",
    response_model=ColorBrightnessResponse,
    description="""
    Check if a color is dark or light based on perceived brightness.
    Accepts either hex color (#RRGGBB) or RGB format (rgb(r,g,b) or r,g,b).
    """,
    response_description="Color brightness analysis with perceived brightness value and"
    "classification.",
    summary="Analyze Color Brightness",
)
async def check_color_brightness(
    color: str = Query(
        ...,
        description="Color in hex (#RRGGBB) or RGB format (rgb(r,g,b) or r,g,b)",
        example="#FF5733",
    ),
    color_format: ColorFormat = Query(
        ColorFormat.HEX, description="Format of the input color"
    ),
) -> ColorBrightnessResponse:
    """
    Analyze the brightness of a color and determine if it's dark or light.

    Args:
        color: Color string in hex or RGB format
        color_format: Format of the input color (hex or rgb)

    Returns:
        ColorBrightnessResponse containing brightness analysis

    Raises:
        HTTPException: If color format is invalid or processing fails
    """
    try:
        color = color.strip()

        # Validate color format
        if not validate_color(color, color_format):
            raise ValueError(
                f"Invalid {color_format.value} color format. "
                f"Use {'#RRGGBB' if color_format == ColorFormat.HEX else 'rgb(r,g,b) or r,g,b'}"
            )

        # Convert to RGB
        rgb = hex_to_rgb(color) if color_format == ColorFormat.HEX else parse_rgb(color)

        # Analyze brightness
        brightness = calculate_brightness(*rgb)
        is_dark = brightness < 0.5

        return ColorBrightnessResponse(
            ok=True,
            status=200,
            message="Successfully analyzed color brightness",
            data={
                "input_color": color,
                "format": color_format.value,
                "rgb_values": list(rgb),
                "brightness": round(brightness, 3),
                "is_dark": is_dark,
                "perception": "dark" if is_dark else "light",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}"
        ) from e
