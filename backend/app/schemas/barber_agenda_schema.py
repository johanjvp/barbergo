from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


# =========================================================
# INFORMACIÓN DEL BARBERO AUTENTICADO
# =========================================================

class BarberAgendaProfileResponse(BaseModel):

    id: int

    user_id: int

    first_name: str

    last_name: str

    barbershop_id: int

    barbershop_name: str

    barbershop_address: str

    barbershop_city: str

    is_active: bool


# =========================================================
# CITA DE LA AGENDA
# =========================================================

class BarberAgendaBookingResponse(BaseModel):

    id: int

    client_user_id: int

    client_name: str

    client_phone: Optional[str] = None

    service_id: int

    service_name: str

    duration_minutes: int

    service_price: Decimal

    status_id: int

    status_code: str

    status_name: str

    start_at: datetime

    end_at: datetime

    customer_notes: Optional[str] = None

    barber_notes: Optional[str] = None


# =========================================================
# RESPUESTA DE AGENDA
# =========================================================

class BarberAgendaResponse(BaseModel):

    barber: BarberAgendaProfileResponse

    date_from: date

    date_to: date

    total: int

    items: list[BarberAgendaBookingResponse]