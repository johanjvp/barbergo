from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    TIMESTAMP,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


class BarberBlock(Base):

    __tablename__ = "barber_blocks"

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

    start_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )