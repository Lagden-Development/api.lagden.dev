"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Python Standard Library
import os

# Third Party Modules
from dotenv import load_dotenv
from fastapi import FastAPI

# Load the environment variables
load_dotenv(override=True)

# Create the FastAPI app
app = FastAPI(
    title="api.lagden.dev",
    description="The lagden.dev API used for our servies.",
    version="2.0.0beta",
)

# Import routers (equivalent to Flask blueprints)
# You'll need to convert these to FastAPI routers
from routers import main_router as main_router
from routers.v1 import main_router as v1_main_router
from routers.v1 import watcher_router as v1_watcher_router

# Include the routers
app.include_router(main_router.router)
app.include_router(v1_main_router.router, prefix="/v1")
app.include_router(v1_watcher_router.router, prefix="/v1/watcher")


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("DEV_PORT", 3000)),
        reload=True,  # Enable auto-reload during development
    )
