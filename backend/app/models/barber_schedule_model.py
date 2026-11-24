from datetime import time
from typing import Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    SmallInteger,
    Time
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


class BarberSchedule(Base):

    __tablename__ = "barber_schedules"

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True
    )

    barber_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "barbers.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    day_of_week: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    start_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    end_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    is_working: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )