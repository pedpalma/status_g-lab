"""Serviços do domínio incidents: create/list/get."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.incident_status.models import IncidentStatus
from app.domains.incidents.models import Incident
from app.external.cep import lookup_cep

STATUS_INICIAL = "aberto"


class InvalidReferenceError(Exception):
    """Levanta quando type_id ou route_id não corresponde a um registro existente."""


def _get_status_id(db: Session, name: str) -> int:
    status_row = db.query(IncidentStatus).filter(IncidentStatus.name == name).first()
    if status_row is None:
        raise RuntimeError(f"Status '{name}' não encontrado em incident_status. ")
    return status_row.id


def create_incident(
    db: Session,
    type_id: int,
    route_id: int,
    cep: str,
    description: str,
    created_by: int,
) -> Incident:
    status_id = _get_status_id(db, STATUS_INICIAL)
    cep_result = lookup_cep(cep)

    incident = Incident(
        type_id=type_id,
        route_id=route_id,
        status_id=status_id,
        cep=cep,
        city=cep_result.city,
        street=cep_result.street,
        description=description,
        created_by=created_by,
    )
    db.add(incident)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise InvalidReferenceError()
    db.refresh(incident)
    return incident


def list_incidents(
    db: Session,
    status_id: int | None = None,
    type_id: int | None = None,
) -> list[Incident]:
    query = db.query(Incident)
    if status_id is not None:
        query = query.filter(Incident.status_id == status_id)
    if type_id is not None:
        query = query.filter(Incident.type_id == type_id)
    return query.order_by(Incident.created_at.desc()).all()


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return db.get(Incident, incident_id)
