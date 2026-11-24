from datetime import date, time

from pydantic import BaseModel


class AvailabilitySlot(BaseModel):

    start_time: time
    end_time: time


class AvailabilityResponse(BaseModel):

    barber_id: int
    service_id: int

    date: date

    duration_minutes: int

    available: bool

    slots: list[AvailabilitySlot]