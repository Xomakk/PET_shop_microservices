from fastapi import Request, HTTPException, status
from config import settings
from auth.services.token_service import TokenService
from auth.schemas import SAccessToken
from auth.exceptions import TokenServiceError


class Guard:
    """Guard class to check permission and validate access tokens."""

    @classmethod
    def __validate_token(cls, request: Request) -> SAccessToken:
        access_token = request.cookies.get(settings.ACCESS_TOKEN)
        print(access_token)
        try:
            token_data = TokenService.decode_access_token(access_token)
            print(token_data)
        except TokenServiceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or invalid.",
            )

        return token_data

    @classmethod
    def auth_user(cls, request: Request) -> SAccessToken:
        """Check if the user is authenticated by validating the access token.

        Args:
            request (Request): The request object.

        Returns:
            SAccessToken: The validated access token data.
        """

        token = cls.__validate_token(request)
        return token

    @classmethod
    def admin(cls, request: Request) -> SAccessToken:
        """Check if the user is an admin by validating the access token.

        Args:
            request (Request): The request object.

        Returns:
            SAccessToken: The validated access token data.
        """

        token = cls.__validate_token(request)

        if not token.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return token
