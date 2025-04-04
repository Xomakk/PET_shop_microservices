"""Auth exceptions."""

from fastapi import status


class TokenServiceError(Exception): ...


class AuthServiceError(Exception):
    status_code: int
    message: str


class ConfirmCodeAlreadySend(AuthServiceError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Confirm code already send."


class ExpiredConfirmationCode(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Confirmation code is expired."


class InvalidConfirmationCode(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid confirmation code."


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


class PasswordError(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Wrong password."


class NewPasswordError(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "The new password must not be the same as the old one."


class RepeatPasswordError(AuthServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Repeat password does not match."
