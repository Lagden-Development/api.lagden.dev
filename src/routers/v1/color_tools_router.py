# /src/routers/v1/color_tools_router.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This is the router for color tools.

Endpoints:
- /check_brightness: Analyze the brightness of a color and determine if it's dark or light.
"""

# Third-Party Imports
from fastapi import APIRouter, Query, BackgroundTasks
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

# Helper Imports
from helpers.api_keys import APIKeyHelper
from helpers.api_logs import APILogHelper
from helpers.colors.calc import calculate_brightness
from helpers.colors.convert import hex_to_rgb, parse_rgb
from helpers.colors.validate import ColorFormat, validate_color


router = APIRouter(
    tags=["Color Tools"],
)


class ColorBrightnessResponse(BaseModel):
    """
    Response model for color brightness analysis.

    Attributes:
        ok (bool): Indicates if the request was successful.
        status (int): HTTP status code of the response.
        message (str): Description or message about the response.
        data (dict): Dictionary containing the color brightness data.
    """

    ok: bool
    status: int
    message: str
    data: dict


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
    background_tasks: BackgroundTasks,
    color: str = Query(
        ...,
        description="Color in hex (#RRGGBB) or RGB format (rgb(r,g,b) or r,g,b)",
        example="#FF5733",
    ),
    color_format: ColorFormat = Query(
        ColorFormat.HEX, description="Format of the input color"
    ),
    api_key: str = Query(
        ...,
        description="API key for authentication",
        example="your-api-key",
    ),
) -> ColorBrightnessResponse:
    """
    Analyze the brightness of a color and determine if it's dark or light.
    """
    status_code = 200
    error_message = None
    key_id = None

    try:
        # Get API key data first

        # Check if the API key has the default role
        if not await APIKeyHelper.has_role(api_key, "default"):
            raise HTTPException(
                status_code=403, detail="API key does not have the required role"
            )

        api_key_data = await APIKeyHelper.use_key(api_key)
        key_id = api_key_data["_id"]

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

        response = ColorBrightnessResponse(
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
        status_code = 400
        error_message = str(e)
        raise HTTPException(status_code=status_code, detail=error_message) from e
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
            route="/color-tools/check_brightness",
            method="GET",
            status_code=status_code,
            error_message=error_message,
        )

    return response
