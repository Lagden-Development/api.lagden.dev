# /src/routers/api/me_router.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Python Standard Library Imports
from typing import Optional
import datetime

# Third-Party Imports
from fastapi import APIRouter, Cookie, Depends
from fastapi.exceptions import HTTPException

# Helper Imports
from helpers.accounts import AccountHelper
from helpers.api_keys import APIKeyHelper
from helpers.api_logs import APILogHelper

router = APIRouter()


async def get_current_user(session: Optional[str] = Cookie(None)):
    """Dependency to get the current authenticated user"""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    account = await AccountHelper.find_account_by_session(session)
    if not account:
        raise HTTPException(status_code=401, detail="Session invalid")

    return account


@router.get("/", include_in_schema=False)
async def me(session: str = Cookie(None), account: dict = Depends(get_current_user)):
    """Get the current user's information"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        public_account = await AccountHelper.get_public_account_data(account)

        return {
            "status": "success",
            "message": "User information retrieved successfully",
            "data": public_account,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/sessions/{session_id}", include_in_schema=False)
async def delete_session(session_id: str, account: dict = Depends(get_current_user)):
    """Delete a session associated with the current user"""
    try:
        await AccountHelper.remove_session(account["_id"], session_id)

        return {
            "status": "success",
            "message": "Session deleted successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/details/name/{new_name}", include_in_schema=False)
async def update_name(
    new_name: str,
    session: str = Cookie(None),
    account: dict = Depends(get_current_user),
):
    """Update the current user's name"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        await AccountHelper.update_account_name(account["_id"], new_name)

        return {
            "status": "success",
            "message": "Name updated successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/details/org/{new_org}", include_in_schema=False)
async def update_org(
    new_org: str,
    session: str = Cookie(None),
    account: dict = Depends(get_current_user),
):
    """Update the current user's organization"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        await AccountHelper.update_account_org(account["_id"], new_org)

        return {
            "status": "success",
            "message": "Organization updated successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api-keys", include_in_schema=False)
async def my_api_keys(
    session: str = Cookie(None), account: dict = Depends(get_current_user)
):
    """Get all API keys associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        keys = await APIKeyHelper.find_keys_by_account(account["_id"])

        return {
            "status": "success",
            "message": "API keys retrieved successfully",
            "data": keys,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api-keys/{key_id}", include_in_schema=False)
async def my_api_key(
    key_id: str, session: str = Cookie(None), account: dict = Depends(get_current_user)
):
    """Get a specific API key associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        key = await APIKeyHelper.find_key_by_id(key_id)

        return {
            "status": "success",
            "message": "API key retrieved successfully",
            "data": key,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/api-keys", include_in_schema=False)
async def create_api_key(
    description: dict,
    session: str = Cookie(None),
    account: dict = Depends(get_current_user),
):
    """Create a new API key for the current user with a description"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        key = await APIKeyHelper.create_key(
            account["_id"], description.get("description")
        )

        return {
            "status": "success",
            "message": "API key created successfully",
            "data": key,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/api-keys/{key_id}", include_in_schema=False)
async def delete_api_key(
    key_id: str, session: str = Cookie(None), account: dict = Depends(get_current_user)
):
    """Delete an API key associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        await APIKeyHelper.delete_key(key_id)

        return {
            "status": "success",
            "message": "API key deleted successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recent-api-logs", include_in_schema=False)
async def my_recent_api_logs(
    session: str = Cookie(None), account: dict = Depends(get_current_user)
):
    """Get all API logs associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        logs = await APILogHelper.find_logs_by_account(account["_id"], limit=5)

        response_logs = []
        # Stringify the _id field in each log entry
        for log in logs:
            log["_id"] = str(log["_id"])
            response_logs.append(log)

        return {
            "status": "success",
            "message": "API logs retrieved successfully",
            "data": response_logs,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/all-api-logs/{limit}/{skip}", include_in_schema=False)
async def my_all_api_logs(
    limit: int,
    skip: int,
    session: str = Cookie(None),
    account: dict = Depends(get_current_user),
):
    """Get all API logs associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        logs = await APILogHelper.find_logs_by_account(
            account["_id"], limit=limit, skip=skip
        )

        response_logs = []
        # Stringify the _id field in each log entry
        for log in logs:
            log["_id"] = str(log["_id"])
            response_logs.append(log)

        return {
            "status": "success",
            "message": "API logs retrieved successfully",
            "data": response_logs,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/total-api-logs", include_in_schema=False)
async def my_total_api_logs(
    session: str = Cookie(None), account: dict = Depends(get_current_user)
):
    """Get the number of API logs associated with the current user"""
    try:
        await AccountHelper.update_session_timestamp(account["_id"], session)
        logs = await APILogHelper.find_logs_by_account(account["_id"], limit=None)

        log_timestamps = []
        for log in logs:
            log_timestamps.append(log["timestamp"])

        now = datetime.datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Handle December to January transition
        if current_month == 1:
            last_month = 12
            last_month_year = current_year - 1
        else:
            last_month = current_month - 1
            last_month_year = current_year

        logs_this_month = 0
        logs_last_month = 0

        for log_timestamp in log_timestamps:
            # Get datetime object from utc timestamp
            log_datetime = datetime.datetime.fromtimestamp(
                log_timestamp, datetime.timezone.utc
            )

            # Get the month and year of the log
            log_month = log_datetime.month
            log_year = log_datetime.year

            # Check if the log was created this month
            if log_month == current_month and log_year == current_year:
                logs_this_month += 1
            # Check if the log was created last month
            elif log_month == last_month and log_year == last_month_year:
                logs_last_month += 1

        return {
            "status": "success",
            "message": "API log count retrieved successfully",
            "data": {
                "total": len(logs),
                "this_month": logs_this_month,
                "last_month": logs_last_month,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
