"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for working with API keys.
"""

# Python Standard Library Imports
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Third-Party Imports
from fastapi import HTTPException

# Database Imports
from db import accounts, api_keys


class APIKeyHelper:
    """
    Helper functions for working with API keys.

    Methods:
    - find_keys_by_account
    - create_key
    - use_key
    - find_key_by_id
    - delete_key
    - get_roles
    - add_role
    - remove_role
    - has_role
    """

    @staticmethod
    async def find_keys_by_account(account_id: str) -> List[Dict[Any, Any]]:
        """Find all API keys associated with an account"""
        keys = list(api_keys.find({"uuid": account_id}))
        if not keys:
            return []
        return keys

    @staticmethod
    async def create_key(
        account_id: str, description: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Create a new API key for an account"""
        # Verify account exists
        account = accounts.find_one({"_id": account_id})
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        current_time = datetime.now().timestamp()
        api_key = {
            "_id": str(uuid.uuid4()),
            "description": description,
            "uuid": account_id,
            "uses": 0,
            "created_at": current_time,
            "last_used": current_time,
            "roles": ["default"],
        }

        api_keys.insert_one(api_key)
        return api_key

    @staticmethod
    async def use_key(key_id: str) -> None:
        """Increment uses count and update last_used timestamp for an API key"""
        result = api_keys.update_one(
            {"_id": key_id},
            {"$inc": {"uses": 1}, "$set": {"last_used": datetime.now().timestamp()}},
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")

        return api_keys.find_one({"_id": key_id})

    @staticmethod
    async def find_key_by_id(key_id: str) -> Dict[Any, Any]:
        """Find API key by ID"""
        key = api_keys.find_one({"_id": key_id})
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")
        return key

    @staticmethod
    async def delete_key(key_id: str) -> None:
        """Delete an API key"""
        result = api_keys.delete_one({"_id": key_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")

    @staticmethod
    async def get_roles(key_id: str) -> List[str]:
        """Get roles for an API key"""
        key = api_keys.find_one({"_id": key_id})
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")
        return key.get("roles", [])

    @staticmethod
    async def add_role(key_id: str, role: str) -> None:
        """Add a role to an API key"""
        result = api_keys.update_one({"_id": key_id}, {"$addToSet": {"roles": role}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")

    @staticmethod
    async def remove_role(key_id: str, role: str) -> None:
        """Remove a role from an API key"""
        # Prevent removing the default role
        if role == "default":
            raise HTTPException(status_code=400, detail="Cannot remove default role")

        result = api_keys.update_one({"_id": key_id}, {"$pull": {"roles": role}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")

    @staticmethod
    async def has_role(key_id: str, role: str) -> bool:
        """Check if an API key has a specific role"""
        key = api_keys.find_one({"_id": key_id})
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")
        return role in key.get("roles", [])
