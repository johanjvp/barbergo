"""
Pequeñas diferencias de SQL entre MySQL y PostgreSQL.

El código usa SQL estándar siempre que es posible (TRUE/FALSE, CURRENT_DATE, EXTRACT...).
Solo lo que no tiene forma común vive aquí.
"""

from app.db.session import engine

IS_POSTGRES = engine.dialect.name == "postgresql"


def days_ago(days: int) -> str:
    """Expresión SQL: la fecha de hace N días (sin hora)."""
    if IS_POSTGRES:
        return f"(CURRENT_DATE - INTERVAL '{int(days)} days')"
    return f"DATE_SUB(CURRENT_DATE, INTERVAL {int(days)} DAY)"


def string_agg_distinct(column: str, separator: str = ",") -> str:
    """Expresión SQL: valores distintos de una columna, ordenados y unidos por separador."""
    if IS_POSTGRES:
        return f"STRING_AGG(DISTINCT {column}, '{separator}' ORDER BY {column})"
    return f"GROUP_CONCAT(DISTINCT {column} ORDER BY {column} SEPARATOR '{separator}')"


def same_iso_week_as_today(column: str) -> str:
    """Predicado SQL: la fecha de `column` cae en la semana (lunes a domingo) de hoy."""
    if IS_POSTGRES:
        return f"date_trunc('week', {column}) = date_trunc('week', CURRENT_DATE)"
    return f"YEARWEEK({column}, 1) = YEARWEEK(CURRENT_DATE, 1)"
