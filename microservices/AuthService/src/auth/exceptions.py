"""Auth exceptions."""

from fastapi import status


class AuthServiceError(Exception):
    status_code: int
    message: str


class NotFoundUserError(AuthServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found."


class BadCredentialsError(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad credentials"


class EmailAlreadyUsedError(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Email already used."


class PermissionError(AuthServiceError):
    status_code = status.HTTP_403_FORBIDDEN
    message = "You dont have permission for this action."
