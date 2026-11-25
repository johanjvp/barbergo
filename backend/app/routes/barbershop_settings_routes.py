from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.controllers.barbershop_settings_controller import (
    BarbershopSettingsController
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

from app.repositories.barbershop_admin_repository import (
    BarbershopAdminRepository
)

from app.schemas.barbershop_settings_schema import (
    AutoConfirmBookingUpdate,
    BarbershopSettingActionResponse,
    BarbershopSettingsResponse,
    BarbershopSettingsUpdate
)


router = APIRouter(
    prefix="/barbershop-settings",
    tags=[
        "Barbershop Settings"
    ]
)


# =====================================================
# OBTENER ROLES DEL USUARIO
# =====================================================

def get_user_roles(
    db: Session,
    user_id: int
) -> set[str]:

    rows = (
        db.execute(
            text(
                """
                SELECT
                    UPPER(r.name) AS role_name

                FROM user_roles ur

                INNER JOIN roles r
                    ON r.id = ur.role_id

                WHERE
                    ur.user_id = :user_id
                """
            ),
            {
                "user_id":
                    user_id
            }
        )
        .mappings()
        .all()
    )

    return {

        str(
            row[
                "role_name"
            ]
        )
        .strip()
        .upper()

        for row in rows

        if row[
            "role_name"
        ]

    }


# =====================================================
# VALIDAR ACCESO A UNA BARBERÍA
# =====================================================

def require_barbershop_settings_access(
    barbershop_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
) -> User:

    # =================================================
    # VALIDAR EXISTENCIA DE LA BARBERÍA
    # =================================================

    barbershop = (
        db.execute(
            text(
                """
                SELECT
                    id,
                    owner_user_id,
                    is_active

                FROM barbershops

                WHERE
                    id = :barbershop_id

                LIMIT 1
                """
            ),
            {
                "barbershop_id":
                    barbershop_id
            }
        )
        .mappings()
        .first()
    )


    if (
        barbershop is None
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=
                "La barbería no existe."
        )


    # =================================================
    # OBTENER ROLES
    # =================================================

    roles = get_user_roles(
        db=db,
        user_id=
            current_user.id
    )


    # =================================================
    # PLATFORM ADMIN
    # =================================================
    #
    # Puede acceder a cualquier barbería.
    # =================================================

    if (
        "PLATFORM_ADMIN"
        in roles
    ):

        return current_user


    # =================================================
    # PROPIETARIO
    # =================================================
    #
    # El propietario siempre puede administrar
    # la configuración de su propia barbería.
    # =================================================

    is_owner = (
        int(
            barbershop[
                "owner_user_id"
            ]
        )
        ==
        int(
            current_user.id
        )
    )


    if is_owner:

        return current_user


    # =================================================
    # BARBERSHOP ADMIN
    # =================================================
    #
    # Tener BARBERSHOP_ADMIN no concede acceso
    # automáticamente a todas las barberías.
    #
    # Debe existir una asignación activa.
    # =================================================

    if (
        "BARBERSHOP_ADMIN"
        in roles
    ):

        has_admin_access = (
            BarbershopAdminRepository
            .has_active_access(
                db=db,
                user_id=
                    current_user.id,
                barbershop_id=
                    barbershop_id
            )
        )


        if has_admin_access:

            return current_user


    # =================================================
    # SIN AUTORIZACIÓN
    # =================================================

    raise HTTPException(
        status_code=
            status.HTTP_403_FORBIDDEN,
        detail=(
            "No tienes permisos para "
            "modificar la configuración "
            "de esta barbería."
        )
    )


# =====================================================
# BARBERÍAS ACCESIBLES PARA CONFIGURACIÓN
# =====================================================
#
# IMPORTANTE:
#
# Esta ruta debe aparecer ANTES de /{barbershop_id}
# para evitar que FastAPI intente interpretar
# "accessible-barbershops" como un ID.
#
# can_manage_admins:
#
# True:
# - PLATFORM_ADMIN
# - propietario de la barbería
#
# False:
# - BARBERSHOP_ADMIN delegado
#
# =====================================================

@router.get(
    "/accessible-barbershops"
)
def get_accessible_barbershops(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    # =================================================
    # OBTENER ROLES
    # =================================================

    roles = get_user_roles(
        db=db,
        user_id=
            current_user.id
    )


    # =================================================
    # PLATFORM ADMIN
    # =================================================
    #
    # Puede ver todas las barberías y gestionar
    # sus administradores.
    # =================================================

    if (
        "PLATFORM_ADMIN"
        in roles
    ):

        rows = (
            db.execute(
                text(
                    """
                    SELECT

                        id,

                        name,

                        city,

                        neighborhood,

                        is_active,

                        1 AS can_manage_admins

                    FROM barbershops

                    ORDER BY

                        is_active DESC,

                        name ASC
                    """
                )
            )
            .mappings()
            .all()
        )


    # =================================================
    # BARBERSHOP ADMIN
    # =================================================
    #
    # Puede ver:
    #
    # 1. Barberías de las cuales sea propietario.
    #
    # 2. Barberías asignadas mediante barbershop_admins.
    #
    # Si es propietario:
    # can_manage_admins = True
    #
    # Si solamente es administrador delegado:
    # can_manage_admins = False
    # =================================================

    elif (
        "BARBERSHOP_ADMIN"
        in roles
    ):

        rows = (
            db.execute(
                text(
                    """
                    SELECT DISTINCT

                        b.id,

                        b.name,

                        b.city,

                        b.neighborhood,

                        b.is_active,

                        CASE

                            WHEN
                                b.owner_user_id =
                                    :user_id

                            THEN 1

                            ELSE 0

                        END AS can_manage_admins

                    FROM barbershops b

                    LEFT JOIN barbershop_admins ba

                        ON
                            ba.barbershop_id =
                                b.id

                        AND
                            ba.user_id =
                                :user_id

                        AND
                            ba.is_active =
                                TRUE

                    WHERE

                        b.owner_user_id =
                            :user_id

                        OR

                        ba.id IS NOT NULL

                    ORDER BY

                        b.is_active DESC,

                        b.name ASC
                    """
                ),
                {
                    "user_id":
                        current_user.id
                }
            )
            .mappings()
            .all()
        )


    # =================================================
    # USUARIO SIN ROL BARBERSHOP_ADMIN
    # =================================================
    #
    # Puede ocurrir que sea propietario de una
    # barbería sin tener BARBERSHOP_ADMIN.
    #
    # En ese caso puede configurar sus propias
    # barberías y gestionar administradores.
    # =================================================

    else:

        rows = (
            db.execute(
                text(
                    """
                    SELECT

                        id,

                        name,

                        city,

                        neighborhood,

                        is_active,

                        1 AS can_manage_admins

                    FROM barbershops

                    WHERE

                        owner_user_id =
                            :owner_user_id

                    ORDER BY

                        is_active DESC,

                        name ASC
                    """
                ),
                {
                    "owner_user_id":
                        current_user.id
                }
            )
            .mappings()
            .all()
        )


    # =================================================
    # SERIALIZAR
    # =================================================

    items = [

        {

            "id":
                int(
                    row[
                        "id"
                    ]
                ),

            "name":
                row[
                    "name"
                ],

            "city":
                row[
                    "city"
                ],

            "neighborhood":
                row[
                    "neighborhood"
                ],

            "is_active":
                bool(
                    row[
                        "is_active"
                    ]
                ),

            "can_manage_admins":
                bool(
                    row[
                        "can_manage_admins"
                    ]
                )

        }

        for row in rows

    ]


    return {

        "items":
            items,

        "total":
            len(
                items
            )

    }


# =====================================================
# OBTENER CONFIGURACIÓN
# =====================================================

@router.get(
    "/{barbershop_id}",
    response_model=
        BarbershopSettingsResponse
)
def get_barbershop_settings(
    barbershop_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_barbershop_settings_access
    )
):

    return (
        BarbershopSettingsController
        .get_settings(
            db=db,
            barbershop_id=
                barbershop_id
        )
    )


# =====================================================
# ACTUALIZAR CONFIGURACIÓN
# =====================================================

@router.patch(
    "/{barbershop_id}",
    response_model=
        BarbershopSettingActionResponse
)
def update_barbershop_settings(
    barbershop_id: int,

    payload:
        BarbershopSettingsUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_barbershop_settings_access
    )
):

    return (
        BarbershopSettingsController
        .update_settings(
            db=db,
            barbershop_id=
                barbershop_id,
            payload=
                payload
        )
    )


# =====================================================
# CONFIRMACIÓN AUTOMÁTICA
# =====================================================

@router.patch(
    "/{barbershop_id}/auto-confirm",
    response_model=
        BarbershopSettingActionResponse
)
def update_auto_confirmation(
    barbershop_id: int,

    payload:
        AutoConfirmBookingUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_barbershop_settings_access
    )
):

    return (
        BarbershopSettingsController
        .update_auto_confirmation(
            db=db,
            barbershop_id=
                barbershop_id,
            enabled=
                payload.enabled
        )
    )