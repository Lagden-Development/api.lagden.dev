"""
This project is licensed under a non-commercial open-source license.
View the full license here: https://github.com/Lagden-Development/.github/blob/main/LICENSE.

This snippet is a helper function to retrieve the client's IP address from a FastAPI request object.
"""

from fastapi.requests import Request


def get_client_ip(request: Request) -> str:
    """
    Retrieve the client's IP address from the 'CF-Connecting-IP' header if present,
    falling back to the default request client IP if the header is absent.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        str: The client's IP address.
    """
    # Cloudflare header for the real client IP
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    # Fallback to the default client IP
    return request.client.host
