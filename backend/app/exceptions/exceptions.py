"""
FinPilot AI – Custom Application Exceptions
Defines base and domain-specific exception classes used across the app.
"""


class FinPilotBaseException(Exception):
    """Root exception for all FinPilot application errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(FinPilotBaseException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, status_code=404)


class BadRequestException(FinPilotBaseException):
    """Raised when the client sends a malformed or invalid request."""

    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(message=message, status_code=400)


class UnauthorizedException(FinPilotBaseException):
    """Raised when authentication is required but missing or invalid."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message=message, status_code=401)


class ForbiddenException(FinPilotBaseException):
    """Raised when the authenticated user lacks permission."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message=message, status_code=403)


class ServiceUnavailableException(FinPilotBaseException):
    """Raised when an external service or dependency is unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(message=message, status_code=503)
