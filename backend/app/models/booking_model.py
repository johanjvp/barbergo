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

    client_user_id: Mapped[Optional[int]] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=True
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

    # ---------- reserva sin cuenta (invitado) ----------
    guest_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    guest_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    guest_email: Mapped[Optional[str]] = mapped_column(String(190), nullable=True)
    manage_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True)
    contact_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ---------- servicio a domicilio ----------
    booking_type: Mapped[str] = mapped_column(
        String(12), nullable=False, server_default=text("'IN_SHOP'")
    )
    home_address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    home_latitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 7), nullable=True)
    home_longitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 7), nullable=True)
    home_access_notes: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    home_fee: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2), nullable=False, server_default=text("0")
    )

    # ---------- recordatorios ----------
    reminder_24h_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reminder_2h_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ---------- pago directo ----------
    payment_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payment_status: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default=text("'PENDING'")
    )
    payment_reference: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    payment_reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    payment_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
