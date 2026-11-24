import html
import os

from datetime import datetime

import resend

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session


# =========================================================
# VARIABLES DE ENTORNO
# =========================================================

load_dotenv()


class BookingEmailService:

    # =====================================================
    # OBTENER VALOR DE DICT U OBJETO
    # =====================================================

    @staticmethod
    def _get_value(
        source,
        key: str,
        default=None
    ):

        if source is None:
            return default

        if isinstance(source, dict):
            return source.get(
                key,
                default
            )

        return getattr(
            source,
            key,
            default
        )


    # =====================================================
    # CONVERTIR A DATETIME
    # =====================================================

    @staticmethod
    def _to_datetime(
        value
    ) -> datetime | None:

        if value is None:
            return None

        if isinstance(
            value,
            datetime
        ):
            return value

        if isinstance(
            value,
            str
        ):

            try:

                return datetime.fromisoformat(
                    value
                )

            except ValueError:

                return None

        return None


    # =====================================================
    # OBTENER FILA COMPLETA
    # =====================================================

    @staticmethod
    def _get_row(
        db: Session,
        query: str,
        params: dict
    ):

        return (
            db.execute(
                text(query),
                params
            )
            .mappings()
            .first()
        )


    # =====================================================
    # EXTRAER NOMBRE DE UNA FILA
    # =====================================================

    @staticmethod
    def _extract_person_name(
        row
    ) -> str | None:

        if not row:
            return None


        # ---------------------------------------------
        # CAMPOS DE NOMBRE COMPLETO
        # ---------------------------------------------

        for field in [
            "full_name",
            "name",
            "display_name"
        ]:

            value = row.get(
                field
            )

            if value:

                return str(
                    value
                ).strip()


        # ---------------------------------------------
        # NOMBRE + APELLIDO
        # ---------------------------------------------

        first_name = None
        last_name = None


        for field in [
            "first_name",
            "firstname",
            "first_names",
            "nombre",
            "nombres"
        ]:

            if row.get(field):

                first_name = str(
                    row.get(field)
                ).strip()

                break


        for field in [
            "last_name",
            "lastname",
            "surname",
            "last_names",
            "apellido",
            "apellidos"
        ]:

            if row.get(field):

                last_name = str(
                    row.get(field)
                ).strip()

                break


        full_name = (
            f"{first_name or ''} "
            f"{last_name or ''}"
        ).strip()


        if full_name:
            return full_name


        # ---------------------------------------------
        # USERNAME
        # ---------------------------------------------

        if row.get(
            "username"
        ):

            return str(
                row["username"]
            ).strip()


        return None


    # =====================================================
    # OBTENER NOMBRE DEL BARBERO
    # =====================================================

    @staticmethod
    def _get_barber_name(
        db: Session,
        barber_id: int
    ) -> str:

        # ---------------------------------------------
        # LEER BARBERO SIN ASUMIR COLUMNAS
        # ---------------------------------------------

        barber = (
            BookingEmailService
            ._get_row(
                db,
                """
                SELECT *
                FROM barbers
                WHERE id = :barber_id
                """,
                {
                    "barber_id":
                        barber_id
                }
            )
        )


        if not barber:

            return (
                f"Profesional #{barber_id}"
            )


        # ---------------------------------------------
        # ¿EL NOMBRE ESTÁ DIRECTAMENTE EN BARBERS?
        # ---------------------------------------------

        direct_name = (
            BookingEmailService
            ._extract_person_name(
                barber
            )
        )


        if direct_name:

            return direct_name


        # ---------------------------------------------
        # ¿BARBERS TIENE USER_ID?
        # ---------------------------------------------

        user_id = (
            barber.get(
                "user_id"
            )
        )


        if user_id:

            user = (
                BookingEmailService
                ._get_row(
                    db,
                    """
                    SELECT *
                    FROM users
                    WHERE id = :user_id
                    """,
                    {
                        "user_id":
                            user_id
                    }
                )
            )


            user_name = (
                BookingEmailService
                ._extract_person_name(
                    user
                )
            )


            if user_name:

                return user_name


            # -----------------------------------------
            # COMO ÚLTIMO RECURSO USAR EMAIL
            # -----------------------------------------

            if (
                user
                and
                user.get("email")
            ):

                return (
                    str(
                        user["email"]
                    )
                    .split("@")[0]
                )


        return (
            f"Profesional #{barber_id}"
        )


    # =====================================================
    # PREPARAR PAYLOAD
    # =====================================================

    @staticmethod
    def prepare_confirmation_payload(
        db: Session,
        booking,
        current_user
    ) -> dict:

        # =================================================
        # RESERVA
        # =================================================

        booking_id = (
            BookingEmailService
            ._get_value(
                booking,
                "id"
            )
        )


        barbershop_id = (
            BookingEmailService
            ._get_value(
                booking,
                "barbershop_id"
            )
        )


        service_id = (
            BookingEmailService
            ._get_value(
                booking,
                "service_id"
            )
        )


        barber_id = (
            BookingEmailService
            ._get_value(
                booking,
                "barber_id"
            )
        )


        status_id = (
            BookingEmailService
            ._get_value(
                booking,
                "status_id"
            )
        )


        status_code = (
            BookingEmailService
            ._get_value(
                booking,
                "status_code"
            )
        )


        start_at = (
            BookingEmailService
            ._get_value(
                booking,
                "start_at"
            )
        )


        end_at = (
            BookingEmailService
            ._get_value(
                booking,
                "end_at"
            )
        )


        service_price = (
            BookingEmailService
            ._get_value(
                booking,
                "service_price"
            )
        )


        # =================================================
        # VALIDACIONES
        # =================================================

        if booking_id is None:

            raise ValueError(
                "La reserva no contiene id."
            )


        if barbershop_id is None:

            raise ValueError(
                "La reserva no contiene barbershop_id."
            )


        if service_id is None:

            raise ValueError(
                "La reserva no contiene service_id."
            )


        if barber_id is None:

            raise ValueError(
                "La reserva no contiene barber_id."
            )


        # =================================================
        # CLIENTE
        # =================================================

        customer_email = (
            BookingEmailService
            ._get_value(
                current_user,
                "email"
            )
        )


        if not customer_email:

            raise ValueError(
                "El usuario no tiene correo electrónico."
            )


        customer_name = None


        # ---------------------------------------------
        # FULL NAME / NAME
        # ---------------------------------------------

        for field in [
            "full_name",
            "name",
            "display_name"
        ]:

            value = (
                BookingEmailService
                ._get_value(
                    current_user,
                    field
                )
            )


            if value:

                customer_name = str(
                    value
                ).strip()

                break


        # ---------------------------------------------
        # FIRST + LAST NAME
        # ---------------------------------------------

        if not customer_name:

            first_name = (
                BookingEmailService
                ._get_value(
                    current_user,
                    "first_name",
                    ""
                )
                or
                ""
            )


            last_name = (
                BookingEmailService
                ._get_value(
                    current_user,
                    "last_name",
                    ""
                )
                or
                ""
            )


            customer_name = (
                f"{first_name} "
                f"{last_name}"
            ).strip()


        # ---------------------------------------------
        # FALLBACK EMAIL
        # ---------------------------------------------

        if not customer_name:

            customer_name = (
                customer_email
                .split("@")[0]
            )


        # =================================================
        # BARBERÍA
        # =================================================

        barbershop = (
            BookingEmailService
            ._get_row(
                db,
                """
                SELECT *
                FROM barbershops
                WHERE id = :barbershop_id
                """,
                {
                    "barbershop_id":
                        barbershop_id
                }
            )
        )


        barbershop_name = (
            f"Barbería #{barbershop_id}"
        )


        barbershop_address = ""


        cancellation_hours = 2


        if barbershop:

            if barbershop.get(
                "name"
            ):

                barbershop_name = (
                    barbershop[
                        "name"
                    ]
                )


            if barbershop.get(
                "address"
            ):

                barbershop_address = (
                    barbershop[
                        "address"
                    ]
                )


            if (
                barbershop.get(
                    "cancellation_hours_before"
                )
                is not None
            ):

                cancellation_hours = (
                    barbershop[
                        "cancellation_hours_before"
                    ]
                )


        # =================================================
        # SERVICIO
        # =================================================

        service = (
            BookingEmailService
            ._get_row(
                db,
                """
                SELECT *
                FROM services
                WHERE id = :service_id
                """,
                {
                    "service_id":
                        service_id
                }
            )
        )


        service_name = (
            f"Servicio #{service_id}"
        )


        if service:

            for field in [
                "name",
                "service_name",
                "title"
            ]:

                if service.get(
                    field
                ):

                    service_name = (
                        service[field]
                    )

                    break


        # =================================================
        # BARBERO
        # =================================================

        barber_name = (
            BookingEmailService
            ._get_barber_name(
                db,
                barber_id
            )
        )


        # =================================================
        # ESTADO
        # =================================================

        if (
            not status_code
            and
            status_id is not None
        ):

            booking_status = (
                BookingEmailService
                ._get_row(
                    db,
                    """
                    SELECT *
                    FROM booking_statuses
                    WHERE id = :status_id
                    """,
                    {
                        "status_id":
                            status_id
                    }
                )
            )


            if booking_status:

                for field in [
                    "code",
                    "status_code",
                    "name"
                ]:

                    if booking_status.get(
                        field
                    ):

                        status_code = (
                            booking_status[
                                field
                            ]
                        )

                        break


        if not status_code:

            status_code = (
                "PENDING"
            )


        # =================================================
        # RETORNAR PAYLOAD
        # =================================================

        return {

            "to_email":
                customer_email,

            "customer_name":
                customer_name,

            "booking_id":
                booking_id,

            "barbershop_name":
                barbershop_name,

            "barbershop_address":
                barbershop_address,

            "service_name":
                service_name,

            "barber_name":
                barber_name,

            "start_at":
                start_at,

            "end_at":
                end_at,

            "service_price":
                service_price,

            "status_code":
                status_code,

            "cancellation_hours_before":
                cancellation_hours

        }


    # =====================================================
    # ENVIAR CORREO
    # =====================================================

    @staticmethod
    def send_booking_confirmation(
        payload: dict
    ) -> None:

        try:

            # =================================================
            # RESEND
            # =================================================

            api_key = (
                os.getenv(
                    "RESEND_API_KEY"
                )
            )


            from_email = (
                os.getenv(
                    "RESEND_FROM_EMAIL",
                    "BarberGo <onboarding@resend.dev>"
                )
            )


            if not api_key:

                print(
                    "ERROR RESEND BARBERGO: "
                    "RESEND_API_KEY no está configurada."
                )

                return


            resend.api_key = (
                api_key
            )


            # =================================================
            # DATOS
            # =================================================

            booking_id = (
                payload[
                    "booking_id"
                ]
            )


            customer_email = (
                payload[
                    "to_email"
                ]
            )


            customer_name = (
                payload[
                    "customer_name"
                ]
            )


            barbershop_name = (
                payload[
                    "barbershop_name"
                ]
            )


            barbershop_address = (
                payload.get(
                    "barbershop_address"
                )
                or
                ""
            )


            service_name = (
                payload[
                    "service_name"
                ]
            )


            barber_name = (
                payload[
                    "barber_name"
                ]
            )


            start_at = (
                BookingEmailService
                ._to_datetime(
                    payload[
                        "start_at"
                    ]
                )
            )


            end_at = (
                BookingEmailService
                ._to_datetime(
                    payload[
                        "end_at"
                    ]
                )
            )


            service_price = (
                payload[
                    "service_price"
                ]
            )


            status_code = (
                payload[
                    "status_code"
                ]
            )


            cancellation_hours = (
                payload[
                    "cancellation_hours_before"
                ]
            )


            # =================================================
            # FECHA
            # =================================================

            if start_at:

                formatted_date = (
                    start_at.strftime(
                        "%d/%m/%Y"
                    )
                )


                formatted_start_time = (
                    start_at.strftime(
                        "%I:%M %p"
                    )
                )

            else:

                formatted_date = (
                    "No disponible"
                )


                formatted_start_time = (
                    "No disponible"
                )


            if end_at:

                formatted_end_time = (
                    end_at.strftime(
                        "%I:%M %p"
                    )
                )

            else:

                formatted_end_time = (
                    ""
                )


            # =================================================
            # PRECIO
            # =================================================

            try:

                numeric_price = float(
                    service_price
                )


                formatted_price = (
                    f"${numeric_price:,.0f}"
                    .replace(
                        ",",
                        "."
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                formatted_price = (
                    "Consultar"
                )


            # =================================================
            # ESTADO
            # =================================================

            status_labels = {

                "PENDING":
                    "Pendiente de confirmación",

                "CONFIRMED":
                    "Confirmada",

                "REJECTED":
                    "Rechazada",

                "CANCELLED_BY_CUSTOMER":
                    "Cancelada por ti",

                "CANCELLED_BY_BARBER":
                    "Cancelada por la barbería",

                "NO_SHOW":
                    "No asististe",

                "IN_PROGRESS":
                    "En curso",

                "COMPLETED":
                    "Completada"

            }


            status_label = (
                status_labels.get(
                    status_code,
                    status_code
                )
            )


            # =================================================
            # ESCAPAR HTML
            # =================================================

            safe_customer = (
                html.escape(
                    str(
                        customer_name
                    )
                )
            )


            safe_barbershop = (
                html.escape(
                    str(
                        barbershop_name
                    )
                )
            )


            safe_address = (
                html.escape(
                    str(
                        barbershop_address
                    )
                )
            )


            safe_service = (
                html.escape(
                    str(
                        service_name
                    )
                )
            )


            safe_barber = (
                html.escape(
                    str(
                        barber_name
                    )
                )
            )


            safe_status = (
                html.escape(
                    str(
                        status_label
                    )
                )
            )


            # =================================================
            # HTML UBICACIÓN
            # =================================================

            address_html = ""


            if safe_address:

                address_html = f"""
                <div style="
                    margin-top:18px;
                    padding:16px;
                    background:#f5f5f5;
                    border-radius:12px;
                    font-size:12px;
                    line-height:1.6;
                    color:#555555;
                ">
                    <strong>Ubicación</strong>
                    <br>
                    {safe_address}
                </div>
                """


            # =================================================
            # HTML DEL CORREO
            # =================================================

            html_body = f"""
<!DOCTYPE html>

<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
</head>


<body style="
    margin:0;
    padding:0;
    background:#f4f4f4;
    font-family:Arial,Helvetica,sans-serif;
    color:#111111;
">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    role="presentation"
    style="
        background:#f4f4f4;
        padding:40px 15px;
    "
>


<tr>

<td align="center">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    role="presentation"
    style="
        max-width:600px;
        background:#ffffff;
        border-radius:20px;
        overflow:hidden;
    "
>


<tr>

<td style="
    padding:35px;
    background:#111111;
    color:#ffffff;
">

    <div style="
        font-size:27px;
        font-weight:800;
    ">
        BarberGo
    </div>


    <div style="
        margin-top:7px;
        color:#999999;
        font-size:10px;
        letter-spacing:2px;
    ">
        RESERVAS
    </div>

</td>

</tr>


<tr>

<td style="
    padding:35px;
">


    <div style="
        color:#999999;
        font-size:10px;
        font-weight:700;
        letter-spacing:1.5px;
        margin-bottom:10px;
    ">
        RESERVA REGISTRADA
    </div>


    <h1 style="
        margin:0 0 15px;
        font-size:30px;
    ">
        ¡Todo listo, {safe_customer}!
    </h1>


    <p style="
        margin:0 0 28px;
        color:#666666;
        line-height:1.7;
        font-size:14px;
    ">
        Hemos recibido correctamente tu reserva.
        Estos son los detalles de tu cita.
    </p>


    <div style="
        margin-bottom:25px;
        padding:18px;
        background:#111111;
        color:#ffffff;
        border-radius:13px;
    ">

        <div style="
            color:#aaaaaa;
            font-size:9px;
            letter-spacing:1.5px;
        ">
            NÚMERO DE RESERVA
        </div>


        <div style="
            margin-top:5px;
            font-size:24px;
            font-weight:800;
        ">
            #{booking_id}
        </div>

    </div>


    <table
        width="100%"
        cellpadding="0"
        cellspacing="0"
        role="presentation"
        style="
            border-collapse:collapse;
        "
    >


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Barbería
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {safe_barbershop}
            </td>

        </tr>


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Servicio
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {safe_service}
            </td>

        </tr>


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Profesional
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {safe_barber}
            </td>

        </tr>


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Fecha
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {formatted_date}
            </td>

        </tr>


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Horario
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {formatted_start_time}
                -
                {formatted_end_time}
            </td>

        </tr>


        <tr>

            <td style="
                padding:14px 0;
                border-bottom:1px solid #eeeeee;
                color:#888888;
                font-size:12px;
            ">
                Estado
            </td>


            <td
                align="right"
                style="
                    padding:14px 0;
                    border-bottom:1px solid #eeeeee;
                    font-size:13px;
                    font-weight:700;
                "
            >
                {safe_status}
            </td>

        </tr>


        <tr>

            <td style="
                padding:20px 0;
                font-size:13px;
                font-weight:700;
            ">
                TOTAL
            </td>


            <td
                align="right"
                style="
                    padding:20px 0;
                    font-size:20px;
                    font-weight:800;
                "
            >
                {formatted_price}
            </td>

        </tr>


    </table>


    {address_html}


    <div style="
        margin-top:18px;
        padding:16px;
        background:#fff8e8;
        color:#755819;
        border-radius:12px;
        font-size:12px;
        line-height:1.6;
    ">

        <strong>
            Política de cancelación
        </strong>

        <br>

        Puedes cancelar tu reserva hasta
        {cancellation_hours} hora(s) antes
        de la cita.

    </div>


    <p style="
        margin-top:28px;
        color:#999999;
        font-size:11px;
        line-height:1.7;
    ">

        Puedes consultar esta reserva desde
        <strong>Mis reservas</strong>
        en BarberGo.

    </p>


</td>

</tr>


<tr>

<td style="
    padding:22px;
    background:#f7f7f7;
    color:#999999;
    text-align:center;
    font-size:10px;
">

    BarberGo · Tu estilo, tu tiempo.

</td>

</tr>


</table>


</td>

</tr>


</table>


</body>

</html>
"""


            # =================================================
            # TEXTO PLANO
            # =================================================

            text_body = f"""
BarberGo

¡Todo listo, {customer_name}!

Reserva #{booking_id}

Barbería: {barbershop_name}
Servicio: {service_name}
Profesional: {barber_name}
Fecha: {formatted_date}
Horario: {formatted_start_time} - {formatted_end_time}
Estado: {status_label}
Total: {formatted_price}

Puedes cancelar hasta {cancellation_hours} hora(s)
antes de la cita.

BarberGo
""".strip()


            # =================================================
            # ENVIAR CON RESEND
            # =================================================

            params = {

                "from":
                    from_email,

                "to": [
                    customer_email
                ],

                "subject":
                    (
                        f"Reserva #{booking_id} "
                        f"registrada | BarberGo"
                    ),

                "html":
                    html_body,

                "text":
                    text_body

            }


            response = (
                resend.Emails.send(
                    params
                )
            )


            # =================================================
            # LOG
            # =================================================

            print(
                "========================================"
            )

            print(
                "RESEND BARBERGO: CORREO ENVIADO"
            )

            print(
                "Reserva:",
                booking_id
            )

            print(
                "Destinatario:",
                customer_email
            )

            print(
                "Respuesta:",
                response
            )

            print(
                "========================================"
            )


        except Exception as error:

            print(
                "========================================"
            )

            print(
                "ERROR RESEND BARBERGO:"
            )

            print(
                repr(
                    error
                )
            )

            print(
                "========================================"
            )