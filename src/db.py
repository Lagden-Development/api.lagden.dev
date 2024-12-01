"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Import the required modules

# Python Standard Library
import os

# Third Party Modules
from pymongo.mongo_client import MongoClient

client = MongoClient(os.getenv("MONGODB_URI"))

api_db = client["ldev_api"]
users = api_db["watcher_users"]


def get_mongo_client():
    """
    Get the MongoDB client

    Returns:
        MongoClient: The MongoDB client
    """
    return client
