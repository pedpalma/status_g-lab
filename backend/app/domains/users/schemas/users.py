"""Schema Pydantic do users domain"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

RoleType = Literal["tecnico", "admin"]


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)
    role: RoleType = "tecnico"


class UserUpdate(BaseModel):
    """Todos os campos são opcionais"""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    role: RoleType | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: RoleType
    is_active: bool
    created_at: datetime
