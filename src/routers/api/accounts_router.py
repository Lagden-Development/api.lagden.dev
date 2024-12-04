"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Python Standard Library Imports
from typing import Optional
import os
import re

# Third-Party Imports
from fastapi import APIRouter, HTTPException, Response, Request, Depends, Cookie
from pydantic import BaseModel, EmailStr, Field, field_validator
import httpx
import bcrypt

# Helper Imports
from helpers.accounts import AccountHelper

router = APIRouter()

RECAPTCHA_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
MIN_RECAPTCHA_SCORE = 0.5


class SignupRequest(BaseModel):
    """
    Signup request data model
    """

    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str
    password_confirmation: str
    org: Optional[str] = None
    recaptcha_token: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("password_confirmation")
    def passwords_match(cls, v: str, info) -> str:
        if info.data.get("password") is not None and v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    """
    Login request data model
    """

    email: EmailStr
    password: str
    recaptcha_token: Optional[str] = None

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v


async def verify_recaptcha(token: Optional[str]) -> bool:
    """
    Verify the recaptcha token

    Args:
        token (Optional[str]): The recaptcha token

    Returns:
        bool: True if the token is valid, False otherwise
    """
    if not token or not RECAPTCHA_SECRET_KEY:
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={"secret": RECAPTCHA_SECRET_KEY, "response": token},
                timeout=10.0,
            )

            response.raise_for_status()
            result = response.json()
            return (
                result.get("success", False)
                and result.get("score", 0) >= MIN_RECAPTCHA_SCORE
            )

    except (httpx.RequestError, httpx.HTTPStatusError):
        return False


async def get_current_user(session: Optional[str] = Cookie(None)):
    """Dependency to get the current authenticated user"""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    account = await AccountHelper.find_account_by_session(session)
    if not account:
        raise HTTPException(status_code=401, detail="Session invalid")

    return account


@router.post("/signup", include_in_schema=False)
async def signup(request: SignupRequest, response: Response, req: Request):
    """Sign up a new user"""
    if not await verify_recaptcha(request.recaptcha_token):
        raise HTTPException(status_code=400, detail="Invalid recaptcha token")

    try:
        # Check if the email is already in use
        if await AccountHelper.find_account_by_email(request.email):
            raise HTTPException(status_code=400, detail="Email already in use")

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode(), salt)

        # Create the account
        account = await AccountHelper.create_account(
            request.name, request.email, hashed_password, request.org
        )

        # Create session - pass the Request object
        session = await AccountHelper.create_session(account["_id"], req)

        # Store session in cookie with secure flags
        response.set_cookie(
            key="session",
            value=str(session["_id"]),
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600 * 24 * 30,  # 30 days
        )

        return {
            "status": "success",
            "message": "User signed up successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/login", include_in_schema=False)
async def login(request: LoginRequest, response: Response, req: Request):
    """Log in a user"""
    if not await verify_recaptcha(request.recaptcha_token):
        raise HTTPException(status_code=400, detail="Invalid recaptcha token")

    try:
        # Find the user
        account = await AccountHelper.find_account_by_email(request.email)
        if not account:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Check the password
        if not bcrypt.checkpw(request.password.encode(), account["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create session - pass the Request object
        session = await AccountHelper.create_session(account["_id"], req)

        # Store session in cookie with secure flags
        response.set_cookie(
            key="session",
            value=str(session["_id"]),
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600 * 24 * 30,  # 30 days
        )

        return {
            "status": "success",
            "message": "User logged in successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/logout", include_in_schema=False)
async def logout(
    response: Response,
    session: str = Cookie(None),
    account: dict = Depends(get_current_user),
):
    """Log out a user"""
    try:
        await AccountHelper.remove_session(account["_id"], session)

        response.delete_cookie(
            key="session", httponly=True, secure=True, samesite="lax"
        )

        return {
            "status": "success",
            "message": "User logged out successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/me", include_in_schema=False)
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
