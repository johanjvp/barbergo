from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Time,
    TIMESTAMP,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import (
    INTEGER,
    TINYINT
)

from app.db.base import Base


class BarbershopBreak(Base):

    __tablename__ = "barbershop_breaks"

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
        TINYINT(unsigned=True),
        nullable=False
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=text("'Descanso'")
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1")
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )