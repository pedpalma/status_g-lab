"""Serviços do domínio incidents: create/list/get."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.incident_status.models import IncidentStatus
from app.domains.incident_types.models import IncidentType
from app.domains.incidents.models import Incident
from app.domains.routes.models import Route
from app.external.cep import lookup_cep

STATUS_INICIAL = "aberto"


class InvalidReferenceError(Exception):
    """Levanta quando type_id ou route_id não corresponde a um registro existente."""


@dataclass
class IncidentWithNames:
    """Incident + nomes resolvidos (type/route/status), usado só na resposta da API."""

    id: int
    type_id: int
    type_name: str
    route_id: int
    route_name: str
    status_id: int
    status_name: str
    status_is_final: bool
    cep: str
    city: str | None
    street: str | None
    description: str
    created_by: int
    created_at: datetime
    closed_at: datetime | None


def _get_status_id(db: Session, name: str) -> int:
    status_row = db.query(IncidentStatus).filter(IncidentStatus.name == name).first()
    if status_row is None:
        raise RuntimeError(f"Status '{name}' não encontrado em incident_status. ")
    return status_row.id


def _to_incident_with_names(
    incident: Incident,
    types: dict[int, str],
    routes: dict[int, str],
    statuses: dict[int, IncidentStatus],
) -> IncidentWithNames:
    status = statuses.get(incident.status_id)
    return IncidentWithNames(
        id=incident.id,
        type_id=incident.type_id,
        type_name=types.get(incident.type_id, ""),
        route_id=incident.route_id,
        route_name=routes.get(incident.route_id, ""),
        status_id=incident.status_id,
        status_name=status.name if status else "",
        status_is_final=status.is_final if status else False,
        cep=incident.cep,
        city=incident.city,
        street=incident.street,
        description=incident.description,
        created_by=incident.created_by,
        created_at=incident.created_at,
        closed_at=incident.closed_at,
    )


def _enrich_with_names(
    db: Session, incidents: list[Incident]
) -> list[IncidentWithNames]:
    """3 queries em lote (types/routes/status), independente do tamanho da lista."""
    if not incidents:
        return []

    type_ids = {i.type_id for i in incidents}
    route_ids = {i.route_id for i in incidents}
    status_ids = {i.status_id for i in incidents}

    types = {
        t.id: t.name
        for t in db.query(IncidentType).filter(IncidentType.id.in_(type_ids))
    }
    routes = {r.id: r.name for r in db.query(Route).filter(Route.id.in_(route_ids))}
    statuses = {
        s.id: s
        for s in db.query(IncidentStatus).filter(IncidentStatus.id.in_(status_ids))
    }

    return [_to_incident_with_names(i, types, routes, statuses) for i in incidents]


def create_incident(
    db: Session,
    type_id: int,
    route_id: int,
    cep: str,
    description: str,
    created_by: int,
) -> IncidentWithNames:
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
    return _enrich_with_names(db, [incident])[0]


def list_incidents(
    db: Session,
    status_id: int | None = None,
    type_id: int | None = None,
) -> list[IncidentWithNames]:
    query = db.query(Incident)
    if status_id is not None:
        query = query.filter(Incident.status_id == status_id)
    if type_id is not None:
        query = query.filter(Incident.type_id == type_id)
    incidents = query.order_by(Incident.created_at.desc()).all()
    return _enrich_with_names(db, incidents)


def get_incident(db: Session, incident_id: int) -> IncidentWithNames | None:
    incident = db.get(Incident, incident_id)
    if incident is None:
        return None
    return _enrich_with_names(db, [incident])[0]
