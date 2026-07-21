"""Schemas Pydantic"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class RouteUpdate(BaseModel):
    """Campos opcionais"""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    is_active: bool | None = None


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
