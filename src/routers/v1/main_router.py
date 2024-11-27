"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.
"""

# Import the required modules
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Create a router (equivalent to Flask's Blueprint)
router = APIRouter()


# Route Endpoints
@router.get("/", include_in_schema=False)
async def index():
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "message": "No route specified, please refer to the documentation for more information.",
        },
    )
