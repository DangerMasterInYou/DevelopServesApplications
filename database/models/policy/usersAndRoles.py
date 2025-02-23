from database.models.models import Base
from sqlalchemy import Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class UserAndRoleModel(Base):
    __tablename__ = "usersAndRoles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
