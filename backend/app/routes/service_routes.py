from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.controllers.service_controller import (
    ServiceController
)

from app.db.session import get_db

from app.dependencies.role_dependencies import (
    require_roles
)

from app.models.user_model import User

from app.schemas.service_schema import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse
)


router = APIRouter(
    tags=["Servicios"]
)


# =========================================================
# CREAR SERVICIO EN BARBERÍA
# =========================================================

@router.post(
    "/barbershops/{barbershop_id}/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service(
    barbershop_id: int,
    data: ServiceCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return ServiceController.create(
        db,
        barbershop_id,
        data,
        current_user
    )


# =========================================================
# LISTAR SERVICIOS DE BARBERÍA
# =========================================================

@router.get(
    "/barbershops/{barbershop_id}/services",
    response_model=list[ServiceResponse]
)
def list_services(
    barbershop_id: int,
    db: Session = Depends(get_db)
):

    return ServiceController.list_by_barbershop(
        db,
        barbershop_id
    )


# =========================================================
# OBTENER SERVICIO
# =========================================================

@router.get(
    "/services/{service_id}",
    response_model=ServiceResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):

    return ServiceController.get_by_id(
        db,
        service_id
    )


# =========================================================
# ACTUALIZAR SERVICIO
# =========================================================

@router.patch(
    "/services/{service_id}",
    response_model=ServiceResponse
)
def update_service(
    service_id: int,
    data: ServiceUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return ServiceController.update(
        db,
        service_id,
        data,
        current_user
    )