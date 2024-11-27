"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Import the required modules
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a router
router = APIRouter()


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index():
    return JSONResponse(
        content={
            "ok": True,
            "message": "Welcome to the lagden.dev API, please refer to the documentation for more information.",
            "swaggerui_docs": "https://api.lagden.dev/docs",
            "redoc_docs": "https://api.lagden.dev/redoc",
        }
    )
