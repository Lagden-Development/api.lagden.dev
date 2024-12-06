# /src/routers/main_router.py
"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.
"""

# Python Standard Library Imports
from typing import Callable
from functools import wraps

# Third-Party Imports
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

# Helper Imports
from helpers.accounts import AccountHelper

# Local Imports
from globals import templates

# Create a router
router = APIRouter()


# Wrapper
def redirect_authenticated(func: Callable) -> Callable:
    """
    Decorator to check for valid session cookies and redirect authenticated users to app.
    If no valid session is found, allows the route to proceed normally.

    Usage:
        @router.get("/login")
        @redirect_authenticated
        async def login(request: Request):
            return templates.TemplateResponse("login.html", {"request": request})
    """

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Get session cookie
        session = request.cookies.get("session")

        if session:
            try:
                # Check if session is valid
                account = await AccountHelper.find_account_by_session(session)

                # If we get here, session is valid - redirect to dashboard
                if account:
                    await AccountHelper.update_session_timestamp(
                        account["_id"], session
                    )
                    return RedirectResponse(url="/app", status_code=HTTP_303_SEE_OTHER)

            except HTTPException:
                # Invalid session, create response to delete cookie
                response = RedirectResponse(
                    url=request.url.path, status_code=HTTP_303_SEE_OTHER
                )
                response.delete_cookie(
                    key="session", httponly=True, secure=True, samesite="lax"
                )
                return response

        # No valid session, proceed with the route as normal
        return await func(request, *args, **kwargs)

    return wrapper


def redirect_unauthenticated(func: Callable) -> Callable:
    """
    Decorator to check for valid session cookies and redirect unauthenticated users to login.
    If a valid session is found, allows the route to proceed normally.

    Usage:
        @router.get("/app")
        @redirect_unauthenticated
        async def app(request: Request):
            return templates.TemplateResponse("app/dashboard.html", {"request": request})
    """

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Get session cookie
        session = request.cookies.get("session")

        if session:
            try:
                # Check if session is valid
                account = await AccountHelper.find_account_by_session(session)

                # If we get here, session is valid - proceed with the route as normal
                if account:
                    await AccountHelper.update_session_timestamp(
                        account["_id"], session
                    )
                    return await func(request, *args, **kwargs)

            except HTTPException:
                # Invalid session, create response to delete cookie
                response = RedirectResponse(
                    url="/login", status_code=HTTP_303_SEE_OTHER
                )
                response.delete_cookie(
                    key="session", httponly=True, secure=True, samesite="lax"
                )
                return response

        # No valid session, redirect to login
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    return wrapper


# Route Endpoints
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """
    Default endpoint that returns the main page.

    Returns:
        HTMLResponse: The main page.
    """
    return templates.TemplateResponse(
        "home.html", {"request": request, "title": "Home"}
    )


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
@redirect_authenticated
async def login(request: Request):
    """
    Endpoint that returns the login page.

    Returns:
        HTMLResponse: The login page.
    """
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "Login"}
    )


@router.get("/signup", response_class=HTMLResponse, include_in_schema=False)
@redirect_authenticated
async def signup(request: Request):
    """
    Endpoint that returns the signup page.

    Returns:
        HTMLResponse: The signup page.
    """
    return templates.TemplateResponse(
        "signup.html", {"request": request, "title": "Signup"}
    )


@router.get("/app", response_class=HTMLResponse, include_in_schema=False)
@redirect_unauthenticated
async def app(request: Request):
    """
    Endpoint that returns the app page.

    Returns:
        HTMLResponse: The app page.
    """
    return templates.TemplateResponse(
        "app/dashboard.html",
        {
            "request": request,
            "title": "App",
        },
    )


@router.get("/app/api-keys", response_class=HTMLResponse, include_in_schema=False)
@redirect_unauthenticated
async def app_api_keys(request: Request):
    """
    Endpoint that returns the API keys page.

    Returns:
        HTMLResponse: The API keys page.
    """
    return templates.TemplateResponse(
        "app/api_keys.html",
        {
            "request": request,
            "title": "API Keys",
        },
    )


@router.get("/app/requests", response_class=HTMLResponse, include_in_schema=False)
@redirect_unauthenticated
async def app_requests(request: Request):
    """
    Endpoint that returns the Requests page.

    Returns:
        HTMLResponse: The Requests page.
    """
    return templates.TemplateResponse(
        "app/requests.html",
        {
            "request": request,
            "title": "Requests",
        },
    )


@router.get("/app/settings", response_class=HTMLResponse, include_in_schema=False)
@redirect_unauthenticated
async def app_settings(request: Request):
    """
    Endpoint that returns the Settings page.

    Returns:
        HTMLResponse: The Settings page.
    """
    return templates.TemplateResponse(
        "app/settings.html",
        {
            "request": request,
            "title": "Settings",
        },
    )
