from datetime import date
from typing import Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.controllers.booking_controller import (
    BookingController
)

from app.db.session import (
    get_db
)

from app.dependencies.auth_dependencies import (
    get_current_user
)

from app.models.user_model import (
    User
)

from app.schemas.booking_schema import (
    BookingCreate,
    BookingResponse
)

from app.dependencies.role_dependencies import (
    require_roles
)

from app.services.booking_email_service import (
    BookingEmailService
)


router = APIRouter(
    prefix="/bookings",
    tags=["Reservas"]
)


# =========================================================
# CREAR RESERVA
# =========================================================

@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    data: BookingCreate,

    background_tasks: BackgroundTasks,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    # =====================================================
    # CREAR RESERVA
    # =====================================================

    booking = (
        BookingController.create(
            db,
            data,
            current_user
        )
    )


    # =====================================================
    # PREPARAR CORREO
    # =====================================================

    try:

        email_payload = (
            BookingEmailService
            .prepare_confirmation_payload(
                db,
                booking,
                current_user
            )
        )


        # El correo se ejecuta después
        # de responder al frontend.

        background_tasks.add_task(
            BookingEmailService
                .send_booking_confirmation,
            email_payload
        )


    except Exception as email_error:

        # La reserva ya existe.
        # Un problema preparando el correo
        # no debe convertirla en error.

        print(
            "ERROR PREPARANDO "
            "CORREO DE RESERVA:",
            repr(email_error)
        )


    return booking


# =========================================================
# MIS RESERVAS
# =========================================================

@router.get(
    "/me",
    response_model=list[BookingResponse]
)
def list_my_bookings(

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return (
        BookingController
        .list_my_bookings(
            db,
            current_user
        )
    )
    
    # =========================================================
# RESERVAS DE UN BARBERO
# CON FILTROS DE FECHA Y ESTADO
# =========================================================

@router.get(
    "/barber/{barber_id}",
    response_model=list[BookingResponse]
)
def list_barber_bookings(
    barber_id: int,

    requested_date: date | None = Query(
        default=None,
        alias="date"
    ),

    status_code: Literal[
        "PENDING",
        "CONFIRMED",
        "REJECTED",
        "CANCELLED_BY_CUSTOMER",
        "CANCELLED_BY_BARBER",
        "NO_SHOW",
        "IN_PROGRESS",
        "COMPLETED"
    ] | None = Query(
        default=None,
        alias="status"
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController
        .list_barber_bookings(
            db,
            barber_id,
            current_user,
            requested_date,
            status_code
        )
    )
    
    # =========================================================
# CONFIRMAR RESERVA
# =========================================================

@router.patch(
    "/{booking_id}/confirm",
    response_model=BookingResponse
)
def confirm_booking(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController.confirm_booking(
            db,
            booking_id,
            current_user
        )
    )


# =========================================================
# RECHAZAR RESERVA
# =========================================================

@router.patch(
    "/{booking_id}/reject",
    response_model=BookingResponse
)
def reject_booking(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController.reject_booking(
            db,
            booking_id,
            current_user
        )
    )
    
    # =========================================================
# CANCELAR RESERVA POR EL CLIENTE
# =========================================================

@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse
)
def cancel_booking_by_customer(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return (
        BookingController
        .cancel_by_customer(
            db,
            booking_id,
            current_user
        )
    )
    
    # =========================================================
# INICIAR SERVICIO
# =========================================================

@router.patch(
    "/{booking_id}/start",
    response_model=BookingResponse
)
def start_booking(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController.start_booking(
            db,
            booking_id,
            current_user
        )
    )


# =========================================================
# COMPLETAR SERVICIO
# =========================================================

@router.patch(
    "/{booking_id}/complete",
    response_model=BookingResponse
)
def complete_booking(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController.complete_booking(
            db,
            booking_id,
            current_user
        )
    )
    
    # =========================================================
# MARCAR CLIENTE COMO NO SHOW
# =========================================================

@router.patch(
    "/{booking_id}/no-show",
    response_model=BookingResponse
)
def mark_booking_no_show(
    booking_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        BookingController.mark_no_show(
            db,
            booking_id,
            current_user
        )
    )