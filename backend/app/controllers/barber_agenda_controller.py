from datetime import date

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.user_model import User

from app.services.barber_agenda_service import (
    BarberAgendaService
)


class BarberAgendaController:


    # =====================================================
    # MI AGENDA
    # =====================================================

    @staticmethod
    def get_my_agenda(
        db: Session,
        current_user: User,
        date_from: date | None = None,
        date_to: date | None = None
    ):

        try:

            return (
                BarberAgendaService
                .get_my_agenda(
                    db=db,
                    user_id=current_user.id,
                    date_from=date_from,
                    date_to=date_to
                )
            )


        except PermissionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,
                detail=
                    str(error)
            )


        except ValueError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=
                    str(error)
            )


        except HTTPException:

            raise


        except Exception as error:

            print(
                "ERROR CONSULTANDO "
                "AGENDA DEL BARBERO:",
                repr(error)
            )


            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=
                    "No fue posible consultar la agenda del barbero."
            )