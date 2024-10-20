"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the main endpoints file for the website. It contains the main endpoints for the website and their
associated logic.
"""

# Import the required modules

# Flask Modules
from flask import Blueprint, jsonify

# DB
from db import users

# Create a Blueprint for main routes
blueprint = Blueprint("v1_watcher", __name__, url_prefix="/v1/watcher")


# Route Endpoints


@blueprint.route("/")
def index():
    return (
        jsonify(
            {
                "ok": False,
                "message": "No user specified, please refer to the documentation for more information.",
            }
        ),
        400,
    )


@blueprint.route("/<int:user>")
def user(user: str):
    if not user:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "No user specified, please refer to the documentation for more information.",
                }
            ),
            400,
        )

    query = users.find_one({"_id": user})

    if not query:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "User Not Found",
                }
            ),
            404,
        )

    if query.get("banned", False):
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "User Banned",
                }
            ),
            403,
        )

    if not query.get("watcher", True):
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "User opted out of watcher",
                }
            ),
            403,
        )

    data = query.copy()
    data.pop("_id")
    data["ok"] = True

    return jsonify(data)
