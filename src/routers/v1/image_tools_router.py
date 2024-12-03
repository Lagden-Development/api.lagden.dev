"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

from io import BytesIO
from typing import List

import cv2
from fastapi import APIRouter, HTTPException, Query
import numpy as np
from PIL import Image
from pydantic import BaseModel, HttpUrl
import requests
from sklearn.cluster import KMeans

router = APIRouter(
    tags=["Image Tools"],
)


class DominantColorsResponse(BaseModel):
    """
    Response model for dominant colors API.

    Attributes:
        ok (bool): Indicates if the request was successful.
        status (int): HTTP status code of the response.
        message (str): Description or message about the response.
        data (dict[str, List]): Dictionary containing the dominant colors data.
    """

    ok: bool
    status: int
    message: str
    data: dict[str, List]


@router.get(
    "/dominant_colors",
    response_model=DominantColorsResponse,
    description="Extracts the dominant colors from an image URL.",
    response_description="The extracted dominant colors in both hex and RGB formats.",
    summary="Extract Dominant Colors from Image",
)
async def extract_dominant_colors(
    url: HttpUrl = Query(..., description="URL of the image to analyze"),
    n_colors: int = Query(
        3, ge=1, le=10, description="Number of dominant colors to extract (1-10)"
    ),
) -> DominantColorsResponse:
    """
    Extract dominant colors from an image URL using K-means clustering.

    Args:
        url: The URL of the image to process
        n_colors: Number of dominant colors to extract (1-10)

    Returns:
        DominantColorsResponse containing hex and RGB color values

    Raises:
        HTTPException: If image download fails or URL is invalid
    """

    # Validate URL
    if not url:
        raise HTTPException(status_code=400, detail="Invalid image URL")

    allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"]

    if not any(url.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Invalid image URL. Supported formats: JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF",
        )

    # Download and process image
    try:
        image_response = requests.get(str(url), timeout=10)
        image_io_stream = BytesIO(image_response.content)
        image_io_stream.seek(0)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to download the image: {str(e)}"
        ) from e

    # Image processing
    try:
        image = Image.open(image_io_stream)
        image_io_stream = BytesIO()
        image.save(image_io_stream, "PNG")
        image_io_stream.seek(0)

        image_byte_string = image_io_stream.read()
        image_np_array = np.frombuffer(image_byte_string, dtype=np.uint8)
        image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

        pixels = image.reshape((-1, 3))
        image = np.float32(pixels)

        # Extract colors
        kmeans = KMeans(n_clusters=n_colors)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_.astype(int).tolist()
        hex_colors = [
            f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
            for color in colors
        ]

        return DominantColorsResponse(
            ok=True,
            status=200,
            message="Successfully extracted dominant colors",
            data={
                "hex_colors": hex_colors,
                "rgb_colors": colors,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing image: {str(e)}"
        ) from e
