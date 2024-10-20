"""
Serve Flask WSGI app using Waitress for production.
"""

import waitress
from app import app

waitress.serve(app, host="0.0.0.0", port=40000)
