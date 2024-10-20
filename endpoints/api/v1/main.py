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
blueprint = Blueprint("v1_main", __name__, url_prefix="/v1")


# Route Endpoints


@blueprint.route("/")
def index():
    return (
        jsonify(
            {
                "ok": False,
                "message": "No route specified, please refer to the documentation for more information.",
            }
        ),
        400,
    )
