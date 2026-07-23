"""Router do sobrecurso incident_updates.
Nested sob /incidents/{incident_id}, mesmo padrão de leitura pública +
escrita tecnico|admin do router pai (ver incidents_router_pattern)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.domains.incidents.updates.schemas import (
    IncidentUpdateCreate,
    IncidentUpdateResponse,
)
from app.domains.incidents.updates.services import (
    IncidentNotFoundError,
    IncidentUpdateWithStatusName,
    InvalidReferenceError,
    create_update,
    list_updates_for_incident,
)
from app.domains.users.models import User

router = APIRouter(prefix="/incidents/{incident_id}/updates", tags=["incident_updates"])


@router.post(
    "", response_model=IncidentUpdateResponse, status_code=status.HTTP_201_CREATED
)
def create_update_endpoint(
    incident_id: int,
    payload: IncidentUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("tecnico", "admin")),
) -> IncidentUpdateWithStatusName:
    try:
        return create_update(
            db,
            incident_id=incident_id,
            status_id=payload.status_id,
            comment=payload.comment,
            created_by=current_user.id,
        )
    except IncidentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente não encontrado.",
        )
    except InvalidReferenceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido.",
        )


@router.get("", response_model=list[IncidentUpdateResponse])
def list_updates_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
) -> list[IncidentUpdateWithStatusName]:
    updates = list_updates_for_incident(db, incident_id)
    if updates is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente não encontrado.",
        )
    return updates
