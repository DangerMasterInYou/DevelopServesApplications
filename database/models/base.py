from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from database.models.users import UserModel
from database.models.tokens import TokenModel

__all__ = ["UserModel", "TokenModel"]
