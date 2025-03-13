from database.models.base import Base
from sqlalchemy import String, Integer, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class ChangeLogModel(Base):
    __tablename__ = "changeLogs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    changed_table: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_id: Mapped[str] = mapped_column(Integer, nullable=False)
    data_before: Mapped[dict] = mapped_column(JSON, nullable=True)
    data_after: Mapped[dict] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_by: Mapped[int] = mapped_column(Integer, nullable=False)
