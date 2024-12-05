# /src/helpers/colors/calc.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for calculating color brightness.
"""

from io import BytesIO

import cv2
import numpy
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombWarning, DecompressionBombError
from sklearn.cluster import KMeans


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


def calculate_dominant_colors(image_io_stream: BytesIO, n_colors: int):
    """
    Calculate the dominant colors in an image using KMeans clustering.

    """

    # Attempt to open image and convert to PNG
    try:
        # Open image
        image = Image.open(image_io_stream)

        # New stream for PNG conversion
        image_io_stream = BytesIO()

        # Convert image to PNG
        image.save(image_io_stream, "PNG")

        # Reset stream position
        image_io_stream.seek(0)
    except UnidentifiedImageError:
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the format could not be identified;"
            "please provide a valid image file. If you believe this is an mistake, please report this issue.",
        }

    except DecompressionBombWarning:
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the image was warned to be a decompression bomb,"
            "and therefore cannot be processed. If you believe this is an mistake, please report this issue.",
        }

    except DecompressionBombError:
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the image was identified as a decompression bomb,"
            "and therefore cannot be processed. If you believe this is an mistake, please report this issue.",
        }

    except (OSError, ValueError) as e:
        return {
            "ok": False,
            "status": 400,
            "detail": f"An error occurred while processing the file: {e}",
        }

    # Attempt to convert image to numpy array
    try:
        image_byte_string = image_io_stream.read()
        image_np_array = numpy.frombuffer(image_byte_string, dtype=numpy.uint8)
        image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

    except cv2.error:
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the image could not be read;"
            "please provide a valid image file. If you believe this is an mistake, please report this issue.",
        }

    except (OSError, ValueError) as e:
        return {
            "ok": False,
            "status": 400,
            "detail": f"An unexpected error occurred while processing the file: {e}",
        }

    # Attempt to reshape image
    try:
        pixels = image.reshape((-1, 3))
        image = numpy.float32(pixels)
    except (ValueError, cv2.error):
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the dominant colors could not be calculated;"
            "please provide a valid image file. If you believe this is an mistake, please report this issue.",
        }

    # Attempt to calculate dominant colors
    try:
        kmeans = KMeans(n_clusters=n_colors)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int).tolist()
        hex_colors = [
            f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
            for color in colors
        ]
    except ValueError:
        return {
            "ok": False,
            "status": 400,
            "detail": "After processing the file, the dominant colors could not be calculated;"
            "please provide a valid image file. If you believe this is an mistake, please report this issue.",
        }

    return {
        "ok": True,
        "colors": hex_colors,
    }


if __name__ == "__main__":
    import requests

    # Test the calculate_brightness function
    assert calculate_brightness(255, 255, 255) == 1

    # Test the calculate_dominant_colors function (Hard to test due to k-means randomness) k-means will
    # always return slightly different colors, so we can only test for the general range of colors near
    # the expected values, rather than the exact values.
    TEST_IMAGE_URL = (
        "https://i.lagden.dev/logo.png"  # Black and white (#000000 and #ffffff) logo
    )
    test_image_io_stream = BytesIO(requests.get(TEST_IMAGE_URL, timeout=10).content)

    result = calculate_dominant_colors(test_image_io_stream, 2)

    assert result["ok"] is True
    assert len(result["colors"]) == 2
    assert result["colors"][0] == "#000000"
    assert (
        result["colors"][1] == "#fdfdfd"
    )  # k-means returns a slightly off-white color

    print("All tests passed!")
