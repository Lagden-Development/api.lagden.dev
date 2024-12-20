"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This is the main FastAPI application file that imports all routers and runs the application.
"""

# Python Standard Library
import os
import logging
import sys

# Third Party Modules
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import routers
from routers import main_router
from routers.v1 import main_router as v1_main_router
from routers.v1 import watcher_router as v1_watcher_router
from routers.v1 import ldev_cms_router as v1_ldev_cms_router
from routers.v1 import image_tools_router as v1_image_tools_router
from routers.v1 import color_tools_router as v1_color_tools_router
from routers.api import accounts_router, me_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Load the environment variables
load_dotenv(override=True)

# Create the FastAPI app
app = FastAPI(
    title="api.lagden.dev",
    description="The lagden.dev API used for our services and tools.",
    version="2.0.0beta",
)


# Mount the static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include page routers
app.include_router(main_router.router)

# Include API routers
app.include_router(v1_main_router.router, prefix="/v1")
app.include_router(v1_watcher_router.router, prefix="/v1/watcher")
app.include_router(v1_ldev_cms_router.router, prefix="/v1/ldev-cms")
app.include_router(v1_image_tools_router.router, prefix="/v1/image-tools")
app.include_router(v1_color_tools_router.router, prefix="/v1/color-tools")

# Include the internal API routers
app.include_router(accounts_router.router, prefix="/api/accounts")
app.include_router(me_router.router, prefix="/api/me")

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST"),
        port=int(os.getenv("DEV_PORT", "3000")),
        reload=True,  # Enable auto-reload during development
    )
