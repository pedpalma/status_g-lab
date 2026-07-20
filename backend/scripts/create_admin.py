"""Script de bootstrap: cria o primeiro usuário admin.

POST /users é admin-only. Sem um admin já existente, ninguém consegue
chamar esse endpoint. Este script roda fora da API, uma única vez,
para quebrar esse paradoxo inicial.

Uso (dentro do container backend):
python -m scripts.create_admin

Nome, email e senha são pedidos interativamente. A senha usa getpass,
não fica salva no histórico do shell."""

import getpass
import sys

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domains.users.models import User


def create_admin(name: str, email: str, password: str) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing is not None:
            print(f"Já existe um usuário com o email {email}.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"Admin criado com sucesso: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    name = input("Nome: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Senha: ")

    if not name or not email:
        print("Nome ou email são obrigatórios.")
        sys.exit(1)
    if len(password) < 8:
        print("Senha deve ter pelo menos 8 caracteres.")
        sys.exit(1)

    create_admin(name, email, password)
