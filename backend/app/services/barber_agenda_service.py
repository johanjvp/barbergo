from datetime import (
    date,
    datetime,
    time,
    timedelta
)

from sqlalchemy.orm import Session

from app.repositories.barber_agenda_repository import (
    BarberAgendaRepository
)


class BarberAgendaService:


    # =====================================================
    # MI AGENDA
    # =====================================================

    @staticmethod
    def get_my_agenda(
        db: Session,
        user_id: int,
        date_from: date | None = None,
        date_to: date | None = None
    ) -> dict:


        # =================================================
        # OBTENER BARBERO AUTENTICADO
        # =================================================

        barber = (
            BarberAgendaRepository
            .get_barber_by_user_id(
                db=db,
                user_id=user_id
            )
        )


        if not barber:

            raise ValueError(
                "El usuario autenticado no está registrado como barbero."
            )


        # =================================================
        # VALIDAR BARBERO
        # =================================================

        if not barber[
            "barber_is_active"
        ]:

            raise PermissionError(
                "El perfil de barbero se encuentra inactivo."
            )


        # =================================================
        # VALIDAR BARBERÍA
        # =================================================

        if not barber[
            "barbershop_is_active"
        ]:

            raise PermissionError(
                "La barbería asignada se encuentra inactiva."
            )


        # =================================================
        # FECHA PREDETERMINADA
        # =================================================

        today = (
            date.today()
        )


        if date_from is None:

            date_from = today


        if date_to is None:

            date_to = date_from


        # =================================================
        # VALIDACIONES DE FECHA
        # =================================================

        if (
            date_to
            <
            date_from
        ):

            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial."
            )


        number_of_days = (
            date_to
            -
            date_from
        ).days


        if number_of_days > 31:

            raise ValueError(
                "El rango máximo permitido para consultar la agenda es de 31 días."
            )


        # =================================================
        # CONVERTIR A DATETIME
        # =================================================

        start_at = (
            datetime.combine(
                date_from,
                time.min
            )
        )


        # El límite final es exclusivo.
        #
        # Ejemplo:
        #
        # date_to = 15 nov
        #
        # buscamos hasta:
        #
        # 16 nov 00:00

        end_at = (
            datetime.combine(
                date_to
                +
                timedelta(
                    days=1
                ),
                time.min
            )
        )


        # =================================================
        # CONSULTAR CITAS
        # =================================================

        bookings = (
            BarberAgendaRepository
            .get_bookings(
                db=db,
                barber_id=barber[
                    "barber_id"
                ],
                start_at=start_at,
                end_at=end_at
            )
        )


        # =================================================
        # NORMALIZAR CITAS
        # =================================================

        items = []


        for booking in bookings:

            client_name = (
                f'{booking["client_first_name"]} '
                f'{booking["client_last_name"]}'
            ).strip()


            items.append({

                "id":
                    int(
                        booking[
                            "id"
                        ]
                    ),

                "client_user_id":
                    int(
                        booking[
                            "client_user_id"
                        ]
                    ),

                "client_name":
                    client_name,

                "client_phone":
                    booking[
                        "client_phone"
                    ],

                "service_id":
                    int(
                        booking[
                            "service_id"
                        ]
                    ),

                "service_name":
                    booking[
                        "service_name"
                    ],

                "duration_minutes":
                    int(
                        booking[
                            "duration_minutes"
                        ]
                    ),

                "service_price":
                    booking[
                        "service_price"
                    ],

                "status_id":
                    int(
                        booking[
                            "status_id"
                        ]
                    ),

                "status_code":
                    booking[
                        "status_code"
                    ],

                "status_name":
                    booking[
                        "status_name"
                    ],

                "start_at":
                    booking[
                        "start_at"
                    ],

                "end_at":
                    booking[
                        "end_at"
                    ],

                "customer_notes":
                    booking[
                        "customer_notes"
                    ],

                "barber_notes":
                    booking[
                        "barber_notes"
                    ]

            })


        # =================================================
        # RESPUESTA
        # =================================================

        return {

            "barber": {

                "id":
                    int(
                        barber[
                            "barber_id"
                        ]
                    ),

                "user_id":
                    int(
                        barber[
                            "user_id"
                        ]
                    ),

                "first_name":
                    barber[
                        "first_name"
                    ],

                "last_name":
                    barber[
                        "last_name"
                    ],

                "barbershop_id":
                    int(
                        barber[
                            "barbershop_id"
                        ]
                    ),

                "barbershop_name":
                    barber[
                        "barbershop_name"
                    ],

                "barbershop_address":
                    barber[
                        "barbershop_address"
                    ],

                "barbershop_city":
                    barber[
                        "barbershop_city"
                    ],

                "is_active":
                    bool(
                        barber[
                            "barber_is_active"
                        ]
                    )

            },

            "date_from":
                date_from,

            "date_to":
                date_to,

            "total":
                len(
                    items
                ),

            "items":
                items

        }