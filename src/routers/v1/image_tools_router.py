# /src/routers/v1/image_tools_router.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This router contains the image tools endpoints.

Endpoints:
    /dominant_colors: Extract dominant colors from an image URL.
"""

# Python Standard Library Imports
from io import BytesIO
from typing import List, Optional, Union

# Third-Party Imports
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, HttpUrl
import requests

# Helper Imports
from helpers.api_keys import APIKeyHelper
from helpers.api_logs import APILogHelper
from helpers.colors.calc import calculate_dominant_colors

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


async def process_image_stream(image_stream: BytesIO, n_colors: int) -> dict:
    """
    Process an image stream to extract dominant colors.

    Args:
        image_stream: BytesIO stream containing the image data
        n_colors: Number of dominant colors to extract

    Returns:
        dict containing the processing results
    """
    result = calculate_dominant_colors(image_stream, n_colors)

    if not result["ok"]:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result.get("detail", "Error processing image"),
        )

    hex_colors = result["colors"]
    rgb_colors = [
        [
            int(color[1:3], 16),
            int(color[3:5], 16),
            int(color[5:7], 16),
        ]
        for color in hex_colors
    ]

    return {
        "hex_colors": hex_colors,
        "rgb_colors": rgb_colors,
    }


@router.post(
    "/dominant_colors",
    response_model=DominantColorsResponse,
    description="Extracts the dominant colors from an uploaded image file or URL.",
    response_description="The extracted dominant colors in both hex and RGB formats.",
    summary="Extract Dominant Colors from Image",
)
async def extract_dominant_colors(
    background_tasks: BackgroundTasks,
    file: Optional[Union[UploadFile, str]] = File(
        None, description="Image file to analyze"
    ),
    url: Optional[HttpUrl] = Query(None, description="URL of the image to analyze"),
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
    Extract dominant colors from either an uploaded image file or an image URL using K-means clustering.

    Args:
        background_tasks: FastAPI BackgroundTasks for logging
        file: Optional uploaded image file
        url: Optional URL of the image to process
        n_colors: Number of dominant colors to extract (1-10)
        api_key: API key for authentication

    Returns:
        DominantColorsResponse containing hex and RGB color values

    Raises:
        HTTPException: If image processing fails, input is invalid, or authentication fails
    """
    status_code = 200
    error_message = None
    key_id = None

    if isinstance(file, str):
        file = None  # TODO: implement proper handling

    try:
        # Validate input: either file or URL must be provided, but not both
        if (file is None and url is None) or (file is not None and url is not None):
            raise HTTPException(
                status_code=400,
                detail="Exactly one of 'file' or 'url' must be provided",
            )

        # Check API key authorization
        if not await APIKeyHelper.has_role(api_key, "default"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

        # Handle file upload
        if file:
            # Validate file type
            content_type = file.content_type
            if not content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only image files are supported.",
                )

            # Read file into memory
            contents = await file.read()
            image_stream = BytesIO(contents)

        # Handle URL
        else:
            url_str = str(url)
            allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"]
            if not any(url_str.lower().endswith(ext) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image URL. Supported formats: JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF",
                )

            try:
                image_response = requests.get(url_str, timeout=10)
                image_stream = BytesIO(image_response.content)
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Failed to download the image: {str(e)}"
                ) from e

        # Process the image
        image_stream.seek(0)
        result = await process_image_stream(image_stream, n_colors)

        return DominantColorsResponse(
            ok=True,
            status=200,
            message="Successfully extracted dominant colors",
            data=result,
        )

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
            method="POST",
            status_code=status_code,
            error_message=error_message,
        )
