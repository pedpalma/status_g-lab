"""Model SQLAlchemy da table incidents"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("incident_types.id"), nullable=False
    )
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("incident_status.id"), nullable=False
    )
    cep: Mapped[str] = mapped_column(String(9), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
