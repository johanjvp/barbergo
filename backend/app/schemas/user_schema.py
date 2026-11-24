from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


# =========================================================
# REGISTRO
# =========================================================

class UserRegister(BaseModel):

    first_name: str = Field(
        min_length=2,
        max_length=100
    )

    last_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    phone: str | None = Field(
        default=None,
        max_length=30
    )

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# =========================================================
# RESPUESTA REGISTRO
# =========================================================

class UserResponse(BaseModel):

    id: int

    first_name: str
    last_name: str

    email: EmailStr

    phone: str | None

    email_verified: bool
    phone_verified: bool

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# ROL
# =========================================================

class RoleResponse(BaseModel):

    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# USUARIO AUTENTICADO
# =========================================================

class UserMeResponse(BaseModel):

    id: int

    first_name: str
    last_name: str

    email: EmailStr

    phone: str | None

    email_verified: bool
    phone_verified: bool

    is_active: bool

    roles: list[RoleResponse]

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )