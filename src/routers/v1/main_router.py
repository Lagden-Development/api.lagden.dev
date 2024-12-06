# /src/routers/v1/main_router.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This file contains the main router for the V1 API.
"""

# Third-Party Libraries
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a router (equivalent to Flask's Blueprint)
router = APIRouter()


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index():
    """
    Default endpoint that returns an error message directing users to the documentation.

    Returns:
        JSONResponse: A 400 error response with a message directing users to the documentation.
    """
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "message": "No route specified, please refer to the documentation for more"
            "information.",
        },
    )
