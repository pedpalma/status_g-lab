"""Model SQLAlchemy da table incident_status"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IncidentStatus(Base):
    __tablename__ = "incident_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
