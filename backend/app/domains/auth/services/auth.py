from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.domains.users.models import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Retorna o usuário se email+senha forem válidos e a conta estiver ativa; senão None."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login(db: Session, email: str, password: str) -> str | None:
    """Autentica e retorna o JWT. None se credenciais inválidas ou usuário inativo."""
    user = authenticate_user(db, email, password)
    if user is None:
        return None
    return create_access_token(subject=str(user.id), role=user.role)
