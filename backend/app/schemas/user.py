from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    QA_MANAGER = "QA_MANAGER"
    INVESTIGATOR = "INVESTIGATOR"
    VIEWER = "VIEWER"


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(..., serialization_alias="name")
    email: str
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: Any) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.full_name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
