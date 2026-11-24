from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    DECIMAL,
    SmallInteger,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


class Barbershop(Base):

    __tablename__ = "barbershops"

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True
    )

    owner_user_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    neighborhood: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=text("'Barranquilla'")
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=text("'Atlántico'")
    )

    latitude: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 7),
        nullable=True
    )

    longitude: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 7),
        nullable=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(190),
        nullable=True
    )

    only_men: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0")
    )

    offers_vip: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0")
    )

    offers_home_service: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0")
    )

    requires_manual_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0")
    )

    cancellation_hours_before: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("2")
    )

    tolerance_minutes: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("10")
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

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )