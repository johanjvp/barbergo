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


class BarbershopSchedule(Base):

    __tablename__ = "barbershop_schedules"

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True
    )

    barbershop_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "barbershops.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    day_of_week: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    open_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    close_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    is_open: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )