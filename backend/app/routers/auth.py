from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.domains.auth.schemas import LoginRequest, TokenResponse
from app.domains.auth.services import login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_endpoint(
    payload: LoginRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    token = login(db, payload.email, payload.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos.",
        )
    return TokenResponse(access_token=token)
