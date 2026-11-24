from datetime import (
    date,
    datetime,
    timedelta
)

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarberNotFoundError,
    PastDateError,
    ServiceNotAvailableForBarberError
)

from app.repositories.availability_repository import (
    AvailabilityRepository
)


class AvailabilityService:

    SLOT_INTERVAL_MINUTES = 15


    # =====================================================
    # DETECTAR CRUCE ENTRE DOS INTERVALOS
    # =====================================================

    @staticmethod
    def _overlaps(
        start_a: datetime,
        end_a: datetime,
        start_b: datetime,
        end_b: datetime
    ) -> bool:

        return (
            start_a < end_b
            and end_a > start_b
        )


    # =====================================================
    # CALCULAR DISPONIBILIDAD
    # =====================================================

    @staticmethod
    def get_availability(
        db: Session,
        barber_id: int,
        service_id: int,
        requested_date: date
    ):

        # -------------------------------------------------
        # 1. NO PERMITIR FECHAS PASADAS
        # -------------------------------------------------

        if requested_date < date.today():
            raise PastDateError()


        # -------------------------------------------------
        # 2. COMPROBAR BARBERO
        # -------------------------------------------------

        barber = (
            AvailabilityRepository.get_barber(
                db,
                barber_id
            )
        )

        if not barber:
            raise BarberNotFoundError()


        # -------------------------------------------------
        # 3. COMPROBAR SERVICIO
        # -------------------------------------------------

        service = (
            AvailabilityRepository
            .get_service_for_barber(
                db,
                barber_id,
                service_id
            )
        )

        if not service:
            raise ServiceNotAvailableForBarberError()


        # -------------------------------------------------
        # 4. DÍA DE LA SEMANA
        #
        # BD:
        # 1 lunes
        # 2 martes
        # ...
        # 7 domingo
        # -------------------------------------------------

        day_of_week = (
            requested_date.weekday() + 1
        )


        # -------------------------------------------------
        # 5. HORARIO DE LA BARBERÍA
        # -------------------------------------------------

        shop_schedule = (
            AvailabilityRepository
            .get_barbershop_schedule(
                db,
                barber.barbershop_id,
                day_of_week
            )
        )

        # Barbería cerrada
        if not shop_schedule:

            return {
                "barber_id": barber_id,
                "service_id": service_id,
                "date": requested_date,
                "duration_minutes":
                    service.duration_minutes,
                "available": False,
                "slots": []
            }


        # -------------------------------------------------
        # 6. HORARIO DEL BARBERO
        # -------------------------------------------------

        barber_schedule = (
            AvailabilityRepository
            .get_barber_schedule(
                db,
                barber_id,
                day_of_week
            )
        )

        # Barbero no trabaja ese día
        if not barber_schedule:

            return {
                "barber_id": barber_id,
                "service_id": service_id,
                "date": requested_date,
                "duration_minutes":
                    service.duration_minutes,
                "available": False,
                "slots": []
            }


        # -------------------------------------------------
        # 7. CONVERTIR HORARIOS EN DATETIME
        # -------------------------------------------------

        shop_start = datetime.combine(
            requested_date,
            shop_schedule.open_time
        )

        shop_end = datetime.combine(
            requested_date,
            shop_schedule.close_time
        )

        barber_start = datetime.combine(
            requested_date,
            barber_schedule.start_time
        )

        barber_end = datetime.combine(
            requested_date,
            barber_schedule.end_time
        )


        # -------------------------------------------------
        # 8. JORNADA EFECTIVA
        #
        # El barbero solo puede trabajar donde coinciden
        # ambos horarios.
        # -------------------------------------------------

        work_start = max(
            shop_start,
            barber_start
        )

        work_end = min(
            shop_end,
            barber_end
        )


        if work_start >= work_end:

            return {
                "barber_id": barber_id,
                "service_id": service_id,
                "date": requested_date,
                "duration_minutes":
                    service.duration_minutes,
                "available": False,
                "slots": []
            }


        # -------------------------------------------------
        # 9. DESCANSOS DE LA BARBERÍA
        # -------------------------------------------------

        shop_breaks = (
            AvailabilityRepository
            .get_barbershop_breaks(
                db,
                barber.barbershop_id,
                day_of_week
            )
        )


        break_intervals = []


        for shop_break in shop_breaks:

            break_start = datetime.combine(
                requested_date,
                shop_break.start_time
            )

            break_end = datetime.combine(
                requested_date,
                shop_break.end_time
            )

            break_intervals.append(
                (
                    break_start,
                    break_end
                )
            )


        # -------------------------------------------------
        # 10. INICIO Y FIN DEL DÍA
        # -------------------------------------------------

        day_start = datetime.combine(
            requested_date,
            datetime.min.time()
        )

        day_end = (
            day_start
            + timedelta(days=1)
        )


        # -------------------------------------------------
        # 11. BLOQUEOS DEL BARBERO
        # -------------------------------------------------

        barber_blocks = (
            AvailabilityRepository.get_blocks(
                db,
                barber_id,
                day_start,
                day_end
            )
        )


        # -------------------------------------------------
        # 12. RESERVAS EXISTENTES
        # -------------------------------------------------

        bookings = (
            AvailabilityRepository
            .get_blocking_bookings(
                db,
                barber_id,
                day_start,
                day_end
            )
        )


        # -------------------------------------------------
        # 13. DURACIÓN DEL SERVICIO
        # -------------------------------------------------

        duration = timedelta(
            minutes=service.duration_minutes
        )


        step = timedelta(
            minutes=(
                AvailabilityService
                .SLOT_INTERVAL_MINUTES
            )
        )


        # -------------------------------------------------
        # 14. PRIMER HORARIO CANDIDATO
        # -------------------------------------------------

        candidate_start = work_start


        # Si consultamos HOY,
        # no mostramos horarios pasados.

        if requested_date == date.today():

            now = datetime.now()

            while candidate_start < now:

                candidate_start += step


        # -------------------------------------------------
        # 15. GENERAR SLOTS
        # -------------------------------------------------

        available_slots = []


        # MUY IMPORTANTE:
        #
        # El servicio completo debe terminar
        # antes o exactamente al terminar la jornada.
        #
        # Ejemplo:
        #
        # cierre = 18:00
        # servicio = 50 minutos
        #
        # 17:00 -> 17:50 ✓
        # 17:15 -> 18:05 ✗
        # -------------------------------------------------

        while (
            candidate_start + duration
            <= work_end
        ):

            candidate_end = (
                candidate_start
                + duration
            )

            unavailable = False


            # ---------------------------------------------
            # 16. DESCANSOS / ALMUERZO
            # ---------------------------------------------

            for (
                break_start,
                break_end
            ) in break_intervals:

                if AvailabilityService._overlaps(
                    candidate_start,
                    candidate_end,
                    break_start,
                    break_end
                ):

                    unavailable = True

                    break


            # ---------------------------------------------
            # 17. BLOQUEOS PERSONALES DEL BARBERO
            # ---------------------------------------------

            if not unavailable:

                for block in barber_blocks:

                    if AvailabilityService._overlaps(
                        candidate_start,
                        candidate_end,
                        block.start_at,
                        block.end_at
                    ):

                        unavailable = True

                        break


            # ---------------------------------------------
            # 18. RESERVAS EXISTENTES
            # ---------------------------------------------

            if not unavailable:

                for booking in bookings:

                    if AvailabilityService._overlaps(
                        candidate_start,
                        candidate_end,
                        booking.start_at,
                        booking.end_at
                    ):

                        unavailable = True

                        break


            # ---------------------------------------------
            # 19. GUARDAR SLOT VÁLIDO
            # ---------------------------------------------

            if not unavailable:

                available_slots.append(
                    {
                        "start_time":
                            candidate_start.time(),

                        "end_time":
                            candidate_end.time()
                    }
                )


            # Siguiente posible inicio
            candidate_start += step


        # -------------------------------------------------
        # 20. RESPUESTA
        # -------------------------------------------------

        return {
            "barber_id":
                barber_id,

            "service_id":
                service_id,

            "date":
                requested_date,

            "duration_minutes":
                service.duration_minutes,

            "available":
                len(available_slots) > 0,

            "slots":
                available_slots
        }