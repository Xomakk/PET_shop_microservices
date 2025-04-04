from fastapi.routing import APIRouter
from fastapi import Depends, Response, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import SUserCreate, SUser, SUserUpdate, SChangePassword
from database import SessionDep
from auth.services.auth_service import AuthService
import auth.exceptions as error
from config import settings
from security import Guard
from auth.schemas import SAccessToken, SCredentials
from pydantic import EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    path="/login",
    response_model=SUser,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and set access token cookie",
)
async def login(
    response: Response, credetials: SCredentials, session: SessionDep
) -> SUser:
    """Authenticate user and return user data with access token cookie."""
    try:
        user = await AuthService.login(
            session=session,
            response=response,
            email=credetials.email,
            password=credetials.password,
        )
    except error.AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return user


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    description="Create new user account",
)
async def register(user_data: SUserCreate, session: SessionDep):
    """Register new user in the system."""
    try:
        await AuthService.register(session=session, user_data=user_data)
    except error.AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return {"message": "User registered successfully"}


@router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Clear access token cookie",
)
async def logout(response: Response):
    """Logout user by clearing the access token cookie."""
    response.delete_cookie(
        settings.ACCESS_TOKEN,
        httponly=True,
        secure=not settings.DEV_MODE,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.get(
    path="/me",
    response_model=SUser,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get authenticated user's information",
)
async def get_current_user(
    session: SessionDep,
    token: SAccessToken = Depends(Guard.auth_user),
):
    """Get information about the currently authenticated user."""
    try:
        return await AuthService.get_user_by_id(session=session, user_id=int(token.sub))
    except error.NotFoundUserError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.patch(
    path="/me",
    response_model=SUser,
    status_code=status.HTTP_200_OK,
    summary="Update current user",
    description="Update authenticated user's information",
)
async def update_current_user(
    update_data: SUserUpdate,
    session: SessionDep,
    token: SAccessToken = Depends(Guard.auth_user),
):
    """Update information for the currently authenticated user."""
    try:
        return await AuthService.edit_user(
            session=session, user_id=int(token.sub), update_data=update_data
        )
    except error.NotFoundUserError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.post(
    path="/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change current user's password",
    dependencies=[Depends(Guard.auth_user)],
)
async def change_password(
    password_data: SChangePassword,
    session: SessionDep,
    token: SAccessToken = Depends(Guard.auth_user),
):
    """Change password for the currently authenticated user."""
    try:
        await AuthService.change_password(
            session=session, user_id=int(token.sub), data=password_data
        )
        return {"message": "Password changed successfully"}
    except error.NotFoundUserError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    except error.PasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    except error.NewPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
    except error.RepeatPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation don't match",
        )


@router.post(
    path="/confirm-code/send",
    status_code=status.HTTP_200_OK,
    summary="Send confirm code",
    description="Send confirm code for email verification",
)
async def sen_confirm_code(email: EmailStr):
    """Send confirmation code to user's email."""
    try:
        await AuthService.send_confirmation_code(email=email)
    except error.ConfirmCodeAlreadySend:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Confirmation code already sent",
        )

    return {"message": "Confirmation code sent successfully"}


@router.get(
    path="/confirm-code/check",
    status_code=status.HTTP_200_OK,
    summary="Check confirm code",
    description="Check confirm code for email verification",
)
async def check_confirm_code(
    email: EmailStr, code: int = Query(..., ge=100000, le=999999)
):
    """Check confirmation code for email verification."""
    try:
        await AuthService.check_confirmation_code(email=email, code=code)
    except error.ExpiredConfirmationCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Confirmation code expired"
        )
    except error.InvalidConfirmationCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid confirmation code"
        )

    return {"message": "Confirmation code is valid"}


@router.post(
    path="/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Initiate password reset process",
)
async def forgot_password():
    """Initiate password reset process (TODO)."""
    # TODO: Сделать реализацию восставновления пароля по email
