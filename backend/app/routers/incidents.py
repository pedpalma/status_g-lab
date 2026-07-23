from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.domains.incidents.schemas import IncidentCreate, IncidentResponse
from app.domains.incidents.services import (
    IncidentWithNames,
    InvalidReferenceError,
    create_incident,
    get_incident,
    list_incidents,
)
from app.domains.users.models import User

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident_endpoint(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("tecnico", "admin")),
) -> IncidentWithNames:
    try:
        return create_incident(
            db,
            type_id=payload.type_id,
            route_id=payload.route_id,
            cep=payload.cep,
            description=payload.description,
            created_by=current_user.id,
        )
    except InvalidReferenceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de incidente ou rota inválidos.",
        )


@router.get("", response_model=list[IncidentResponse])
def list_incidents_endpoint(
    db: Session = Depends(get_db),
    status_id: int | None = None,
    type_id: int | None = None,
) -> list[IncidentWithNames]:
    return list_incidents(db, status_id=status_id, type_id=type_id)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
) -> IncidentWithNames:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente não encontrado.",
        )
    return incident
