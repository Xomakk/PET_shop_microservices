from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import re


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


class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    is_admin: bool
    is_super_admin: bool
