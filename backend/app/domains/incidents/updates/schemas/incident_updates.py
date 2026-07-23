"""Schema Pydantic do domínio incident_updates"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentUpdateCreate(BaseModel):
    status_id: int
    comment: str | None = None


class IncidentUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    status_id: int
    status_name: str
    status_is_final: bool
    comment: str | None
    created_by: int
    created_at: datetime
