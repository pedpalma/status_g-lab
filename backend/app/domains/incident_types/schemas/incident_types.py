"""Schemas Pydantic"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncidentTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class IncidentTypeUpdate(BaseModel):
    """Campos opcionais"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class IncidentTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    created_at: datetime
