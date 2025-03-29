from sqlalchemy.ext.asyncio import AsyncSession
import exceptions as error
from utils import get_password_hash, verify_password, create_access_token
from fastapi import Response
from config import settings
from auth.models import User
from auth.schemas import SUser, SUserCreate
from auth.dao import UserDAO


class AuthService:
    """Service for handling authentication and user management operations."""

    @staticmethod
    async def login(
        session: AsyncSession, response: Response, email: str, password: str
    ) -> User:
        """Authenticate user and set access token cookie.

        Args:
            session: AsyncSession for database operations
            response: FastAPI Response object to set cookies
            email: User's email address
            password: User's plain text password

        Raises:
            error.NotFoundUserError: If no user found with provided email
            error.BadCredentialsError: If provided password doesn't match

        Returns:
            Authenticated User object
        """
        user: User = await UserDAO(session).find_one_or_none(email=email)

        if not user:
            raise error.NotFoundUserError

        if not verify_password(password, user.password_hash):
            raise error.BadCredentialsError

        access_token = create_access_token({"sub": user.id})
        response.set_cookie(
            "access_token",
            value=access_token,
            max_age=settings.TOKEN_LIFETIME,
            httponly=True,
            secure=not settings.DEV_MODE,  # HTTPS only in production
            samesite="lax",
        )

        return user

    @staticmethod
    async def register(session: AsyncSession, user_data: SUserCreate) -> None:
        """Register new user in the system.

        Args:
            session: AsyncSession for database operations
            user_data: User registration data (email, password, etc.)

        Raises:
            error.EmailAlreadyUsedError: If email is already registered
        """
        existing_user = await UserDAO(session).find_one_or_none(email=user_data.email)

        if existing_user:
            raise error.EmailAlreadyUsedError

        user_dict = user_data.model_dump()
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]  # Remove plain password before saving

        await UserDAO(session).create(**user_dict)
        await session.commit()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> SUser:
        """Retrieve user information by ID.

        Args:
            session: AsyncSession for database operations
            user_id: ID of the user to retrieve

        Raises:
            error.NotFoundUserError: If no user found with provided ID

        Returns:
            User information in SUser schema format
        """
        user = await UserDAO(session).find_one_or_none(id=user_id)

        if not user:
            raise error.NotFoundUserError

        return SUser.model_validate(user)

    @staticmethod
    async def edit_user(
        session: AsyncSession, user_id: int, update_data: dict
    ) -> SUser:
        """Update user information.

        Args:
            session: AsyncSession for database operations
            user_id: ID of the user to update
            update_data: Dictionary with fields to update

        Raises:
            error.NotFoundUserError: If no user found with provided ID

        Returns:
            Updated user information in SUser schema format
        """
        user = await UserDAO(session).find_one_or_none(id=user_id)
        if not user:
            raise error.NotFoundUserError

        updated_user = await UserDAO(session).update_one(user_id, update_data)
        await session.commit()
        return SUser.model_validate(updated_user)

    @staticmethod
    async def remove_user(session: AsyncSession, user_id: int) -> None:
        """Delete user from the system.

        Args:
            session: AsyncSession for database operations
            user_id: ID of the user to delete

        Raises:
            error.NotFoundUserError: If no user found with provided ID
        """
        user = await UserDAO(session).find_one_or_none(id=user_id)
        if not user:
            raise error.NotFoundUserError

        await UserDAO(session).delete_one(user_id)
        await session.commit()

    async def change_password(): ...