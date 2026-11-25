"""
Tablas que no tienen modelo ORM (se consultan con SQL directo).

Están definidas con SQLAlchemy para que se creen igual en MySQL y en PostgreSQL.
Se registran en Base.metadata, así que `create_all` las incluye.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    TIMESTAMP,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import expression

from app.db.base import Base


def _uint():
    # En MySQL los ids son UNSIGNED (las claves foráneas deben coincidir); PostgreSQL lo ignora.
    return INTEGER(unsigned=True)


email_verifications = Table(
    "email_verifications",
    Base.metadata,
    Column("id", _uint(), primary_key=True, autoincrement=True),
    Column("email", String(190), nullable=False),
    Column("code_hash", String(64), nullable=False),
    Column("purpose", String(20), nullable=False, server_default=text("'GUEST_BOOKING'")),
    Column("attempts", SmallInteger, nullable=False, server_default=text("0")),
    Column("expires_at", DateTime, nullable=False),
    Column("used_at", DateTime, nullable=True),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Index("idx_email_verifications_email", "email", "created_at"),
)

barbershop_payment_methods = Table(
    "barbershop_payment_methods",
    Base.metadata,
    Column("id", _uint(), primary_key=True, autoincrement=True),
    Column("barbershop_id", _uint(), ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=False),
    Column("method", String(20), nullable=False),
    Column("bank_name", String(80), nullable=True),
    Column("account_type", String(20), nullable=True),
    Column("account_number", String(40), nullable=True),
    Column("account_holder", String(120), nullable=True),
    Column("holder_document", String(30), nullable=True),
    Column("instructions", String(300), nullable=True),
    Column("is_active", Boolean, nullable=False, server_default=expression.true()),
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    UniqueConstraint("barbershop_id", "method", name="uq_shop_method"),
)

_ON = True
_OFF = False

# (columna, valor por defecto) de los ajustes booleanos de la barbería
_SETTINGS_FLAGS = [
    ("bookings_enabled", _ON), ("auto_confirm_bookings", _OFF), ("allow_same_day_booking", _ON),
    ("allow_overbooking", _OFF), ("allow_any_available_barber", _ON), ("allow_customer_notes", _ON),
    ("allow_customer_cancellation", _ON), ("allow_reschedule", _ON), ("customer_can_choose_barber", _ON),
    ("require_customer_account", _OFF), ("require_customer_phone", _OFF),
]
_SETTINGS_NUMBERS = [
    ("booking_interval_minutes", 15), ("max_booking_days_ahead", 60), ("min_booking_notice_minutes", 0),
    ("buffer_between_bookings_minutes", 0), ("cancellation_limit_minutes", 120),
    ("reschedule_limit_minutes", 120), ("tolerance_minutes", 10),
]
_SETTINGS_PERMISSIONS = [
    ("barber_can_confirm_bookings", _ON), ("barber_can_cancel_bookings", _ON), ("barber_can_start_service", _ON),
    ("barber_can_complete_service", _ON), ("barber_can_edit_schedule", _OFF), ("barber_can_block_schedule", _ON),
    ("send_booking_reminders", _ON),
]
_SETTINGS_NOTIFY = [
    ("notify_customer_confirmation", _ON), ("notify_customer_cancellation", _ON),
    ("notify_barber_new_booking", _ON), ("notify_barber_cancellation", _ON),
]


def _flag(name: str, default: bool) -> Column:
    return Column(name, Boolean, nullable=False, server_default=expression.true() if default else expression.false())


def _number(name: str, default: int) -> Column:
    return Column(name, Integer, nullable=False, server_default=text(str(default)))


barbershop_settings = Table(
    "barbershop_settings",
    Base.metadata,
    Column("id", _uint(), primary_key=True, autoincrement=True),
    Column("barbershop_id", _uint(), ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=False, unique=True),
    *[_flag(n, d) for n, d in _SETTINGS_FLAGS],
    *[_number(n, d) for n, d in _SETTINGS_NUMBERS],
    *[_flag(n, d) for n, d in _SETTINGS_PERMISSIONS],
    _number("reminder_minutes_before", 60),
    *[_flag(n, d) for n, d in _SETTINGS_NOTIFY],
    Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

EXTRA_TABLES = [email_verifications, barbershop_payment_methods, barbershop_settings]
