from typing import Optional

class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__

class NotFoundException(AppException):
    """Resource not found exception."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="RESOURCE_NOT_FOUND")

class InvalidInputException(AppException):
    """Invalid input exception."""
    def __init__(self, message: str = "Invalid input provided"):
        super().__init__(message, status_code=400, error_code="INVALID_INPUT")

class PermissionDeniedException(AppException):
    """Permission denied exception."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403, error_code="PERMISSION_DENIED")
