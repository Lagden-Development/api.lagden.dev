"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.
"""

# Import the required modules

# Python Standard Library
import os

# Third Party Modules
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

api_db = client["ldev_api"]
users = api_db["watcher_users"]


def get_mongo_client():
    return client
