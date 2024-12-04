"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for working with API logs.
"""

# Python Standard Library Imports
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Third-Party Imports
from fastapi import HTTPException

# Database Imports
from db import api_keys, api_logs


class APILogHelper:
    """
    Helper functions for logging API usage.

    Methods:
    - log_request: Create a new log entry for an API request
    - find_logs_by_account: Get all logs for a specific account
    - find_logs_by_api_key: Get all logs for a specific API key
    - find_logs_by_route: Get all logs for a specific route
    - get_recent_logs: Get recent logs with optional filtering
    """

    @staticmethod
    async def log_request(
        key_id: str,
        route: str,
        method: str,
        status_code: int,
        error_message: Optional[str] = None,
    ) -> Dict[Any, Any]:
        """
        Log an API request with associated metadata
        """
        # Find the API key to get the account UUID
        api_key = api_keys.find_one({"_id": key_id})
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Create the log entry
        log_entry = {
            "uuid": api_key["uuid"],  # Account UUID
            "kid": key_id,  # API Key ID
            "route": route,
            "method": method.upper(),
            "status_code": status_code,
            "timestamp": datetime.now().timestamp(),
        }

        # Add error message if provided
        if error_message:
            log_entry["error"] = error_message

        api_logs.insert_one(log_entry)
        return log_entry

    @staticmethod
    async def find_logs_by_account(
        account_id: str, limit: Union[int, None] = 100, skip: int = 0
    ) -> List[Dict[Any, Any]]:
        """Get all logs for a specific account"""
        if limit is None:
            return list(api_logs.find({"uuid": account_id}).sort("timestamp", -1))

        return list(
            api_logs.find({"uuid": account_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

    @staticmethod
    async def find_logs_by_api_key(
        key_id: str, limit: Union[int, None] = 100, skip: int = 0
    ) -> List[Dict[Any, Any]]:
        """Get all logs for a specific API key"""

        if limit is None:
            return list(api_logs.find({"kid": key_id}).sort("timestamp", -1))

        return list(
            api_logs.find({"kid": key_id}).sort("timestamp", -1).skip(skip).limit(limit)
        )

    @staticmethod
    async def find_logs_by_route(
        route: str,
        account_id: Optional[str] = None,
        limit: Union[int, None] = 100,
        skip: int = 0,
    ) -> List[Dict[Any, Any]]:
        """Get all logs for a specific route, optionally filtered by account"""

        query = {"route": route}
        if account_id:
            query["uuid"] = account_id

        if limit is None:
            return list(api_logs.find(query).sort("timestamp", -1))

        return list(api_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit))

    @staticmethod
    async def get_recent_logs(
        minutes: int = 60,
        status_code: Optional[int] = None,
        method: Optional[str] = None,
        limit: Union[int, None] = 100,
    ) -> List[Dict[Any, Any]]:
        """
        Get recent logs with optional filtering by status code and method
        """
        # Calculate the timestamp from minutes ago
        cutoff_time = datetime.now().timestamp() - (minutes * 60)

        # Build the query
        query = {"timestamp": {"$gte": cutoff_time}}
        if status_code:
            query["status_code"] = status_code
        if method:
            query["method"] = method.upper()

        if limit is None:
            return list(api_logs.find(query).sort("timestamp", -1))

        return list(api_logs.find(query).sort("timestamp", -1).limit(limit))

    @staticmethod
    async def get_error_logs(
        account_id: Optional[str] = None, hours: int = 24, limit: Union[int, None] = 100
    ) -> List[Dict[Any, Any]]:
        """
        Get logs for failed requests (status code >= 400)
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        query = {"timestamp": {"$gte": cutoff_time}, "status_code": {"$gte": 400}}

        if account_id:
            query["uuid"] = account_id

        if limit is None:
            return list(api_logs.find(query).sort("timestamp", -1))

        return list(api_logs.find(query).sort("timestamp", -1).limit(limit))
