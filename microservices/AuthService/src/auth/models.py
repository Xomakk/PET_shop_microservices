from sqlalchemy.orm import Mapped, mapped_column
from database import BaseModel


class User(BaseModel):
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]

    is_admin: Mapped[bool] = mapped_column(
        default=False, server_default="false", nullable=False
    )
    is_super_admin: Mapped[bool] = mapped_column(
        default=False, server_default="false", nullable=False
    )

    def __repr__(self):
        return f"{self.__class__.__name__} (id={self.id})"
