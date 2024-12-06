# /src/helpers/colors/calc.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for calculating color brightness and dominant colors.
"""

# Python Standard Library Imports
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, Union, Tuple
import logging
import warnings

# Third-Party Imports
from numpy.typing import NDArray
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombWarning, DecompressionBombError
from sklearn.cluster import KMeans
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_IMAGE_SIZE = 4096  # Maximum dimension size in pixels
MIN_IMAGE_SIZE = 1  # Minimum dimension size in pixels
MAX_COLORS = 10  # Maximum number of dominant colors to extract
MIN_COLORS = 1  # Minimum number of dominant colors to extract
RGB_MAX = 255  # Maximum RGB value


@dataclass
class ColorResult:
    """Data class for color calculation results."""

    ok: bool
    colors: List[str] = None
    status: int = None
    detail: str = None


class ColorError(Exception):
    """Base exception class for color-related errors."""


class ImageProcessingError(ColorError):
    """Exception raised for errors during image processing."""


class InvalidColorError(ColorError):
    """Exception raised for invalid color values."""


def validate_rgb(r: int, g: int, b: int) -> None:
    """
    Validate RGB color values.

    Args:
        r: Red value
        g: Green value
        b: Blue value

    Raises:
        InvalidColorError: If any color value is invalid
    """
    for val, color in [(r, "red"), (g, "green"), (b, "blue")]:
        if not isinstance(val, (int, np.integer)):
            raise InvalidColorError(f"Invalid {color} value: must be an integer")
        if not 0 <= val <= RGB_MAX:
            raise InvalidColorError(
                f"Invalid {color} value: must be between 0 and {RGB_MAX}"
            )


def calculate_brightness(r: int, g: int, b: int) -> float:
    """
    Calculate perceived brightness using the formula: (0.299*R + 0.587*G + 0.114*B)/255

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        float: Brightness value between 0 and 1

    Raises:
        InvalidColorError: If color values are invalid
    """
    try:
        validate_rgb(r, g, b)
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / RGB_MAX
        return round(brightness, 3)
    except InvalidColorError as e:
        logger.error("Error calculating brightness: %s", str(e))
        raise


def validate_image(image: Image.Image) -> None:
    """
    Validate image dimensions and format.

    Args:
        image: PIL Image object

    Raises:
        ImageProcessingError: If image is invalid
    """
    width, height = image.size
    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        raise ImageProcessingError(
            f"Image dimensions exceed maximum size of {MAX_IMAGE_SIZE}px"
        )
    if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
        raise ImageProcessingError(
            f"Image dimensions below minimum size of {MIN_IMAGE_SIZE}px"
        )


def preprocess_image(image_io_stream: BytesIO) -> Tuple[NDArray, Image.Image]:
    """
    Preprocess image for color analysis.

    Args:
        image_io_stream: BytesIO stream containing image data

    Returns:
        Tuple of numpy array and PIL Image

    Raises:
        ImageProcessingError: If image processing fails
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", DecompressionBombWarning)
            image = Image.open(image_io_stream)
            validate_image(image)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert to numpy array
            image_array = np.array(image)
            return image_array, image

    except (
        UnidentifiedImageError,
        DecompressionBombWarning,
        DecompressionBombError,
    ) as e:
        raise ImageProcessingError(f"Invalid image format or size: {str(e)}") from e
    except Exception as e:
        raise ImageProcessingError(f"Error processing image: {str(e)}") from e


def calculate_dominant_colors(
    image_io_stream: BytesIO, n_colors: int = 5
) -> Dict[str, Union[bool, List[str], int, str]]:
    """
    Calculate the dominant colors in an image using KMeans clustering.

    Args:
        image_io_stream: BytesIO stream containing image data
        n_colors: Number of dominant colors to extract (default: 5)

    Returns:
        Dictionary containing results:
        {
            'ok': bool,
            'colors': List[str] (hex colors) or None,
            'status': int or None,
            'detail': str or None
        }
    """
    try:
        # Validate n_colors
        if not isinstance(n_colors, int) or not MIN_COLORS <= n_colors <= MAX_COLORS:
            return ColorResult(
                ok=False,
                status=400,
                detail=f"Number of colors must be between {MIN_COLORS} and {MAX_COLORS}",
            ).__dict__

        # Reset stream position
        image_io_stream.seek(0)

        # Preprocess image
        image_array, _ = preprocess_image(image_io_stream)

        # Reshape image for clustering
        pixels = image_array.reshape(-1, 3)

        # Calculate dominant colors using KMeans
        kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int)

        # Convert to hex colors
        hex_colors = [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r, g, b in colors]

        return ColorResult(ok=True, colors=hex_colors).__dict__

    except ImageProcessingError as e:
        logger.error("Image processing error: %s", str(e))
        return ColorResult(ok=False, status=400, detail=str(e)).__dict__

    except ValueError as e:
        logger.error("Value error: %s", str(e))
        return ColorResult(
            ok=False,
            status=400,
            detail=f"Value error: {str(e)}",
        ).__dict__
    except TypeError as e:
        logger.error("Type error: %s", str(e))
        return ColorResult(
            ok=False,
            status=400,
            detail=f"Type error: {str(e)}",
        ).__dict__
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return ColorResult(
            ok=False,
            status=500,
            detail="An unexpected error occurred while processing the image",
        ).__dict__


if __name__ == "__main__":
    import requests

    def run_tests():
        """Run test cases for the module."""
        # Test calculate_brightness
        try:
            assert calculate_brightness(255, 255, 255) == 1.0
            assert calculate_brightness(0, 0, 0) == 0.0
            assert calculate_brightness(255, 0, 0) == 0.299
            print("Brightness calculation tests passed!")
        except AssertionError:
            print("Brightness calculation tests failed!")

        # Test invalid RGB values
        try:
            calculate_brightness(256, 0, 0)  # Should raise InvalidColorError
            print("RGB validation test failed!")
        except InvalidColorError:
            print("RGB validation test passed!")

        # Test dominant color calculation
        try:
            # Test with a known image (black and white logo)
            test_image_url = "https://i.lagden.dev/logo.png"
            response = requests.get(test_image_url, timeout=10)
            test_image_io_stream = BytesIO(response.content)

            result = calculate_dominant_colors(test_image_io_stream, 2)
            assert result["ok"] is True
            assert len(result["colors"]) == 2
            # Check if colors are close to black and white
            colors = {color.lower() for color in result["colors"]}
            assert any(c.startswith("#0") for c in colors), "Black color not found"
            assert any(c.startswith("#f") for c in colors), "White color not found"
            print("Dominant color calculation tests passed!")

        except AssertionError as e:
            print(f"Dominant color calculation tests failed: {str(e)}")
        except Exception as e:
            print(f"Error during testing: {str(e)}")

    run_tests()
