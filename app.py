"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.
"""

# Import the required modules

# Python Standard Library
import os

# Third Party Modules
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Flask Modules
from flask import Flask, jsonify

# Flask Extensions
from flask_minify import Minify

# Endpoints
from endpoints.api import main
from endpoints.api.v1 import main as v1_main
from endpoints.api.v1 import watcher

# Load the environment variables
load_dotenv()

# Create the Flask app and load extentions

# Flask App
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_port=1)

# Extensions
Minify(app)


# Pass the config to the templates
@app.context_processor
def inject_global_variable():
    global CONFIG
    return dict(CONFIG=CONFIG)


# Custom Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page Not Found"}), 404


# Register the all the blueprints

app.register_blueprint(main.blueprint)
app.register_blueprint(v1_main.blueprint)
app.register_blueprint(watcher.blueprint)

# Run the built-in development server when ran as a script.
if __name__ == "__main__":
    app.run(
        debug=True,
        host=os.getenv("HOST", "0.0.0.0"),
        port=os.getenv("PORT", 5000),
    )
