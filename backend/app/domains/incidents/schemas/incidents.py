"""Schema Pydantic do dominio incidents"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    type_id: int
    route_id: int
    cep: str = Field(min_length=8, max_length=9)
    description: str = Field(min_length=1)


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_id: int
    route_id: int
    status_id: int
    cep: str
    city: str | None
    description: str
    created_by: int
    created_at: datetime
    closed_at: datetime | None
