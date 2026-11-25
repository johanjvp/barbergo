from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.controllers.booking_controller import BookingController
from app.core.exceptions import (
    BookingCancellationWindowError,
    BookingNotFoundError,
    InvalidBookingStatusTransitionError,
)
from app.core.rate_limit import check_rate_limit, client_ip
from app.db.session import get_db
from app.schemas.guest_schema import (
    GuestBookingCreate,
    GuestBookingCreated,
    GuestBookingView,
    GuestCodeRequest,
    GuestCodeResponse,
)
from app.services.guest_booking_service import GuestBookingService

router = APIRouter(prefix="/guest", tags=["Reservas sin cuenta"])


@router.post("/verification-code", response_model=GuestCodeResponse)
def request_verification_code(
    data: GuestCodeRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    check_rate_limit(f"guest-code:{client_ip(request)}", max_hits=10, window_seconds=3600)
    minutes = GuestBookingService.request_code(db, str(data.email))
    return GuestCodeResponse(expires_in_minutes=minutes)


@router.post(
    "/bookings",
    response_model=GuestBookingCreated,
    status_code=status.HTTP_201_CREATED,
)
def create_guest_booking(
    data: GuestBookingCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    check_rate_limit(f"guest-booking:{client_ip(request)}", max_hits=10, window_seconds=3600)

    # Reutiliza el mapeo de errores de negocio de las reservas normales
    # (horario, conflicto, barbería inactiva, domicilio, etc.).
    try:
        return BookingController.create_guest(db, data)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible crear la reserva.",
        )


def _token_errors(error: Exception):
    if isinstance(error, BookingNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Reserva no encontrada.")
    if isinstance(error, (InvalidBookingStatusTransitionError, BookingCancellationWindowError)):
        return HTTPException(status.HTTP_409_CONFLICT, str(error))
    return error


@router.get("/bookings/{token}", response_model=GuestBookingView)
def get_guest_booking(token: str, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(f"guest-view:{client_ip(request)}", max_hits=60, window_seconds=600)
    try:
        return GuestBookingService.get_by_token(db, token)
    except Exception as error:
        raise _token_errors(error)


@router.post("/bookings/{token}/cancel", response_model=GuestBookingView)
def cancel_guest_booking(token: str, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(f"guest-cancel:{client_ip(request)}", max_hits=20, window_seconds=600)
    try:
        return GuestBookingService.cancel_by_token(db, token)
    except Exception as error:
        raise _token_errors(error)
