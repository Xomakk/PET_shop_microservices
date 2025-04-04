from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import auth.exceptions as error
from utils import get_password_hash, verify_password
from auth.services.token_service import TokenService
from fastapi import Response
from config import settings
from auth.models import User
from auth.schemas import SUser, SUserCreate, SUserUpdate, SChangePassword
from auth.dao import UserDAO
from auth.tasks import send_email_task
from database import redis
import random


class AuthService:
    """Service for handling authentication and user management operations."""

    confirm_redis_prefix = "confirm_code:"

    @classmethod
    async def send_confirmation_code(cls, email: EmailStr):
        """Send a confirmation code to the user's email.

        Args:
            email (EmailStr): user email.
        """
        if await redis.exists(cls.confirm_redis_prefix + email):
            raise error.ConfirmCodeAlreadySend

        code = random.randint(100000, 999999)

        await redis.set(
            name=cls.confirm_redis_prefix + email,
            value=str(code),
            ex=300,
        )
        send_email_task.delay(
            subject="Confirmation email",
            body="Your code for confirmation: {}".format(code),
            recipient_list=[email],
        )

    @classmethod
    async def check_confirmation_code(cls, email: EmailStr, code: int) -> None:
        """Check if the confirmation code is valid.

        Args:
            email (EmailStr): user email.
            code (int): confirmation code.

        Raises:
            error.InvalidConfirmationCode: If the confirmation code is invalid or expired.
        """
        redis_code: bytes = await redis.get(cls.confirm_redis_prefix + email)

        if not redis_code:
            raise error.ExpiredConfirmationCode

        if redis_code.decode("utf-8") != str(code):
            raise error.InvalidConfirmationCode

        await redis.delete(cls.confirm_redis_prefix + email)

    @staticmethod
    async def login(
        session: AsyncSession, response: Response, email: str, password: str
    ) -> SUser:
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
            raise error.BadCredentialsError

        if not verify_password(password, user.password_hash):
            raise error.BadCredentialsError

        access_token = TokenService.create_access_token(
            {"sub": str(user.id), "is_admin": user.is_admin or user.is_super_admin}
        )
        response.set_cookie(
            settings.ACCESS_TOKEN,
            value=access_token,
            max_age=settings.TOKEN_LIFETIME,
            httponly=True,
            secure=not settings.DEV_MODE,
            samesite="lax",
        )

        return SUser.model_validate(user)

    @staticmethod
    async def register(session: AsyncSession, user_data: SUserCreate) -> None:
        """Register new user in the system.

        Args:
            session: AsyncSession for database operations
            user_data: User registration data (email, password, etc.)

        Raises:
            error.EmailAlreadyUsedError: If email is already registered
            error.InvalidConfirmationCode: If confirmation code is invalid or expired
        """
        existing_user = await UserDAO(session).find_one_or_none(email=user_data.email)

        if existing_user:
            raise error.EmailAlreadyUsedError

        if user_data.password != user_data.repeat_password:
            raise error.RepeatPasswordError

        user_dict = user_data.model_dump()
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]
        del user_dict["repeat_password"]

        await UserDAO(session).create(user_dict)
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
        session: AsyncSession, user_id: int, update_data: SUserUpdate
    ) -> SUser:
        """Update user information.

        Args:
            session: AsyncSession for database operations
            user_id: ID of the user to update
            update_data: SUserUpadte schema with fields to update

        Raises:
            error.NotFoundUserError: If no user found with provided ID

        Returns:
            Updated user information in SUser schema format
        """
        user = await UserDAO(session).find_one_or_none(id=user_id)
        if not user:
            raise error.NotFoundUserError

        update_dict = update_data.model_dump(exclude_none=True)
        updated_user = await UserDAO(session).update_one(user_id, update_dict)
        await session.commit()
        print(updated_user)
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

    @staticmethod
    async def change_password(
        session: AsyncSession, user_id: int, data: SChangePassword
    ) -> None:
        """Change the password for a user after validating all requirements.

        Args:
            session (AsyncSession): The database session to use for operations.
            user_id (int): The ID of the user whose password will be changed.
            data (SChangePassword): An object containing:
                - password: The user's current password
                - new_password: The desired new password
                - repeat_password: Confirmation of the new password

        Raises:
            NotFoundUserError: If no user is found with the provided user_id.
            PasswordError: If the current password provided doesn't match the stored hash.
            NewPasswordError: If the new password is identical to the current password.
            RepeatPasswordError: If the new password and confirmation don't match.
        """
        user: User = await UserDAO(session).find_one_or_none(id=user_id)

        if not user:
            raise error.NotFoundUserError

        if not verify_password(data.password, user.password_hash):
            raise error.PasswordError

        if data.password == data.new_password:
            raise error.NewPasswordError

        if data.new_password != data.repeat_password:
            raise error.RepeatPasswordError

        await UserDAO(session).update_one(
            user_id, {"password_hash": get_password_hash(data.new_password)}
        )
        await session.commit()

    @staticmethod
    async def forgot_password(): ...  # TODO: сделать отправку ссылки для восстановления пароля
