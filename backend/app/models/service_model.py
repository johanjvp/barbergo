from sqlalchemy.sql import expression
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


class Service(Base):

    __tablename__ = "services"

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

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2),
        nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    is_vip: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=expression.false()
    )

    home_service_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=expression.false()
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=expression.true()
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