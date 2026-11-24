from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidBarbershopSearchError
)

from app.services.discovery_service import (
    DiscoveryService
)


class DiscoveryController:

    @staticmethod
    def discover(
        db: Session,
        **filters
    ):

        try:

            return (
                DiscoveryService.discover(
                    db=db,
                    **filters
                )
            )


        except InvalidBarbershopSearchError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,

                detail=str(error)
            )