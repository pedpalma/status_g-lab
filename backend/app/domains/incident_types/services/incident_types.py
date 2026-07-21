"""Serviços do domínio incident_types: create/list/get/update/deactivate."""

from sqlalchemy.orm import Session

from app.domains.incident_types.models import IncidentType


class NameAlreadyRegisteredError(Exception):
    """Levantado quando o nome do tipo de incidente já pertence a outro tipo."""


def _name_in_use(
    db: Session, name: str, ignore_incident_type_id: int | None = None
) -> bool:
    query = db.query(IncidentType).filter(IncidentType.name == name)
    if ignore_incident_type_id is not None:
        query = query.filter(IncidentType.id != ignore_incident_type_id)
    return query.first() is not None


def create_incident_type(db: Session, name: str) -> IncidentType:
    if _name_in_use(db, name):
        raise NameAlreadyRegisteredError(name)

    incident_type = IncidentType(name=name)
    db.add(incident_type)
    db.commit()
    db.refresh(incident_type)
    return incident_type


def list_incident_types(db: Session) -> list[IncidentType]:
    return db.query(IncidentType).order_by(IncidentType.name).all()


def get_incident_type(db: Session, incident_type_id: int) -> IncidentType | None:
    return db.get(IncidentType, incident_type_id)


def update_incident_type(
    db: Session,
    incident_type_id: int,
    name: str | None = None,
    is_active: bool | None = None,
) -> IncidentType | None:
    incident_type = db.get(IncidentType, incident_type_id)
    if incident_type is None:
        return None

    if name is not None and name != incident_type.name:
        if _name_in_use(db, name, ignore_incident_type_id=incident_type_id):
            raise NameAlreadyRegisteredError(name)
        incident_type.name = name

    if is_active is not None:
        incident_type.is_active = is_active

    db.commit()
    db.refresh(incident_type)
    return incident_type


def deactivate_incident_type(db: Session, incident_type_id: int) -> IncidentType | None:
    incident_type = db.get(IncidentType, incident_type_id)
    if incident_type is None:
        return None
    incident_type.is_active = False
    db.commit()
    db.refresh(incident_type)
    return incident_type
