from pydantic import BaseModel


class AdminBarbershopStatusUpdate(
    BaseModel
):

    is_active: bool