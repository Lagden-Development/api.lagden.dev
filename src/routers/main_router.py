"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.
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
