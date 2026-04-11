"""Response-Header für IT-Sicherheit setzen."""

from typing import Final

from fastapi import Response

__all__ = ["set_response_headers"]


ONE_YEAR_IN_SECONDS: Final = 365 * 24 * 60 * 60


def set_response_headers(response: Response) -> Response:
    """Response-Header für IT-Sicherheit setzen."""
    headers: Final = response.headers
    headers["X-Frame-Options"] = "SAMEORIGIN"
    headers["X-XSS-Protection"] = "1; mode=block"
    headers["X-Content-Type-Options"] = "nosniff"
    headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'"
    headers["Strict-Transport-Security"] = (
        f"max-age={ONE_YEAR_IN_SECONDS}; includeSubDomains"
    )
    return response
