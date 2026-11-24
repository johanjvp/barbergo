from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import SMALLINT

from app.db.base import Base


class BookingStatus(Base):

    __tablename__ = "booking_statuses"

    id: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True),
        primary_key=True
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )