from pydantic import BaseModel


class BarbershopAdminAssign(BaseModel):
    user_id: int


class BarbershopAdminAssignmentResponse(BaseModel):

    id: int
    user_id: int
    barbershop_id: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class BarbershopAdminResponse(BaseModel):

    id: int
    user_id: int
    barbershop_id: int

    first_name: str
    last_name: str
    email: str

    is_active: bool


class BarbershopAdminActionResponse(BaseModel):
    message: str