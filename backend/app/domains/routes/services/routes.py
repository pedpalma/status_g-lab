"""Serviços do domínio routes: create/list/get/update/deactivate."""

from sqlalchemy.orm import Session

from app.domains.routes.models import Route


class NameAlreadyRegisteredError(Exception):
    """Levantado quando o nome da rota já pertence a outra rota."""


def _name_in_use(db: Session, name: str, ignore_route_id: int | None = None) -> bool:
    query = db.query(Route).filter(Route.name == name)
    if ignore_route_id is not None:
        query = query.filter(Route.id != ignore_route_id)
    return query.first() is not None


def create_route(db: Session, name: str, description: str | None) -> Route:
    if _name_in_use(db, name):
        raise NameAlreadyRegisteredError(name)

    route = Route(name=name, description=description)
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def list_routes(db: Session) -> list[Route]:
    return db.query(Route).order_by(Route.name).all()


def get_route(db: Session, route_id: int) -> Route | None:
    return db.get(Route, route_id)


def update_route(
    db: Session,
    route_id: int,
    name: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
) -> Route | None:
    route = db.get(Route, route_id)
    if route is None:
        return None

    if name is not None and name != route.name:
        if _name_in_use(db, name, ignore_route_id=route_id):
            raise NameAlreadyRegisteredError(name)
        route.name = name

    if description is not None:
        route.description = description
    if is_active is not None:
        route.is_active = is_active

    db.commit()
    db.refresh(route)
    return route


def deactivate_route(db: Session, route_id: int) -> Route | None:
    route = db.get(Route, route_id)
    if route is None:
        return None
    route.is_active = False
    db.commit()
    db.refresh(route)
    return route
