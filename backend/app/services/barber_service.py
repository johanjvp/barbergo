from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopForbiddenError,
    BarbershopNotFoundError,
    BarberLimitReachedError,
    BarberNotFoundError,
    InvalidBarberServiceError,
    UserAlreadyBarberError,
    UserNotFoundError
)

from app.models.barber_model import Barber
from app.models.user_model import User

from app.repositories.barber_repository import (
    BarberRepository
)

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

from app.repositories.user_repository import (
    UserRepository
)

from app.schemas.barber_schema import (
    BarberCreate,
    BarberUpdate
)


class BarberService:

    MAX_BARBERS_PER_SHOP = 5


    # =====================================================
    # VALIDAR PERMISOS DE ADMINISTRACIÓN
    # =====================================================

    @staticmethod
    def _validate_management(
        db: Session,
        barbershop_id: int,
        current_user: User
    ):

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                barbershop_id
            )
        )

        if not barbershop:
            raise BarbershopNotFoundError()


        roles = {
            role.name
            for role in current_user.roles
        }


        is_platform_admin = (
            "PLATFORM_ADMIN" in roles
        )


        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )


        if (
            not is_platform_admin
            and not is_owner
        ):
            raise BarbershopForbiddenError()


        return barbershop


    # =====================================================
    # VALIDAR SERVICIOS DEL BARBERO
    # =====================================================

    @staticmethod
    def _validate_services(
        db: Session,
        barbershop_id: int,
        service_ids: list[int]
    ):

        clean_ids = list(
            set(service_ids)
        )


        valid_ids = (
            BarberRepository
                .get_valid_service_ids(
                    db,
                    barbershop_id,
                    clean_ids
                )
        )


        if (
            len(valid_ids)
            != len(clean_ids)
        ):
            raise InvalidBarberServiceError()


        return valid_ids


    # =====================================================
    # CONSTRUIR RESPUESTA DEL BARBERO
    # =====================================================

    @staticmethod
    def _to_response(
        db: Session,
        barber: Barber
    ) -> dict:

        # ---------------------------------------------
        # OBTENER INFORMACIÓN DEL USUARIO
        # ---------------------------------------------

        user = (
            UserRepository.get_by_id(
                db,
                barber.user_id
            )
        )


        # ---------------------------------------------
        # NOMBRE Y APELLIDO
        # ---------------------------------------------

        first_name = (
            user.first_name
            if user
            else "Barbero"
        )


        last_name = (
            user.last_name
            if user
            else ""
        )


        # ---------------------------------------------
        # SERVICIOS ASOCIADOS AL BARBERO
        # ---------------------------------------------

        service_ids = (
            BarberRepository
                .get_services_for_barber(
                    db,
                    barber.id
                )
        )


        # ---------------------------------------------
        # RESPUESTA
        # ---------------------------------------------

        return {

            "id":
                barber.id,

            "user_id":
                barber.user_id,

            "barbershop_id":
                barber.barbershop_id,


            # =========================================
            # INFORMACIÓN PERSONAL
            # =========================================

            "first_name":
                first_name,

            "last_name":
                last_name,


            # =========================================
            # INFORMACIÓN PROFESIONAL
            # =========================================

            "bio":
                barber.bio,

            "years_experience":
                barber.years_experience,

            "accepts_home_service":
                barber.accepts_home_service,

            "is_active":
                barber.is_active,


            # =========================================
            # SERVICIOS
            # =========================================

            "service_ids":
                service_ids,


            # =========================================
            # FECHAS
            # =========================================

            "created_at":
                barber.created_at,

            "updated_at":
                barber.updated_at
        }


    # =====================================================
    # CREAR BARBERO
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        barbershop_id: int,
        data: BarberCreate,
        current_user: User
    ):

        # ---------------------------------------------
        # VALIDAR BARBERÍA Y PERMISOS
        # ---------------------------------------------

        BarberService._validate_management(
            db,
            barbershop_id,
            current_user
        )


        # ---------------------------------------------
        # VALIDAR USUARIO
        # ---------------------------------------------

        user = (
            UserRepository.get_by_id(
                db,
                data.user_id
            )
        )


        if not user:
            raise UserNotFoundError()


        # ---------------------------------------------
        # VALIDAR QUE NO SEA BARBERO YA
        # ---------------------------------------------

        existing_barber = (
            BarberRepository.get_by_user_id(
                db,
                data.user_id
            )
        )


        if existing_barber:
            raise UserAlreadyBarberError()


        # ---------------------------------------------
        # VALIDAR LÍMITE DE BARBEROS
        # ---------------------------------------------

        active_count = (
            BarberRepository
                .count_active_by_barbershop(
                    db,
                    barbershop_id
                )
        )


        if (
            active_count
            >= BarberService.MAX_BARBERS_PER_SHOP
        ):
            raise BarberLimitReachedError()


        # ---------------------------------------------
        # VALIDAR SERVICIOS
        # ---------------------------------------------

        valid_service_ids = (
            BarberService._validate_services(
                db,
                barbershop_id,
                data.service_ids
            )
        )


        try:

            # -----------------------------------------
            # CREAR BARBERO
            # -----------------------------------------

            barber = Barber(

                user_id=
                    data.user_id,

                barbershop_id=
                    barbershop_id,

                bio=
                    data.bio,

                years_experience=
                    data.years_experience,

                accepts_home_service=
                    data.accepts_home_service
            )


            BarberRepository.create(
                db,
                barber
            )


            # -----------------------------------------
            # ASOCIAR SERVICIOS
            # -----------------------------------------

            BarberRepository.replace_services(
                db,
                barber.id,
                valid_service_ids
            )


            # -----------------------------------------
            # ASIGNAR ROL BARBER
            # -----------------------------------------

            barber_role = (
                UserRepository
                    .get_role_by_name(
                        db,
                        "BARBER"
                    )
            )


            if barber_role:

                role_names = {
                    role.name
                    for role in user.roles
                }


                if (
                    "BARBER"
                    not in role_names
                ):

                    user.roles.append(
                        barber_role
                    )


            # -----------------------------------------
            # CONFIRMAR TRANSACCIÓN
            # -----------------------------------------

            db.commit()

            db.refresh(
                barber
            )


            return (
                BarberService._to_response(
                    db,
                    barber
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR BARBEROS DE UNA BARBERÍA
    # =====================================================

    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ):

        # ---------------------------------------------
        # VALIDAR BARBERÍA
        # ---------------------------------------------

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                barbershop_id
            )
        )


        if not barbershop:
            raise BarbershopNotFoundError()


        # ---------------------------------------------
        # CONSULTAR BARBEROS
        # ---------------------------------------------

        barbers = (
            BarberRepository
                .list_by_barbershop(
                    db,
                    barbershop_id
                )
        )


        # ---------------------------------------------
        # CONSTRUIR RESPUESTAS
        # ---------------------------------------------

        return [

            BarberService._to_response(
                db,
                barber
            )

            for barber in barbers

        ]


    # =====================================================
    # OBTENER BARBERO POR ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        barber_id: int
    ):

        barber = (
            BarberRepository.get_by_id(
                db,
                barber_id
            )
        )


        if not barber:
            raise BarberNotFoundError()


        return (
            BarberService._to_response(
                db,
                barber
            )
        )


    # =====================================================
    # ACTUALIZAR BARBERO
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        barber_id: int,
        data: BarberUpdate,
        current_user: User
    ):

        # ---------------------------------------------
        # OBTENER BARBERO
        # ---------------------------------------------

        barber = (
            BarberRepository.get_by_id(
                db,
                barber_id
            )
        )


        if not barber:
            raise BarberNotFoundError()


        # ---------------------------------------------
        # VALIDAR PERMISOS
        # ---------------------------------------------

        BarberService._validate_management(
            db,
            barber.barbershop_id,
            current_user
        )


        # ---------------------------------------------
        # CAMPOS A ACTUALIZAR
        # ---------------------------------------------

        values = (
            data.model_dump(
                exclude_unset=True,
                exclude={
                    "service_ids"
                }
            )
        )


        # ---------------------------------------------
        # VALIDAR REACTIVACIÓN
        # ---------------------------------------------

        if (
            data.is_active is True
            and not barber.is_active
        ):

            active_count = (
                BarberRepository
                    .count_active_by_barbershop(
                        db,
                        barber.barbershop_id
                    )
            )


            if (
                active_count
                >= BarberService.MAX_BARBERS_PER_SHOP
            ):
                raise BarberLimitReachedError()


        try:

            # -----------------------------------------
            # ACTUALIZAR DATOS
            # -----------------------------------------

            BarberRepository.update(
                db,
                barber,
                values
            )


            # -----------------------------------------
            # ACTUALIZAR SERVICIOS
            # -----------------------------------------

            if (
                data.service_ids
                is not None
            ):

                valid_ids = (
                    BarberService
                        ._validate_services(
                            db,
                            barber.barbershop_id,
                            data.service_ids
                        )
                )


                BarberRepository.replace_services(
                    db,
                    barber.id,
                    valid_ids
                )


            # -----------------------------------------
            # CONFIRMAR CAMBIOS
            # -----------------------------------------

            db.commit()

            db.refresh(
                barber
            )


            return (
                BarberService._to_response(
                    db,
                    barber
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise