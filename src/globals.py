"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This snippet is for all global variables used in the FastAPI application.
"""

from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from helpers.accounts import AccountHelper


class AuthTemplates(Jinja2Templates):
    """Extension of Jinja2Templates that automatically injects auth status"""

    async def get_auth_status(self, request: Request) -> bool:
        """Check if user is authenticated"""
        session = request.cookies.get("session")
        if session:
            try:
                account = await AccountHelper.find_account_by_session(session)
                if account:
                    await AccountHelper.update_session_timestamp(
                        account["_id"], session
                    )
                    return True
            except HTTPException:
                pass
        return False

    def TemplateResponse(
        self,
        name: str,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: dict = None,
        include_in_schema: bool = True,
        **kwargs,
    ) -> HTMLResponse:
        """Override TemplateResponse to automatically include auth status"""
        request = context.get("request")
        if request:
            if "authed" not in context:
                context["authed"] = self.get_auth_status(request)

        return super().TemplateResponse(
            name,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
            include_in_schema=include_in_schema,
            **kwargs,
        )


# Set up templates with automatic auth injection
templates = AuthTemplates(directory="templates")
