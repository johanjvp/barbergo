from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base


user_roles = Table(

    "user_roles",

    Base.metadata,

    Column(
        "user_id",
        INTEGER(unsigned=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),

    Column(
        "role_id",
        INTEGER(unsigned=True),
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT"
        ),
        primary_key=True
    )
)