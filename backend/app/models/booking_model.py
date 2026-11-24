from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DateTime,
    DECIMAL,
    ForeignKey,
    String,
    TIMESTAMP,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import INTEGER, SMALLINT

from app.db.base import Base


class Booking(Base):

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True
    )

    client_user_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    barbershop_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "barbershops.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    barber_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "barbers.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    service_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "services.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status_id: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True),
        ForeignKey(
            "booking_statuses.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    service_price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2),
        nullable=False
    )

    customer_notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    barber_notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )