from sqlalchemy import (
    Column,
    ForeignKey,
    Table
)

from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


barber_services = Table(
    "barber_services",
    Base.metadata,

    Column(
        "barber_id",
        INTEGER(unsigned=True),
        ForeignKey(
            "barbers.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),

    Column(
        "service_id",
        INTEGER(unsigned=True),
        ForeignKey(
            "services.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)