"""Custom exceptions for CloakBrowser Manager client."""


class APIError(Exception):
    """Base exception for Manager API errors."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised when Manager returns 401 Unauthorized."""
    pass


class NotFoundError(APIError):
    """Raised when Manager returns 404 Not Found."""
    pass


class ConflictError(APIError):
    """Raised when Manager returns 409 Conflict."""
    pass


def _raise_for_status(status_code: int, detail: str = "") -> None:
    """Map HTTP status code to appropriate exception."""
    if 200 <= status_code < 300:
        return
    if status_code == 401:
        raise AuthenticationError(detail or "Authentication failed", status_code)
    if status_code == 404:
        raise NotFoundError(detail or "Resource not found", status_code)
    if status_code == 409:
        raise ConflictError(detail or "Resource conflict", status_code)
    raise APIError(detail or f"API error (HTTP {status_code})", status_code)
