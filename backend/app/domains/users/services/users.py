"""Serviços do domínio users: create/list/get/update/deactivate."""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domains.users.models import User


class EmailAlreadyRegisteredError(Exception):
    """Levantado quando o email já pertence a outro usuário."""


def _email_in_use(db: Session, email: str, ignore_user_id: int | None = None) -> bool:
    query = db.query(User).filter(User.email == email)
    if ignore_user_id is not None:
        query = query.filter(User.id != ignore_user_id)
    return query.first() is not None


def create_user(db: Session, name: str, email: str, password: str, role: str) -> User:
    if _email_in_use(db, email):
        raise EmailAlreadyRegisteredError(email)

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.name).all()


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def update_user(
    db: Session,
    user_id: int,
    name: str | None = None,
    email: str | None = None,
    role: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
) -> User | None:
    user = db.get(User, user_id)
    if user is None:
        return None

    if email is not None and email != user.email:
        if _email_in_use(db, email, ignore_user_id=user_id):
            raise EmailAlreadyRegisteredError(email)
        user.email = email

    if name is not None:
        user.name = name
    if role is not None:
        user.role = role
    if password is not None:
        user.password_hash = hash_password(password)
    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User | None:
    user = db.get(User, user_id)
    if user is None:
        return None
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
