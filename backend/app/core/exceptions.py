class EmailAlreadyRegisteredError(Exception):
    pass


class DefaultRoleNotFoundError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass

class BarbershopNotFoundError(Exception):
    pass


class BarbershopForbiddenError(Exception):
    pass

class ServiceNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


class BarberNotFoundError(Exception):
    pass


class UserAlreadyBarberError(Exception):
    pass


class BarberLimitReachedError(Exception):
    pass


class InvalidBarberServiceError(Exception):
    pass

class InvalidScheduleError(Exception):
    pass


class BarberBlockNotFoundError(Exception):
    pass


class BarberScheduleForbiddenError(Exception):
    pass

class ServiceNotAvailableForBarberError(Exception):
    pass


class BarberNotWorkingError(Exception):
    pass


class PastDateError(Exception):
    pass

class BarbershopBreakNotFoundError(Exception):
    pass


class InvalidBarbershopBreakError(Exception):
    pass


class BarbershopBreakConflictError(Exception):
    pass

class BookingConflictError(Exception):
    pass


class BookingStatusNotFoundError(Exception):
    pass


class InvalidBookingTimeError(Exception):
    pass


class PastBookingTimeError(Exception):
    pass


class BarbershopInactiveError(Exception):
    pass

class BookingNotFoundError(Exception):
    pass


class InvalidBookingStatusTransitionError(Exception):
    pass

class BookingForbiddenError(Exception):
    pass


class BookingCancellationWindowError(Exception):
    pass

class InvalidBarbershopSearchError(Exception):
    pass


class HomeServiceError(InvalidBookingTimeError):
    """Reglas del servicio a domicilio (se responde 400 con el mensaje)."""


class PaymentMethodError(InvalidBookingTimeError):
    """Método de pago inválido para la barbería (se responde 400 con el mensaje)."""
