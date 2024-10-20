"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the main endpoints file for the website. It contains the main endpoints for the website and their
associated logic.
"""

# Import the required modules

# Flask Modules
from flask import Blueprint, jsonify

# Create a Blueprint for main routes
blueprint = Blueprint("main", __name__, url_prefix="/")


# Route Endpoints


@blueprint.route("/")
def index():
    return jsonify(
        {
            "ok": True,
            "message": "Welcome to the lagden.dev API, please refer to the documentation for more information.",
            "documentation": "https://docs.api.lagden.dev",
        }
    )
