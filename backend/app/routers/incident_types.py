from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.domains.incident_types.models import IncidentType
from app.domains.incident_types.schemas import (
    IncidentTypeCreate,
    IncidentTypeResponse,
    IncidentTypeUpdate,
)
from app.domains.incident_types.services import (
    NameAlreadyRegisteredError,
    create_incident_type,
    deactivate_incident_type,
    get_incident_type,
    list_incident_types,
    update_incident_type,
)
from app.domains.users.models import User

router = APIRouter(prefix="/incident-types", tags=["incident_types"])


@router.post(
    "", response_model=IncidentTypeResponse, status_code=status.HTTP_201_CREATED
)
def create_incident_type_endpoint(
    payload: IncidentTypeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> IncidentType:
    try:
        return create_incident_type(db, name=payload.name)
    except NameAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de tipo de incidente já cadastrado.",
        )


@router.get("", response_model=list[IncidentTypeResponse])
def list_incident_types_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[IncidentType]:
    return list_incident_types(db)


@router.get("/{incident_type_id}", response_model=IncidentTypeResponse)
def get_incident_type_endpoint(
    incident_type_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> IncidentType:
    incident_type = get_incident_type(db, incident_type_id)
    if incident_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de incidente não encontrado.",
        )
    return incident_type


@router.patch("/{incident_type_id}", response_model=IncidentTypeResponse)
def update_incident_type_endpoint(
    incident_type_id: int,
    payload: IncidentTypeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> IncidentType:
    try:
        incident_type = update_incident_type(
            db,
            incident_type_id,
            name=payload.name,
            is_active=payload.is_active,
        )
    except NameAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de tipo de incidente já cadastrado.",
        )
    if incident_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de incidente não encontrado.",
        )
    return incident_type


@router.delete("/{incident_type_id}", response_model=IncidentTypeResponse)
def deactivate_incident_type_endpoint(
    incident_type_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> IncidentType:
    incident_type = deactivate_incident_type(db, incident_type_id)
    if incident_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de incidente não encontrado.",
        )
    return incident_type
