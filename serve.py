"""
Serve Flask WSGI app using Waitress for production.
"""

# Import the required modules

# Python Standard Library
import os

# Third Party Modules
import waitress

# Local Modules
from app import app

waitress.serve(app, host=os.getenv("HOST", "0.0.0.0"), port=os.getenv("PORT", 5000))
