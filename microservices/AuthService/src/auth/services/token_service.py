from jose import jwt
from datetime import datetime, timedelta, timezone
from config import settings
from auth.exceptions import TokenServiceError
from auth.schemas import SAccessToken


class TokenService:
    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """
        Creates a signed JWT access token with expiration.

        Args:
            data: Dictionary containing claims to include in the token.
                Typically includes at least 'sub' (subject) claim.

        Returns:
            str: Encoded JWT token string

        Raises:
            jwt.JWTError: If token encoding fails

        Example:
            >>> token = create_access_token({"sub": 123})
            >>> isinstance(token, str)
            True
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.TOKEN_LIFETIME)
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(
            claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encode_jwt

    @classmethod
    def decode_access_token(cls, token: str) -> SAccessToken:
        """
        Verifies and decodes a JSON Web Token (JWT).

        Parameters:
            token (str): The JWT token to be verified and decoded

        Returns:
            dict: The decoded token payload containing the claims if verification succeeds
            None: Returned when the token fails validation

        Raises:
            HTTPException: Raised when token verification fails due to:
                - Expired signature
                - Invalid signature
                - Malformed token
                - Other JWT validation errors
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except Exception as e:
            raise TokenServiceError

        return SAccessToken.model_validate(payload)
