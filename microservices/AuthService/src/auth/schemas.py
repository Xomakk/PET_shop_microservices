from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
import re


class SAccessToken(BaseModel):
    sub: str
    is_admin: bool = False
    exp: int


class SCredentials(BaseModel):
    email: EmailStr
    password: str


class SUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    repeat_password: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("The password must be at least 8 characters long.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            raise ValueError("Password must contain at least one special character.")

        if " " in value:
            raise ValueError("Password cannot contain spaces.")

        common_passwords = ["password", "12345678", "qwertyui", "admin123"]
        if value.lower() in common_passwords:
            raise ValueError("Password is too common and insecure.")

        return value


class SUserUpdate(BaseModel):
    name: Optional[str]


class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    is_admin: bool
    is_super_admin: bool


class SChangePassword(BaseModel):
    password: str = Field(..., description="Old password")
    new_password: str = Field(..., description="New password")
    repeat_password: str = Field(..., description="Repeat password")

    @field_validator("new_password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("The new password must be at least 8 characters long.")

        if not re.search(r"\d", value):
            raise ValueError("New password must contain at least one digit.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("New password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("New password must contain at least one lowercase letter.")

        if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            raise ValueError(
                "New password must contain at least one special character."
            )

        if " " in value:
            raise ValueError("New password cannot contain spaces.")

        common_passwords = ["password", "12345678", "qwertyui", "admin123"]
        if value.lower() in common_passwords:
            raise ValueError("New password is too common and insecure.")

        return value
