from database.models.base import Base
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    cipher: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
