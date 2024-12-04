"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This snippet is for all global variables used in the FastAPI application.
"""

from datetime import datetime
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import accounts


class AuthTemplates(Jinja2Templates):
    """Extension of Jinja2Templates that automatically injects auth status"""

    def get_auth_status(self, request: Request) -> bool:
        """Check if user is authenticated"""
        session_id = request.cookies.get("session")
        if session_id:
            account = accounts.find_one({"sessions._id": session_id})
            if account:
                # Update the session timestamp directly
                accounts.update_one(
                    {"_id": account["_id"], "sessions._id": session_id},
                    {"$set": {"sessions.$.last_used": datetime.now().timestamp()}},
                )
                return True
        return False

    def TemplateResponse(
        self,
        name: str,
        context: dict,
        *,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: None = None,
        **kwargs,
    ) -> HTMLResponse:
        """Override TemplateResponse to automatically include auth status"""
        request = context.get("request")
        if request:
            if "authed" not in context:
                context["authed"] = self.get_auth_status(request)

        return super().TemplateResponse(
            name=name,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            **kwargs,
        )


# Set up templates with automatic auth injection
templates = AuthTemplates(directory="templates")
