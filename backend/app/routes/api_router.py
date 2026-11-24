from fastapi import APIRouter

from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router
from app.routes.discovery_routes import router as discovery_router
from app.routes.barbershop_routes import router as barbershop_router
from app.routes.service_routes import router as service_router
from app.routes.barber_routes import router as barber_router
from app.routes.schedule_routes import router as schedule_router
from app.routes.availability_routes import router as availability_router
from app.routes.booking_routes import router as booking_router
from app.routes.admin_routes import (router as admin_router)
from app.routes.barbershop_settings_routes import (router as barbershop_settings_router)
from app.routes.barbershop_admin_routes import (router as barbershop_admin_router)
from app.routes.barber_agenda_routes import (router as barber_agenda_router)


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(discovery_router)
api_router.include_router(barbershop_router)
api_router.include_router(service_router)
api_router.include_router(barber_router)
api_router.include_router(schedule_router)
api_router.include_router(availability_router)
api_router.include_router(booking_router)
api_router.include_router(admin_router)
api_router.include_router(barbershop_settings_router)
api_router.include_router(barbershop_admin_router)
api_router.include_router(barber_agenda_router)

