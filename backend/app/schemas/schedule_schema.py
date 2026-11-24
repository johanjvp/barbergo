from datetime import datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# =========================================================
# HORARIO BARBERÍA
# =========================================================

class BarbershopScheduleUpsert(BaseModel):

    open_time: time | None = None
    close_time: time | None = None

    is_open: bool = True

    @model_validator(mode="after")
    def validate_schedule(self):

        if self.is_open:

            if self.open_time is None or self.close_time is None:
                raise ValueError(
                    "Una barbería abierta debe tener "
                    "hora de apertura y cierre."
                )

            if self.close_time <= self.open_time:
                raise ValueError(
                    "La hora de cierre debe ser "
                    "posterior a la hora de apertura."
                )

        else:
            self.open_time = None
            self.close_time = None

        return self


class BarbershopScheduleResponse(BaseModel):

    id: int
    barbershop_id: int
    day_of_week: int

    open_time: time | None
    close_time: time | None

    is_open: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# HORARIO BARBERO
# =========================================================

class BarberScheduleUpsert(BaseModel):

    start_time: time | None = None
    end_time: time | None = None

    is_working: bool = True

    @model_validator(mode="after")
    def validate_schedule(self):

        if self.is_working:

            if self.start_time is None or self.end_time is None:
                raise ValueError(
                    "Un barbero que trabaja ese día "
                    "debe tener hora de inicio y fin."
                )

            if self.end_time <= self.start_time:
                raise ValueError(
                    "La hora de finalización debe ser "
                    "posterior a la hora de inicio."
                )

        else:
            self.start_time = None
            self.end_time = None

        return self


class BarberScheduleResponse(BaseModel):

    id: int
    barber_id: int
    day_of_week: int

    start_time: time | None
    end_time: time | None

    is_working: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# BLOQUEOS
# =========================================================

class BarberBlockCreate(BaseModel):

    start_at: datetime
    end_at: datetime

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    @model_validator(mode="after")
    def validate_dates(self):

        if self.end_at <= self.start_at:
            raise ValueError(
                "La fecha/hora final debe ser "
                "posterior a la inicial."
            )

        return self


class BarberBlockResponse(BaseModel):

    id: int
    barber_id: int

    start_at: datetime
    end_at: datetime

    reason: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    
    # =========================================================
# DESCANSOS DE BARBERÍA
# =========================================================

class BarbershopBreakCreate(BaseModel):

    day_of_week: int = Field(
        ge=1,
        le=7
    )

    start_time: time
    end_time: time

    name: str = Field(
        default="Descanso",
        min_length=2,
        max_length=100
    )

    @model_validator(mode="after")
    def validate_break(self):

        if self.end_time <= self.start_time:
            raise ValueError(
                "La hora final del descanso debe ser "
                "posterior a la hora inicial."
            )

        return self


class BarbershopBreakUpdate(BaseModel):

    day_of_week: int | None = Field(
        default=None,
        ge=1,
        le=7
    )

    start_time: time | None = None
    end_time: time | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    is_active: bool | None = None


class BarbershopBreakResponse(BaseModel):

    id: int
    barbershop_id: int

    day_of_week: int

    start_time: time
    end_time: time

    name: str

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    

# =========================================================
# AGENDA SEMANAL DEL BARBERO
# =========================================================

class AgendaBreakResponse(BaseModel):

    id: int

    name: str

    start_time: time

    end_time: time


class AgendaBlockResponse(BaseModel):

    id: int

    start_at: datetime

    end_at: datetime

    reason: str | None = None


class BarberAgendaDayResponse(BaseModel):

    date: str

    day_of_week: int


    # -----------------------------------------------------
    # HORARIO BARBERÍA
    # -----------------------------------------------------

    is_barbershop_open: bool

    barbershop_open_time: time | None = None

    barbershop_close_time: time | None = None


    # -----------------------------------------------------
    # HORARIO BARBERO
    # -----------------------------------------------------

    is_working: bool

    start_time: time | None = None

    end_time: time | None = None


    # -----------------------------------------------------
    # DESCANSOS Y BLOQUEOS
    # -----------------------------------------------------

    breaks: list[AgendaBreakResponse] = Field(
        default_factory=list
    )

    blocks: list[AgendaBlockResponse] = Field(
        default_factory=list
    )


class BarberWeeklyAgendaResponse(BaseModel):

    barber_id: int

    barbershop_id: int

    week_start: str

    week_end: str

    days: list[BarberAgendaDayResponse] = Field(
        default_factory=list
    )