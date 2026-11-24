from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarberNotFoundError,
    PastDateError,
    ServiceNotAvailableForBarberError
)

from app.services.availability_service import (
    AvailabilityService
)


class AvailabilityController:

    @staticmethod
    def get_availability(
        db: Session,
        barber_id: int,
        service_id: int,
        requested_date: date
    ):

        try:

            return (
                AvailabilityService
                .get_availability(
                    db,
                    barber_id,
                    service_id,
                    requested_date
                )
            )

        # =================================================
        # BARBERO NO EXISTE
        # =================================================

        except BarberNotFoundError:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barbero no encontrado."
            )


        # =================================================
        # EL BARBERO NO REALIZA ESE SERVICIO
        # =================================================

        except ServiceNotAvailableForBarberError:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El barbero no ofrece "
                    "el servicio solicitado."
                )
            )


        # =================================================
        # FECHA PASADA
        # =================================================

        except PastDateError:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No se puede consultar disponibilidad "
                    "para una fecha pasada."
                )
            )