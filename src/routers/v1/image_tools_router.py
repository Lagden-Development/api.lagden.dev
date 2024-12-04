"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

from io import BytesIO
from typing import List

import cv2
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
import numpy as np
from PIL import Image
from pydantic import BaseModel, HttpUrl
import requests
from sklearn.cluster import KMeans

from helpers.api_keys import APIKeyHelper
from helpers.api_logs import APILogHelper

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
    background_tasks: BackgroundTasks,
    url: HttpUrl = Query(..., description="URL of the image to analyze"),
    n_colors: int = Query(
        3, ge=1, le=10, description="Number of dominant colors to extract (1-10)"
    ),
    api_key: str = Query(
        ...,
        description="API key for authentication",
        example="your-api-key",
    ),
) -> DominantColorsResponse:
    """
    Extract dominant colors from an image URL using K-means clustering.

    Args:
        background_tasks: FastAPI BackgroundTasks for logging
        url: The URL of the image to process
        n_colors: Number of dominant colors to extract (1-10)
        api_key: API key for authentication

    Returns:
        DominantColorsResponse containing hex and RGB color values

    Raises:
        HTTPException: If image download fails, URL is invalid, or authentication fails
    """
    status_code = 200
    error_message = None
    key_id = None

    try:
        # Check if the API key has the default role
        if not await APIKeyHelper.has_role(api_key, "default"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        # Validate URL
        if not url:
            raise HTTPException(status_code=400, detail="Invalid image URL")
        url = str(url)

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

    except HTTPException as e:
        status_code = e.status_code
        error_message = e.detail
        raise
    except Exception as e:
        status_code = 500
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(status_code=status_code, detail=error_message) from e
    finally:
        # Add logging as a background task
        background_tasks.add_task(
            APILogHelper.log_request,
            key_id=key_id,
            route="/image-tools/dominant_colors",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )
