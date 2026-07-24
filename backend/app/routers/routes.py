from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.domains.routes.models import Route
from app.domains.routes.schemas import RouteCreate, RouteResponse, RouteUpdate
from app.domains.routes.services import (
    NameAlreadyRegisteredError,
    create_route,
    deactivate_route,
    get_route,
    list_routes,
    update_route,
)
from app.domains.users.models import User

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route_endpoint(
    payload: RouteCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> Route:
    try:
        return create_route(db, name=payload.name, description=payload.description)
    except NameAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de rota já cadastrado.",
        )


@router.get("", response_model=list[RouteResponse])
def list_routes_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("tecnico", "admin")),
) -> list[Route]:
    return list_routes(db)


@router.get("/{route_id}", response_model=RouteResponse)
def get_route_endpoint(
    route_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> Route:
    route = get_route(db, route_id)
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rota não encontrada.",
        )
    return route


@router.patch("/{route_id}", response_model=RouteResponse)
def update_route_endpoint(
    route_id: int,
    payload: RouteUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> Route:
    try:
        route = update_route(
            db,
            route_id,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
        )
    except NameAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de rota já cadastrado.",
        )
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rota não encontrada.",
        )
    return route


@router.delete("/{route_id}", response_model=RouteResponse)
def deactivate_route_endpoint(
    route_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> Route:
    route = deactivate_route(db, route_id)
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rota não encontrada.",
        )
    return route
