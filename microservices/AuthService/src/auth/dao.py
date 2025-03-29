from auth.models import User
from dao import BaseDAO


class UserDAO(BaseDAO[User]):
    model = User
