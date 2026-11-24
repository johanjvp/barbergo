from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


class BarbershopAdmin(Base):

    __tablename__ = "barbershop_admins"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "barbershop_id",
            name="uq_barbershop_admin_user_barbershop"
        ),
    )

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    barbershop_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "barbershops.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
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
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )