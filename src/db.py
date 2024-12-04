"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This snippet is a helper function to retrieve the MongoDB client and collections for use in the FastAPI application.
"""

# Python Standard Library
import os
from typing import Optional

# Third Party Modules
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


def create_mongo_client() -> Optional[MongoClient]:
    """
    Create and validate MongoDB client connection

    Returns:
        MongoClient: The MongoDB client if connection is successful
        None: If connection fails
    """
    try:
        # Get MongoDB URI from environment variable
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")

        # Create client
        mongo_client = MongoClient(mongodb_uri)

        # Validate connection
        mongo_client.admin.command("ping")
        print("Successfully connected to MongoDB")

        return mongo_client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        return None


# Initialize client
client = create_mongo_client()

# Initialize database and collections if client connection was successful
if client:
    api_db = client["ldev_api"]
    users = api_db["watcher_users"]
    accounts = api_db["api_accounts"]
    api_logs = api_db["api_logs"]
    api_keys = api_db["api_keys"]
else:
    raise RuntimeError("Failed to establish MongoDB connection")


def get_mongo_client():
    """
    Get the MongoDB client

    Returns:
        MongoClient: The MongoDB client

    Raises:
        RuntimeError: If the MongoDB client is not initialized
    """
    if client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return client
