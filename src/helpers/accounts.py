# /src/helpers/accounts.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This module contains helper functions for working with accounts.
"""

# Python Standard Library Imports
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

# Third-Party Imports
from fastapi import Response, Request
from fastapi.exceptions import HTTPException

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
    async def update_account_name(account_id: str, name: str) -> None:
        """Update an account's name"""
        accounts.update_one({"_id": account_id}, {"$set": {"name": name}})

    @staticmethod
    async def update_account_org(account_id: str, org: str) -> None:
        """Update an account's organization"""
        accounts.update_one({"_id": account_id}, {"$set": {"org": org}})

    @staticmethod
    async def add_email_to_account(account_id: str, email: str) -> None:
        """Add an email to an account"""
        accounts.update_one(
            {"_id": account_id, "emails.address": {"$ne": email}},
            {"$push": {"emails": {"address": email, "verified": False}}},
        )

    @staticmethod
    async def remove_email_from_account(account_id: str, email: str) -> None:
        """Remove an email from an account"""

        # Check if the email is the primary email
        account = accounts.find_one({"_id": account_id})

        found = False
        for email_address in account["emails"]:
            if email_address["address"] == email:
                if email_address["primary"]:
                    raise HTTPException(
                        status_code=400, detail="Cannot remove primary email"
                    )
                found = True
                break

        if not found:
            raise HTTPException(status_code=400, detail="Email not found")

        accounts.update_one(
            {"_id": account_id}, {"$pull": {"emails": {"address": email}}}
        )

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
            "expires_at": datetime.now().timestamp() + 5,  # 86400 * 30,  # 30 days
        }

        # Create an index to delete expired sessions if it doesn't exist
        if "sessions.expires_at" not in accounts.index_information():
            accounts.create_index(
                "sessions.expires_at",
                expireAfterSeconds=0,
                partialFilterExpression={"sessions.expires_at": {"$exists": True}},
            )

        accounts.update_one({"_id": account_id}, {"$push": {"sessions": session}})

        return session

    @staticmethod
    async def get_public_account_data(account: Dict[Any, Any]) -> Dict[Any, Any]:
        """Get public account data by removing sensitive fields"""
        public_account = account.copy()

        # Remove sensitive fields
        del public_account["password"]

        # Find and mark the current session as current: True
        for session in public_account["sessions"]:
            if session["last_used"] == max(
                [session["last_used"] for session in public_account["sessions"]]
            ):
                session["current"] = True
            else:
                session["current"] = False

        return public_account
