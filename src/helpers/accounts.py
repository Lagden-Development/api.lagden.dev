"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for working with accounts.
"""

# Python Standard Library Imports
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# Third-Party Imports
from fastapi import HTTPException, Response, Request

# Helper Imports
from helpers.fastapi.ip import get_client_ip

# Database Imports
from db import accounts


class AccountHelper:
    """
    Helper functions for working with accounts.

    Methods:
    - get_session_from_response
    - find_account_by_session
    - find_account_by_email
    - update_session_timestamp
    - remove_session
    - create_session
    - get_public_account_data
    """

    @staticmethod
    async def create_account(
        name: str, email: str, password: str, org: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Create a new account"""
        account = {
            "_id": str(uuid.uuid4()),
            "name": name,
            "emails": [{"address": email, "verified": False}],
            "password": password,
            "org": org,
            "sessions": [],
        }
        accounts.insert_one(account)
        return account

    @staticmethod
    async def get_session_from_response(response: Response) -> str:
        """Get and validate session ID from response cookie"""
        session_id = response.cookies.get("session")
        if not session_id:
            raise HTTPException(status_code=400, detail="No session found")
        return session_id

    @staticmethod
    async def find_account_by_session(session_id: str) -> Dict[Any, Any]:
        """Find account by session ID"""
        account = accounts.find_one({"sessions._id": session_id})
        if not account:
            raise HTTPException(status_code=400, detail="Account not found")
        return account

    @staticmethod
    async def find_account_by_email(email: str) -> Optional[Dict[Any, Any]]:
        """Find account by email address"""
        return accounts.find_one({"emails.address": email})

    @staticmethod
    async def update_session_timestamp(account_id: str, session_id: str) -> None:
        """Update last_used timestamp for a session"""
        accounts.update_one(
            {"_id": account_id, "sessions._id": session_id},
            {"$set": {"sessions.$.last_used": datetime.now().timestamp()}},
        )

    @staticmethod
    async def remove_session(account_id: str, session_id: str) -> None:
        """Remove a session from an account"""
        accounts.update_one(
            {"_id": account_id}, {"$pull": {"sessions": {"_id": session_id}}}
        )

    @staticmethod
    async def create_session(account_id: str, request: Request) -> Dict[str, Any]:
        """Create a new session for an account"""

        while True:
            session_id = str(uuid.uuid4())
            if not accounts.find_one({"sessions._id": session_id}):
                break

        session = {
            "_id": session_id,
            "ip": get_client_ip(request),
            "created_at": datetime.now().timestamp(),
            "last_used": datetime.now().timestamp(),
            "expires_at": datetime.now().timestamp() + 86400 * 30,  # 30 days
        }

        accounts.update_one({"_id": account_id}, {"$push": {"sessions": session}})

        return session

    @staticmethod
    async def get_public_account_data(account: Dict[Any, Any]) -> Dict[Any, Any]:
        """Get public account data by removing sensitive fields"""
        public_account = account.copy()

        # Remove sensitive fields
        del public_account["password"]

        # REDACT the session ids (for security)
        public_sessions = []
        for session in public_account["sessions"]:
            session["_id"] = "REDACTED FOR SECURITY"
            public_sessions.append(session)
        public_account["sessions"] = public_sessions

        return public_account
