from sqlalchemy.orm import Session

from app.schemas.barbershop_settings_schema import (
    BarbershopSettingsUpdate
)

from app.services.barbershop_settings_service import (
    BarbershopSettingsService
)


class BarbershopSettingsController:

    # =====================================================
    # OBTENER CONFIGURACIÓN
    # =====================================================

    @staticmethod
    def get_settings(
        db: Session,
        barbershop_id: int
    ) -> dict:

        return (
            BarbershopSettingsService
            .get_settings(
                db=db,
                barbershop_id=barbershop_id
            )
        )


    # =====================================================
    # ACTUALIZAR CONFIGURACIÓN
    # =====================================================

    @staticmethod
    def update_settings(
        db: Session,
        barbershop_id: int,
        payload: BarbershopSettingsUpdate
    ) -> dict:

        return (
            BarbershopSettingsService
            .update_settings(
                db=db,
                barbershop_id=barbershop_id,
                payload=payload
            )
        )


    # =====================================================
    # CONFIRMACIÓN AUTOMÁTICA
    # =====================================================

    @staticmethod
    def update_auto_confirmation(
        db: Session,
        barbershop_id: int,
        enabled: bool
    ) -> dict:

        return (
            BarbershopSettingsService
            .update_auto_confirmation(
                db=db,
                barbershop_id=barbershop_id,
                enabled=enabled
            )
        )