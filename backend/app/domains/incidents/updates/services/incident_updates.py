"""Serviços do domínio incident_updates: create_update, list_updates_for_incident."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.incident_status.models import IncidentStatus
from app.domains.incidents.models import Incident
from app.domains.incidents.updates.models import IncidentUpdate


class IncidentNotFoundError(Exception):
    """Levanta quando incident_id (path) não corresponde a um incidente existente."""


class InvalidReferenceError(Exception):
    """Levanta quando status_id não corresponde a um status existente."""


@dataclass
class IncidentUpdateWithStatusName:
    """IncidentUpdate + nome do status resolvido, usado só na resposta da API."""

    id: int
    incident_id: int
    status_id: int
    status_name: str
    status_is_final: bool
    comment: str | None
    created_by: int
    created_at: datetime


def _to_update_with_status_name(
    update: IncidentUpdate, statuses: dict[int, IncidentStatus]
) -> IncidentUpdateWithStatusName:
    status = statuses.get(update.status_id)
    return IncidentUpdateWithStatusName(
        id=update.id,
        incident_id=update.incident_id,
        status_id=update.status_id,
        status_name=status.name if status else "",
        status_is_final=status.is_final if status else False,
        comment=update.comment,
        created_by=update.created_by,
        created_at=update.created_at,
    )


def _enrich_with_status_name(
    db: Session, updates: list[IncidentUpdate]
) -> list[IncidentUpdateWithStatusName]:
    """1 query em lote pro status, independente do tamanho da lista
    (mesmo racional de incidents_response_enrichment_pattern, com 1 tabela
    relacionada em vez de 3)."""
    if not updates:
        return []

    status_ids = {u.status_id for u in updates}
    statuses = {
        s.id: s
        for s in db.query(IncidentStatus).filter(IncidentStatus.id.in_(status_ids))
    }

    return [_to_update_with_status_name(u, statuses) for u in updates]


def create_update(
    db: Session,
    incident_id: int,
    status_id: int,
    comment: str | None,
    created_by: int,
) -> IncidentUpdateWithStatusName:
    """Cria a atualização, propaga o novo status pro incidente pai e,
    se o status for final, encerra o incidente (closed_at = now())."""
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise IncidentNotFoundError()

    update = IncidentUpdate(
        incident_id=incident_id,
        status_id=status_id,
        comment=comment,
        created_by=created_by,
    )
    db.add(update)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise InvalidReferenceError()

    # status_id já validado pelo flush acima (FK íntegra), então a busca
    # abaixo sempre encontra a linha.
    status_row = db.get(IncidentStatus, status_id)
    assert status_row is not None, "status sumiu após flush bem-sucedido"

    incident.status_id = status_id
    if status_row.is_final:
        incident.closed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(update)
    return _enrich_with_status_name(db, [update])[0]


def list_updates_for_incident(
    db: Session, incident_id: int
) -> list[IncidentUpdateWithStatusName] | None:
    """Retorna None quando o incidente não existe (o router traduz pra 404)."""
    if db.get(Incident, incident_id) is None:
        return None

    updates = (
        db.query(IncidentUpdate)
        .filter(IncidentUpdate.incident_id == incident_id)
        .order_by(IncidentUpdate.created_at.desc())
        .all()
    )
    return _enrich_with_status_name(db, updates)
