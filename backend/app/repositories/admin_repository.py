from app.db.dialect import days_ago, same_iso_week_as_today, string_agg_distinct
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.user_model import User


class AdminRepository:

    # =====================================================
    # EJECUTAR ESCALAR
    # =====================================================

    @staticmethod
    def _scalar(
        db: Session,
        query: str,
        params: dict | None = None
    ):
        result = (
            db.execute(
                text(query),
                params or {}
            )
            .scalar()
        )

        return result

    # =====================================================
    # LISTADO ADMINISTRATIVO DE BARBERÍAS
    # =====================================================

    @staticmethod
    def list_barbershops_admin(
        db: Session,
        search: str | None = None,
        status_filter: str = "all",
        limit: int = 50,
        offset: int = 0
    ) -> dict:

        conditions = []
        params = {
            "limit": limit,
            "offset": offset
        }

        # =================================================
        # BÚSQUEDA
        # =================================================

        if (
            search
            and
            search.strip()
        ):

            params["search"] = (
                f"%{search.strip().lower()}%"
            )

            conditions.append(
                """
                (
                    LOWER(bs.name)
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            bs.city,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            bs.neighborhood,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            bs.address,
                            ''
                        )
                    )
                    LIKE :search
                )
                """
            )

        # =================================================
        # ESTADO
        # =================================================

        if (
            status_filter ==
            "active"
        ):

            conditions.append(
                "bs.is_active = TRUE"
            )

        elif (
            status_filter ==
            "inactive"
        ):

            conditions.append(
                "bs.is_active = FALSE"
            )

        # =================================================
        # WHERE
        # =================================================

        where_clause = ""

        if conditions:

            where_clause = (
                "WHERE "
                +
                " AND ".join(
                    conditions
                )
            )

        # =================================================
        # TOTAL
        # =================================================

        total = (
            db.execute(
                text(
                    f"""
                    SELECT
                        COUNT(*)

                    FROM barbershops bs

                    {where_clause}
                    """
                ),
                params
            )
            .scalar()
        )

        # =================================================
        # DATOS
        # =================================================

        rows = (
            db.execute(
                text(
                    f"""
                    SELECT

                        bs.id,

                        bs.name,

                        bs.city,

                        bs.neighborhood,

                        bs.address,

                        bs.phone,

                        bs.email,

                        bs.is_active,

                        bs.created_at,


                        COUNT(
                            b.id
                        )
                        AS bookings_count,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN st.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS reserved_value,


                        COALESCE(
                            AVG(
                                CASE

                                    WHEN st.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE NULL

                                END
                            ),
                            0
                        )
                        AS average_ticket,


                        SUM(
                            CASE

                                WHEN st.code =
                                    'COMPLETED'

                                THEN 1

                                ELSE 0

                            END
                        )
                        AS completed_bookings,


                        SUM(
                            CASE

                                WHEN st.code IN (
                                    'CANCELLED_BY_CUSTOMER',
                                    'CANCELLED_BY_BARBER',
                                    'CANCELLED_BY_ADMIN'
                                )

                                THEN 1

                                ELSE 0

                            END
                        )
                        AS cancelled_bookings


                    FROM barbershops bs


                    LEFT JOIN bookings b
                        ON b.barbershop_id =
                            bs.id


                    LEFT JOIN booking_statuses st
                        ON st.id =
                            b.status_id


                    {where_clause}


                    GROUP BY

                        bs.id,
                        bs.name,
                        bs.city,
                        bs.neighborhood,
                        bs.address,
                        bs.phone,
                        bs.email,
                        bs.is_active,
                        bs.created_at


                    ORDER BY

                        bookings_count DESC,
                        bs.created_at DESC


                    LIMIT :limit
                    OFFSET :offset
                    """
                ),
                params
            )
            .mappings()
            .all()
        )

        items = []

        for row in rows:

            items.append(
                {

                    "id":
                        int(
                            row["id"]
                        ),

                    "name":
                        row["name"],

                    "city":
                        row["city"],

                    "neighborhood":
                        row["neighborhood"],

                    "address":
                        row["address"],

                    "phone":
                        row["phone"],

                    "email":
                        row["email"],

                    "is_active":
                        bool(
                            row["is_active"]
                        ),

                    "created_at":
                        (
                            row["created_at"]
                            .isoformat()
                            if
                            row["created_at"]
                            else
                            None
                        ),

                    "bookings_count":
                        int(
                            row[
                                "bookings_count"
                            ]
                            or 0
                        ),

                    "completed_bookings":
                        int(
                            row[
                                "completed_bookings"
                            ]
                            or 0
                        ),

                    "cancelled_bookings":
                        int(
                            row[
                                "cancelled_bookings"
                            ]
                            or 0
                        ),

                    "reserved_value":
                        float(
                            row[
                                "reserved_value"
                            ]
                            or 0
                        ),

                    "average_ticket":
                        float(
                            row[
                                "average_ticket"
                            ]
                            or 0
                        )

                }
            )

        return {

            "total":
                int(
                    total
                    or 0
                ),

            "limit":
                limit,

            "offset":
                offset,

            "items":
                items

        }
        
            # =====================================================
    # DETALLE ADMINISTRATIVO DE BARBERÍA
    # =====================================================

    @staticmethod
    def get_barbershop_detail_admin(
        db: Session,
        barbershop_id: int
    ) -> dict | None:

        # =================================================
        # DATOS GENERALES DE LA BARBERÍA
        # =================================================

        barbershop = (
            db.execute(
                text(
                    """
                    SELECT

                        bs.id,

                        bs.name,

                        bs.city,

                        bs.neighborhood,

                        bs.address,

                        bs.phone,

                        bs.email,

                        bs.is_active,

                        bs.created_at

                    FROM barbershops bs

                    WHERE
                        bs.id =
                            :barbershop_id

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


        # =================================================
        # BARBERÍA NO ENCONTRADA
        # =================================================

        if not barbershop:

            return None


        # =================================================
        # MÉTRICAS DE RESERVAS
        # =================================================

        metrics = (
            db.execute(
                text(
                    """
                    SELECT

                        COUNT(
                            b.id
                        )
                            AS bookings_count,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN st.code =
                                        'COMPLETED'

                                    THEN 1

                                    ELSE 0

                                END
                            ),
                            0
                        )
                            AS completed_bookings,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN st.code IN (
                                        'CANCELLED_BY_CUSTOMER',
                                        'CANCELLED_BY_BARBER',
                                        'CANCELLED_BY_ADMIN'
                                    )

                                    THEN 1

                                    ELSE 0

                                END
                            ),
                            0
                        )
                            AS cancelled_bookings,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN st.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN
                                        b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                            AS reserved_value,


                        COALESCE(
                            AVG(
                                CASE

                                    WHEN st.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN
                                        b.service_price

                                    ELSE NULL

                                END
                            ),
                            0
                        )
                            AS average_ticket


                    FROM bookings b

                    LEFT JOIN booking_statuses st
                        ON st.id =
                            b.status_id

                    WHERE
                        b.barbershop_id =
                            :barbershop_id
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


        # =================================================
        # BARBEROS ACTIVOS
        # =================================================

        active_barbers = (
            db.execute(
                text(
                    """
                    SELECT
                        COUNT(*)

                    FROM barbers

                    WHERE
                        barbershop_id =
                            :barbershop_id

                        AND

                        is_active = TRUE
                    """
                ),
                {
                    "barbershop_id":
                        barbershop_id
                }
            )
            .scalar()
        )


        # =================================================
        # RESPUESTA
        # =================================================

        return {

            "id":
                int(
                    barbershop[
                        "id"
                    ]
                ),

            "name":
                barbershop[
                    "name"
                ],

            "city":
                barbershop[
                    "city"
                ],

            "neighborhood":
                barbershop[
                    "neighborhood"
                ],

            "address":
                barbershop[
                    "address"
                ],

            "phone":
                barbershop[
                    "phone"
                ],

            "email":
                barbershop[
                    "email"
                ],

            "is_active":
                bool(
                    barbershop[
                        "is_active"
                    ]
                ),

            "created_at":
                (
                    barbershop[
                        "created_at"
                    ]
                    .isoformat()

                    if
                    barbershop[
                        "created_at"
                    ]

                    else
                    None
                ),

            "metrics": {

                "bookings_count":
                    int(
                        metrics[
                            "bookings_count"
                        ]
                        or 0
                    ),

                "completed_bookings":
                    int(
                        metrics[
                            "completed_bookings"
                        ]
                        or 0
                    ),

                "cancelled_bookings":
                    int(
                        metrics[
                            "cancelled_bookings"
                        ]
                        or 0
                    ),

                "reserved_value":
                    float(
                        metrics[
                            "reserved_value"
                        ]
                        or 0
                    ),

                "average_ticket":
                    float(
                        metrics[
                            "average_ticket"
                        ]
                        or 0
                    ),

                "active_barbers":
                    int(
                        active_barbers
                        or 0
                    )

            }

        }

    # =====================================================
    # CAMBIAR ESTADO BARBERÍA
    # =====================================================

    @staticmethod
    def update_barbershop_status(
        db: Session,
        barbershop_id: int,
        is_active: bool
    ) -> dict | None:

        existing = (
            db.execute(
                text(
                    """
                    SELECT
                        id,
                        name

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

        if not existing:

            return None

        db.execute(
            text(
                """
                UPDATE barbershops

                SET
                    is_active =
                        :is_active

                WHERE
                    id =
                        :barbershop_id
                """
            ),
            {

                "barbershop_id":
                    barbershop_id,

                "is_active":
                    bool(is_active)

            }
        )

        db.commit()

        return {

            "id":
                int(
                    existing["id"]
                ),

            "name":
                existing["name"],

            "is_active":
                is_active

        }

    # =====================================================
    # USUARIOS
    # =====================================================

    @staticmethod
    def count_users(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM users
                """
            )
            or 0
        )

    @staticmethod
    def count_users_today(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM users
                WHERE DATE(created_at) = CURRENT_DATE
                """
            )
            or 0
        )

    @staticmethod
    def count_users_this_week(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM users
                WHERE
                    """ + same_iso_week_as_today("created_at") + """
                """
            )
            or 0
        )

    @staticmethod
    def count_users_this_month(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM users
                WHERE
                    EXTRACT(YEAR FROM created_at)
                    =
                    EXTRACT(YEAR FROM CURRENT_DATE)

                    AND

                    EXTRACT(MONTH FROM created_at)
                    =
                    EXTRACT(MONTH FROM CURRENT_DATE)
                """
            )
            or 0
        )

    # =====================================================
    # BARBERÍAS
    # =====================================================

    @staticmethod
    def count_barbershops(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM barbershops
                """
            )
            or 0
        )

    @staticmethod
    def count_active_barbershops(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM barbershops
                WHERE is_active = TRUE
                """
            )
            or 0
        )

    @staticmethod
    def count_new_barbershops_this_month(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM barbershops
                WHERE
                    EXTRACT(YEAR FROM created_at)
                    =
                    EXTRACT(YEAR FROM CURRENT_DATE)

                    AND

                    EXTRACT(MONTH FROM created_at)
                    =
                    EXTRACT(MONTH FROM CURRENT_DATE)
                """
            )
            or 0
        )

    # =====================================================
    # RESERVAS
    # =====================================================

    @staticmethod
    def count_bookings(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM bookings
                """
            )
            or 0
        )

    @staticmethod
    def count_bookings_today(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM bookings
                WHERE DATE(created_at) = CURRENT_DATE
                """
            )
            or 0
        )

    @staticmethod
    def count_bookings_this_week(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM bookings
                WHERE
                    """ + same_iso_week_as_today("created_at") + """
                """
            )
            or 0
        )

    @staticmethod
    def count_bookings_this_month(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)
                FROM bookings
                WHERE
                    EXTRACT(YEAR FROM created_at)
                    =
                    EXTRACT(YEAR FROM CURRENT_DATE)

                    AND

                    EXTRACT(MONTH FROM created_at)
                    =
                    EXTRACT(MONTH FROM CURRENT_DATE)
                """
            )
            or 0
        )

    # =====================================================
    # RESERVAS POR ESTADO
    # =====================================================

    @staticmethod
    def booking_status_counts(
        db: Session
    ) -> dict:

        rows = (
            db.execute(
                text(
                    """
                    SELECT
                        bs.code AS status_code,
                        COUNT(*) AS total

                    FROM bookings b

                    INNER JOIN booking_statuses bs
                        ON bs.id = b.status_id

                    GROUP BY
                        bs.code
                    """
                )
            )
            .mappings()
            .all()
        )

        result = {}

        for row in rows:

            code = str(
                row["status_code"]
            ).upper()

            result[code] = int(
                row["total"]
            )

        return result

    # =====================================================
    # FINANCIERO OPERATIVO
    # =====================================================

    @staticmethod
    def financial_summary(
        db: Session
    ) -> dict:

        row = (
            db.execute(
                text(
                    """
                    SELECT

                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS reserved_value,


                        COALESCE(
                            AVG(
                                CASE

                                    WHEN bs.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE NULL

                                END
                            ),
                            0
                        )
                        AS average_ticket


                    FROM bookings b

                    INNER JOIN booking_statuses bs
                        ON bs.id = b.status_id
                    """
                )
            )
            .mappings()
            .first()
        )

        if not row:

            return {
                "reserved_value": 0,
                "average_ticket": 0
            }

        return {

            "reserved_value":
                float(
                    row[
                        "reserved_value"
                    ]
                    or 0
                ),

            "average_ticket":
                float(
                    row[
                        "average_ticket"
                    ]
                    or 0
                )

        }

    # =====================================================
    # SIMULACIÓN FINANCIERA
    # =====================================================

    @staticmethod
    def financial_simulation_base(
        db: Session
    ) -> dict:

        row = (
            db.execute(
                text(
                    """
                    SELECT

                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS gross_booking_value,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code = 'COMPLETED'

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS completed_value,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code IN (
                                        'CANCELLED_BY_CUSTOMER',
                                        'CANCELLED_BY_BARBER',
                                        'CANCELLED_BY_ADMIN'
                                    )

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS cancelled_value,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code = 'NO_SHOW'

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS no_show_value,


                        COALESCE(
                            SUM(
                                CASE

                                    WHEN bs.code = 'REJECTED'

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS rejected_value


                    FROM bookings b

                    INNER JOIN booking_statuses bs
                        ON bs.id = b.status_id
                    """
                )
            )
            .mappings()
            .first()
        )

        if not row:

            return {

                "gross_booking_value":
                    0,

                "completed_value":
                    0,

                "cancelled_value":
                    0,

                "no_show_value":
                    0,

                "rejected_value":
                    0

            }

        return {

            "gross_booking_value":
                float(
                    row[
                        "gross_booking_value"
                    ]
                    or 0
                ),

            "completed_value":
                float(
                    row[
                        "completed_value"
                    ]
                    or 0
                ),

            "cancelled_value":
                float(
                    row[
                        "cancelled_value"
                    ]
                    or 0
                ),

            "no_show_value":
                float(
                    row[
                        "no_show_value"
                    ]
                    or 0
                ),

            "rejected_value":
                float(
                    row[
                        "rejected_value"
                    ]
                    or 0
                )

        }

    # =====================================================
    # VALOR RESERVADO HOY
    # =====================================================

    @staticmethod
    def reserved_value_today(
        db: Session
    ) -> float:

        value = (
            AdminRepository._scalar(
                db,
                """
                SELECT

                    COALESCE(
                        SUM(
                            CASE

                                WHEN bs.code IN (
                                    'PENDING',
                                    'CONFIRMED',
                                    'IN_PROGRESS',
                                    'COMPLETED'
                                )

                                THEN b.service_price

                                ELSE 0

                            END
                        ),
                        0
                    )

                FROM bookings b

                INNER JOIN booking_statuses bs
                    ON bs.id = b.status_id

                WHERE
                    DATE(b.created_at)
                    =
                    CURRENT_DATE
                """
            )
        )

        return float(
            value
            or 0
        )

    # =====================================================
    # VALOR RESERVADO ESTE MES
    # =====================================================

    @staticmethod
    def reserved_value_this_month(
        db: Session
    ) -> float:

        value = (
            AdminRepository._scalar(
                db,
                """
                SELECT

                    COALESCE(
                        SUM(
                            CASE

                                WHEN bs.code IN (
                                    'PENDING',
                                    'CONFIRMED',
                                    'IN_PROGRESS',
                                    'COMPLETED'
                                )

                                THEN b.service_price

                                ELSE 0

                            END
                        ),
                        0
                    )

                FROM bookings b

                INNER JOIN booking_statuses bs
                    ON bs.id = b.status_id

                WHERE
                    EXTRACT(YEAR FROM b.created_at)
                    =
                    EXTRACT(YEAR FROM CURRENT_DATE)

                    AND

                    EXTRACT(MONTH FROM b.created_at)
                    =
                    EXTRACT(MONTH FROM CURRENT_DATE)
                """
            )
        )

        return float(
            value
            or 0
        )

    # =====================================================
    # VALOR COMPLETADO ESTE MES
    # =====================================================

    @staticmethod
    def completed_value_this_month(
        db: Session
    ) -> float:

        value = (
            AdminRepository._scalar(
                db,
                """
                SELECT

                    COALESCE(
                        SUM(
                            b.service_price
                        ),
                        0
                    )

                FROM bookings b

                INNER JOIN booking_statuses bs
                    ON bs.id = b.status_id

                WHERE
                    bs.code = 'COMPLETED'

                    AND

                    EXTRACT(YEAR FROM b.created_at)
                    =
                    EXTRACT(YEAR FROM CURRENT_DATE)

                    AND

                    EXTRACT(MONTH FROM b.created_at)
                    =
                    EXTRACT(MONTH FROM CURRENT_DATE)
                """
            )
        )

        return float(
            value
            or 0
        )

    # =====================================================
    # USUARIOS ÚLTIMOS 30 DÍAS
    # =====================================================

    @staticmethod
    def users_growth_last_30_days(
        db: Session
    ) -> list[dict]:

        rows = (
            db.execute(
                text(
                    """
                    SELECT
                        DATE(created_at) AS date,
                        COUNT(*) AS total

                    FROM users

                    WHERE
                        created_at
                        >=
                        """ + days_ago(29) + """

                    GROUP BY
                        DATE(created_at)

                    ORDER BY
                        DATE(created_at)
                    """
                )
            )
            .mappings()
            .all()
        )

        return [

            {
                "date":
                    str(
                        row[
                            "date"
                        ]
                    ),

                "total":
                    int(
                        row[
                            "total"
                        ]
                    )
            }

            for row in rows
        ]

    # =====================================================
    # RESERVAS ÚLTIMOS 30 DÍAS
    # =====================================================

    @staticmethod
    def bookings_growth_last_30_days(
        db: Session
    ) -> list[dict]:

        rows = (
            db.execute(
                text(
                    """
                    SELECT
                        DATE(created_at) AS date,
                        COUNT(*) AS total

                    FROM bookings

                    WHERE
                        created_at
                        >=
                        """ + days_ago(29) + """

                    GROUP BY
                        DATE(created_at)

                    ORDER BY
                        DATE(created_at)
                    """
                )
            )
            .mappings()
            .all()
        )

        return [

            {
                "date":
                    str(
                        row[
                            "date"
                        ]
                    ),

                "total":
                    int(
                        row[
                            "total"
                        ]
                    )
            }

            for row in rows
        ]

    # =====================================================
    # TOP BARBERÍAS POR NÚMERO DE RESERVAS
    # =====================================================

    @staticmethod
    def top_barbershops(
        db: Session,
        limit: int = 5
    ) -> list[dict]:

        rows = (
            db.execute(
                text(
                    """
                    SELECT

                        bs.id AS barbershop_id,

                        bs.name AS barbershop_name,

                        COUNT(
                            b.id
                        )
                        AS bookings_count,

                        COALESCE(
                            SUM(
                                CASE

                                    WHEN st.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN b.service_price

                                    ELSE 0

                                END
                            ),
                            0
                        )
                        AS reserved_value


                    FROM barbershops bs

                    LEFT JOIN bookings b
                        ON b.barbershop_id = bs.id

                    LEFT JOIN booking_statuses st
                        ON st.id = b.status_id


                    GROUP BY

                        bs.id,
                        bs.name


                    ORDER BY

                        bookings_count DESC,
                        reserved_value DESC


                    LIMIT :limit
                    """
                ),
                {
                    "limit":
                        limit
                }
            )
            .mappings()
            .all()
        )

        return [

            {

                "barbershop_id":
                    int(
                        row[
                            "barbershop_id"
                        ]
                    ),

                "barbershop_name":
                    row[
                        "barbershop_name"
                    ],

                "bookings_count":
                    int(
                        row[
                            "bookings_count"
                        ]
                    ),

                "reserved_value":
                    float(
                        row[
                            "reserved_value"
                        ]
                        or 0
                    )

            }

            for row in rows
        ]

    # =====================================================
    # SERVICIOS MÁS RESERVADOS
    # =====================================================

    @staticmethod
    def top_services(
        db: Session,
        limit: int = 5
    ) -> list[dict]:

        rows = (
            db.execute(
                text(
                    """
                    SELECT

                        s.id AS service_id,

                        s.name AS service_name,

                        COUNT(
                            b.id
                        )
                        AS bookings_count,

                        COALESCE(
                            SUM(
                                b.service_price
                            ),
                            0
                        )
                        AS booked_value


                    FROM services s

                    LEFT JOIN bookings b
                        ON b.service_id = s.id


                    GROUP BY

                        s.id,
                        s.name


                    ORDER BY

                        bookings_count DESC,
                        booked_value DESC


                    LIMIT :limit
                    """
                ),
                {
                    "limit":
                        limit
                }
            )
            .mappings()
            .all()
        )

        return [

            {

                "service_id":
                    int(
                        row[
                            "service_id"
                        ]
                    ),

                "service_name":
                    row[
                        "service_name"
                    ],

                "bookings_count":
                    int(
                        row[
                            "bookings_count"
                        ]
                    ),

                "booked_value":
                    float(
                        row[
                            "booked_value"
                        ]
                        or 0
                    )

            }

            for row in rows
        ]

    # =====================================================
    # BARBEROS CON MAYOR NÚMERO DE RESERVAS
    # =====================================================

    @staticmethod
    def top_barbers(
        db: Session,
        limit: int = 5
    ) -> list[dict]:

        rows = (
            db.execute(
                text(
                    """
                    SELECT

                        br.id AS barber_id,

                        COUNT(
                            b.id
                        )
                        AS bookings_count,

                        COALESCE(
                            SUM(
                                b.service_price
                            ),
                            0
                        )
                        AS booked_value


                    FROM barbers br

                    LEFT JOIN bookings b
                        ON b.barber_id = br.id


                    GROUP BY

                        br.id


                    ORDER BY

                        bookings_count DESC,
                        booked_value DESC


                    LIMIT :limit
                    """
                ),
                {
                    "limit":
                        limit
                }
            )
            .mappings()
            .all()
        )

        return [

            {

                "barber_id":
                    int(
                        row[
                            "barber_id"
                        ]
                    ),

                "bookings_count":
                    int(
                        row[
                            "bookings_count"
                        ]
                    ),

                "booked_value":
                    float(
                        row[
                            "booked_value"
                        ]
                        or 0
                    )

            }

            for row in rows
        ]

    # =====================================================
    # CLIENTES ÚNICOS
    # =====================================================

    @staticmethod
    def count_unique_customers(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT
                    COUNT(
                        DISTINCT client_user_id
                    )

                FROM bookings
                """
            )
            or 0
        )

    # =====================================================
    # CLIENTES RECURRENTES
    # =====================================================

    @staticmethod
    def count_returning_customers(
        db: Session
    ) -> int:

        return int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)

                FROM (

                    SELECT
                        client_user_id

                    FROM bookings

                    GROUP BY
                        client_user_id

                    HAVING
                        COUNT(*) > 1

                ) AS returning_customers
                """
            )
            or 0
        )

    # =====================================================
    # TASA DE CANCELACIÓN
    # =====================================================

    @staticmethod
    def cancellation_rate(
        db: Session
    ) -> float:

        total = (
            AdminRepository
            .count_bookings(
                db
            )
        )

        if total == 0:

            return 0.0

        cancelled = int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)

                FROM bookings b

                INNER JOIN booking_statuses bs
                    ON bs.id = b.status_id

                WHERE
                    bs.code IN (
                        'CANCELLED_BY_CUSTOMER',
                        'CANCELLED_BY_BARBER',
                        'CANCELLED_BY_ADMIN'
                    )
                """
            )
            or 0
        )

        return round(
            (
                cancelled
                /
                total
            )
            *
            100,
            2
        )

    # =====================================================
    # TASA NO SHOW
    # =====================================================

    @staticmethod
    def no_show_rate(
        db: Session
    ) -> float:

        total = (
            AdminRepository
            .count_bookings(
                db
            )
        )

        if total == 0:

            return 0.0

        no_show = int(
            AdminRepository._scalar(
                db,
                """
                SELECT COUNT(*)

                FROM bookings b

                INNER JOIN booking_statuses bs
                    ON bs.id = b.status_id

                WHERE
                    bs.code = 'NO_SHOW'
                """
            )
            or 0
        )

        return round(
            (
                no_show
                /
                total
            )
            *
            100,
            2
        )

    # =====================================================
    # ADMIN - USUARIOS
    # =====================================================

    @staticmethod
    def list_users_admin(
        db: Session,
        search: str | None = None,
        role_filter: str = "all",
        status_filter: str = "all",
        limit: int = 100,
        offset: int = 0
    ) -> dict:

        conditions = []

        params = {
            "limit": limit,
            "offset": offset
        }

        # =================================================
        # BÚSQUEDA
        # =================================================

        if (
            search
            and
            search.strip()
        ):

            params["search"] = (
                f"%{search.strip().lower()}%"
            )

            conditions.append(
                """
                (
                    LOWER(
                        COALESCE(
                            u.first_name,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            u.last_name,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        CONCAT(
                            COALESCE(
                                u.first_name,
                                ''
                            ),
                            ' ',
                            COALESCE(
                                u.last_name,
                                ''
                            )
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            u.email,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            u.phone,
                            ''
                        )
                    )
                    LIKE :search
                )
                """
            )

        # =================================================
        # ROL
        # =================================================

        if (
            role_filter
            and
            role_filter != "all"
        ):

            params["role_filter"] = (
                role_filter.upper()
            )

            conditions.append(
                """
                EXISTS (
                    SELECT 1

                    FROM user_roles ur_filter

                    INNER JOIN roles r_filter
                        ON r_filter.id =
                            ur_filter.role_id

                    WHERE
                        ur_filter.user_id =
                            u.id

                        AND

                        UPPER(
                            r_filter.name
                        ) =
                            :role_filter
                )
                """
            )

        # =================================================
        # ESTADO
        # =================================================

        if (
            status_filter ==
            "active"
        ):

            conditions.append(
                "u.is_active = TRUE"
            )

        elif (
            status_filter ==
            "inactive"
        ):

            conditions.append(
                "u.is_active = FALSE"
            )

        # =================================================
        # WHERE
        # =================================================

        where_clause = ""

        if conditions:

            where_clause = (
                "WHERE "
                +
                " AND ".join(
                    conditions
                )
            )

        # =================================================
        # TOTAL FILTRADO
        # =================================================

        total = (
            db.execute(
                text(
                    f"""
                    SELECT
                        COUNT(*)

                    FROM users u

                    {where_clause}
                    """
                ),
                params
            )
            .scalar()
        )

        # =================================================
        # RESUMEN GLOBAL
        # =================================================

        summary_row = (
            db.execute(
                text(
                    """
                    SELECT

                        COUNT(*)
                            AS total,

                        SUM(
                            CASE
                                WHEN is_active = TRUE
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS active,

                        SUM(
                            CASE
                                WHEN is_active = FALSE
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS inactive,

                        SUM(
                            CASE

                                WHEN
                                    EXTRACT(YEAR FROM created_at) =
                                    EXTRACT(YEAR FROM CURRENT_DATE)

                                    AND

                                    EXTRACT(MONTH FROM created_at) =
                                    EXTRACT(MONTH FROM CURRENT_DATE)

                                THEN 1

                                ELSE 0

                            END
                        )
                            AS new_this_month

                    FROM users
                    """
                )
            )
            .mappings()
            .first()
        )

        # =================================================
        # CONTEO POR ROLES
        # =================================================

        role_rows = (
            db.execute(
                text(
                    """
                    SELECT

                        UPPER(r.name)
                            AS role_name,

                        COUNT(
                            DISTINCT ur.user_id
                        )
                            AS total

                    FROM user_roles ur

                    INNER JOIN roles r
                        ON r.id =
                            ur.role_id

                    GROUP BY
                        UPPER(r.name)
                    """
                )
            )
            .mappings()
            .all()
        )

        role_counts = {

            "CLIENT": 0,

            "BARBER": 0,

            "BARBERSHOP_ADMIN": 0,

            "PLATFORM_ADMIN": 0

        }

        for role_row in role_rows:

            role_name = (
                role_row[
                    "role_name"
                ]
                or
                ""
            )

            if (
                role_name
                in
                role_counts
            ):

                role_counts[
                    role_name
                ] = int(
                    role_row[
                        "total"
                    ]
                    or 0
                )

        # =================================================
        # LISTADO
        # =================================================

        rows = (
            db.execute(
                text(
                    f"""
                    SELECT

                        u.id,

                        u.first_name,

                        u.last_name,

                        u.email,

                        u.phone,

                        u.email_verified,

                        u.phone_verified,

                        u.is_active,

                        u.created_at,

                        u.updated_at,

                        role_data.roles,

                        COALESCE(
                            booking_data.bookings_count,
                            0
                        )
                            AS bookings_count,

                        COALESCE(
                            booking_data.completed_bookings,
                            0
                        )
                            AS completed_bookings,

                        COALESCE(
                            booking_data.cancelled_bookings,
                            0
                        )
                            AS cancelled_bookings,

                        COALESCE(
                            booking_data.booked_value,
                            0
                        )
                            AS booked_value,

                        booking_data.last_booking_at


                    FROM users u


                    LEFT JOIN (

                        SELECT

                            ur.user_id,

                            {string_agg_distinct("r.name")}
                                AS roles

                        FROM user_roles ur

                        INNER JOIN roles r
                            ON r.id =
                                ur.role_id

                        GROUP BY
                            ur.user_id

                    ) role_data

                        ON role_data.user_id =
                            u.id


                    LEFT JOIN (

                        SELECT

                            b.client_user_id
                                AS user_id,

                            COUNT(*)
                                AS bookings_count,

                            SUM(
                                CASE

                                    WHEN st.code =
                                        'COMPLETED'

                                    THEN 1

                                    ELSE 0

                                END
                            )
                                AS completed_bookings,

                            SUM(
                                CASE

                                    WHEN st.code IN (
                                        'CANCELLED_BY_CUSTOMER',
                                        'CANCELLED_BY_BARBER',
                                        'CANCELLED_BY_ADMIN'
                                    )

                                    THEN 1

                                    ELSE 0

                                END
                            )
                                AS cancelled_bookings,

                            COALESCE(
                                SUM(
                                    CASE

                                        WHEN st.code IN (
                                            'PENDING',
                                            'CONFIRMED',
                                            'IN_PROGRESS',
                                            'COMPLETED'
                                        )

                                        THEN
                                            b.service_price

                                        ELSE 0

                                    END
                                ),
                                0
                            )
                                AS booked_value,

                            MAX(
                                b.start_at
                            )
                                AS last_booking_at

                        FROM bookings b

                        INNER JOIN booking_statuses st
                            ON st.id =
                                b.status_id

                        GROUP BY
                            b.client_user_id

                    ) booking_data

                        ON booking_data.user_id =
                            u.id


                    {where_clause}


                    ORDER BY

                        u.created_at DESC,
                        u.id DESC


                    LIMIT :limit
                    OFFSET :offset
                    """
                ),
                params
            )
            .mappings()
            .all()
        )

        items = []

        for row in rows:

            raw_roles = (
                row["roles"]
                or
                ""
            )

            roles = [

                role.strip()

                for role
                in raw_roles.split(",")

                if role.strip()

            ]

            first_name = (
                row["first_name"]
                or
                ""
            )

            last_name = (
                row["last_name"]
                or
                ""
            )

            full_name = (
                f"{first_name} {last_name}"
                .strip()
            )

            items.append(
                {

                    "id":
                        int(
                            row["id"]
                        ),

                    "first_name":
                        row[
                            "first_name"
                        ],

                    "last_name":
                        row[
                            "last_name"
                        ],

                    "full_name":
                        (
                            full_name
                            or
                            row["email"]
                        ),

                    "email":
                        row["email"],

                    "phone":
                        row["phone"],

                    "email_verified":
                        bool(
                            row[
                                "email_verified"
                            ]
                        ),

                    "phone_verified":
                        bool(
                            row[
                                "phone_verified"
                            ]
                        ),

                    "is_active":
                        bool(
                            row[
                                "is_active"
                            ]
                        ),

                    "roles":
                        roles,

                    "created_at":
                        (
                            row[
                                "created_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "created_at"
                            ]
                            else
                            None
                        ),

                    "updated_at":
                        (
                            row[
                                "updated_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "updated_at"
                            ]
                            else
                            None
                        ),

                    "bookings_count":
                        int(
                            row[
                                "bookings_count"
                            ]
                            or 0
                        ),

                    "completed_bookings":
                        int(
                            row[
                                "completed_bookings"
                            ]
                            or 0
                        ),

                    "cancelled_bookings":
                        int(
                            row[
                                "cancelled_bookings"
                            ]
                            or 0
                        ),

                    "booked_value":
                        float(
                            row[
                                "booked_value"
                            ]
                            or 0
                        ),

                    "last_booking_at":
                        (
                            row[
                                "last_booking_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "last_booking_at"
                            ]
                            else
                            None
                        )

                }
            )

        return {

            "summary": {

                "total":
                    int(
                        summary_row[
                            "total"
                        ]
                        or 0
                    ),

                "active":
                    int(
                        summary_row[
                            "active"
                        ]
                        or 0
                    ),

                "inactive":
                    int(
                        summary_row[
                            "inactive"
                        ]
                        or 0
                    ),

                "new_this_month":
                    int(
                        summary_row[
                            "new_this_month"
                        ]
                        or 0
                    ),

                "clients":
                    role_counts[
                        "CLIENT"
                    ],

                "barbers":
                    role_counts[
                        "BARBER"
                    ],

                "barbershop_admins":
                    role_counts[
                        "BARBERSHOP_ADMIN"
                    ],

                "platform_admins":
                    role_counts[
                        "PLATFORM_ADMIN"
                    ]

            },

            "total":
                int(
                    total
                    or 0
                ),

            "limit":
                limit,

            "offset":
                offset,

            "items":
                items

        }

    # =====================================================
    # ACTIVAR / INHABILITAR USUARIO
    # =====================================================

    @staticmethod
    def update_user_status(
        db: Session,
        user_id: int,
        is_active: bool
    ) -> User | None:

        # -------------------------------------------------
        # BUSCAR USUARIO
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        # -------------------------------------------------
        # USUARIO NO EXISTE
        # -------------------------------------------------

        if user is None:

            return None

        # -------------------------------------------------
        # ACTUALIZAR ESTADO
        # -------------------------------------------------

        user.is_active = is_active

        # -------------------------------------------------
        # GUARDAR CAMBIO
        # -------------------------------------------------

        try:

            db.commit()

            db.refresh(
                user
            )

        except Exception:

            db.rollback()

            raise

        return user

    # =====================================================
    # ADMIN - LISTADO DE RESERVAS
    # =====================================================

    @staticmethod
    def list_bookings_admin(
        db: Session,
        search: str | None = None,
        status_filter: str = "all",
        barbershop_id: int | None = None,
        barber_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:

        conditions = []

        params = {
            "limit": limit,
            "offset": offset
        }

        # =================================================
        # BÚSQUEDA
        # =================================================

        if (
            search
            and
            search.strip()
        ):

            params["search"] = (
                f"%{search.strip().lower()}%"
            )

            conditions.append(
                """
                (
                    LOWER(
                        CONCAT(
                            COALESCE(
                                client.first_name,
                                ''
                            ),
                            ' ',
                            COALESCE(
                                client.last_name,
                                ''
                            )
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            client.email,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            client.phone,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            shop.name,
                            ''
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        CONCAT(
                            COALESCE(
                                barber_user.first_name,
                                ''
                            ),
                            ' ',
                            COALESCE(
                                barber_user.last_name,
                                ''
                            )
                        )
                    )
                    LIKE :search

                    OR

                    LOWER(
                        COALESCE(
                            service.name,
                            ''
                        )
                    )
                    LIKE :search
                )
                """
            )

        # =================================================
        # ESTADO
        # =================================================

        if (
            status_filter
            and
            status_filter != "all"
        ):

            params["status_filter"] = (
                status_filter.upper()
            )

            conditions.append(
                """
                UPPER(
                    booking_status.code
                )
                =
                :status_filter
                """
            )

        # =================================================
        # BARBERÍA
        # =================================================

        if (
            barbershop_id
            is not None
        ):

            params["barbershop_id"] = (
                barbershop_id
            )

            conditions.append(
                """
                b.barbershop_id =
                :barbershop_id
                """
            )

        # =================================================
        # BARBERO
        # =================================================

        if (
            barber_id
            is not None
        ):

            params["barber_id"] = (
                barber_id
            )

            conditions.append(
                """
                b.barber_id =
                :barber_id
                """
            )

        # =================================================
        # FECHA DESDE
        # =================================================

        if date_from:

            params["date_from"] = (
                date_from
            )

            conditions.append(
                """
                DATE(
                    b.start_at
                )
                >=
                :date_from
                """
            )

        # =================================================
        # FECHA HASTA
        # =================================================

        if date_to:

            params["date_to"] = (
                date_to
            )

            conditions.append(
                """
                DATE(
                    b.start_at
                )
                <=
                :date_to
                """
            )

        # =================================================
        # WHERE
        # =================================================

        where_clause = ""

        if conditions:

            where_clause = (
                "WHERE "
                +
                " AND ".join(
                    conditions
                )
            )

        # =================================================
        # JOINS BASE
        # =================================================

        base_query = """
            FROM bookings b

            INNER JOIN users client
                ON client.id =
                    b.client_user_id

            INNER JOIN barbershops shop
                ON shop.id =
                    b.barbershop_id

            INNER JOIN barbers barber
                ON barber.id =
                    b.barber_id

            INNER JOIN users barber_user
                ON barber_user.id =
                    barber.user_id

            INNER JOIN services service
                ON service.id =
                    b.service_id

            INNER JOIN booking_statuses booking_status
                ON booking_status.id =
                    b.status_id
        """

        # =================================================
        # TOTAL FILTRADO
        # =================================================

        total = (
            db.execute(
                text(
                    f"""
                    SELECT
                        COUNT(*)

                    {base_query}

                    {where_clause}
                    """
                ),
                params
            )
            .scalar()
        )

        # =================================================
        # MÉTRICAS GENERALES
        # =================================================

        summary_row = (
            db.execute(
                text(
                    """
                    SELECT

                        COUNT(*)
                            AS total,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'PENDING'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS pending,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'CONFIRMED'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS confirmed,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'IN_PROGRESS'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS in_progress,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'COMPLETED'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS completed,

                        SUM(
                            CASE
                                WHEN bs.code IN (
                                    'CANCELLED_BY_CUSTOMER',
                                    'CANCELLED_BY_BARBER',
                                    'CANCELLED_BY_ADMIN'
                                )
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS cancelled,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'REJECTED'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS rejected,

                        SUM(
                            CASE
                                WHEN bs.code =
                                    'NO_SHOW'
                                THEN 1
                                ELSE 0
                            END
                        )
                            AS no_show,

                        SUM(
                            CASE
                                WHEN DATE(
                                    b.start_at
                                ) =
                                CURRENT_DATE

                                THEN 1
                                ELSE 0
                            END
                        )
                            AS today,

                        COALESCE(
                            SUM(
                                CASE
                                    WHEN bs.code IN (
                                        'PENDING',
                                        'CONFIRMED',
                                        'IN_PROGRESS',
                                        'COMPLETED'
                                    )

                                    THEN
                                        b.service_price

                                    ELSE 0
                                END
                            ),
                            0
                        )
                            AS reserved_value

                    FROM bookings b

                    INNER JOIN booking_statuses bs
                        ON bs.id =
                            b.status_id
                    """
                )
            )
            .mappings()
            .first()
        )

        # =================================================
        # LISTADO
        # =================================================

        rows = (
            db.execute(
                text(
                    f"""
                    SELECT

                        b.id,

                        b.client_user_id,

                        client.first_name
                            AS client_first_name,

                        client.last_name
                            AS client_last_name,

                        client.email
                            AS client_email,

                        client.phone
                            AS client_phone,


                        b.barbershop_id,

                        shop.name
                            AS barbershop_name,


                        b.barber_id,

                        barber_user.first_name
                            AS barber_first_name,

                        barber_user.last_name
                            AS barber_last_name,


                        b.service_id,

                        service.name
                            AS service_name,

                        service.duration_minutes
                            AS service_duration_minutes,


                        b.status_id,

                        booking_status.code
                            AS status_code,

                        booking_status.name
                            AS status_name,


                        b.start_at,

                        b.end_at,

                        b.service_price,

                        b.customer_notes,

                        b.barber_notes,

                        b.created_at,

                        b.updated_at


                    {base_query}


                    {where_clause}


                    ORDER BY

                        b.start_at DESC,

                        b.id DESC


                    LIMIT :limit
                    OFFSET :offset
                    """
                ),
                params
            )
            .mappings()
            .all()
        )

        # =================================================
        # SERIALIZAR
        # =================================================

        items = []

        for row in rows:

            client_first_name = (
                row[
                    "client_first_name"
                ]
                or
                ""
            )

            client_last_name = (
                row[
                    "client_last_name"
                ]
                or
                ""
            )

            client_full_name = (
                f"{client_first_name} "
                f"{client_last_name}"
            ).strip()

            barber_first_name = (
                row[
                    "barber_first_name"
                ]
                or
                ""
            )

            barber_last_name = (
                row[
                    "barber_last_name"
                ]
                or
                ""
            )

            barber_full_name = (
                f"{barber_first_name} "
                f"{barber_last_name}"
            ).strip()

            items.append(
                {

                    "id":
                        int(
                            row["id"]
                        ),

                    "client_user_id":
                        int(
                            row[
                                "client_user_id"
                            ]
                        ),

                    "client_first_name":
                        row[
                            "client_first_name"
                        ],

                    "client_last_name":
                        row[
                            "client_last_name"
                        ],

                    "client_full_name":
                        (
                            client_full_name
                            or
                            row[
                                "client_email"
                            ]
                        ),

                    "client_email":
                        row[
                            "client_email"
                        ],

                    "client_phone":
                        row[
                            "client_phone"
                        ],


                    "barbershop_id":
                        int(
                            row[
                                "barbershop_id"
                            ]
                        ),

                    "barbershop_name":
                        row[
                            "barbershop_name"
                        ],


                    "barber_id":
                        int(
                            row[
                                "barber_id"
                            ]
                        ),

                    "barber_first_name":
                        row[
                            "barber_first_name"
                        ],

                    "barber_last_name":
                        row[
                            "barber_last_name"
                        ],

                    "barber_full_name":
                        barber_full_name,


                    "service_id":
                        int(
                            row[
                                "service_id"
                            ]
                        ),

                    "service_name":
                        row[
                            "service_name"
                        ],

                    "service_duration_minutes":
                        int(
                            row[
                                "service_duration_minutes"
                            ]
                        ),


                    "status_id":
                        int(
                            row[
                                "status_id"
                            ]
                        ),

                    "status_code":
                        row[
                            "status_code"
                        ],

                    "status_name":
                        row[
                            "status_name"
                        ],


                    "start_at":
                        (
                            row[
                                "start_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "start_at"
                            ]
                            else
                            None
                        ),

                    "end_at":
                        (
                            row[
                                "end_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "end_at"
                            ]
                            else
                            None
                        ),

                    "service_price":
                        float(
                            row[
                                "service_price"
                            ]
                            or 0
                        ),

                    "customer_notes":
                        row[
                            "customer_notes"
                        ],

                    "barber_notes":
                        row[
                            "barber_notes"
                        ],

                    "created_at":
                        (
                            row[
                                "created_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "created_at"
                            ]
                            else
                            None
                        ),

                    "updated_at":
                        (
                            row[
                                "updated_at"
                            ]
                            .isoformat()
                            if
                            row[
                                "updated_at"
                            ]
                            else
                            None
                        )

                }
            )

        # =================================================
        # RESPUESTA
        # =================================================

        return {

            "summary": {

                "total":
                    int(
                        summary_row[
                            "total"
                        ]
                        or 0
                    ),

                "pending":
                    int(
                        summary_row[
                            "pending"
                        ]
                        or 0
                    ),

                "confirmed":
                    int(
                        summary_row[
                            "confirmed"
                        ]
                        or 0
                    ),

                "in_progress":
                    int(
                        summary_row[
                            "in_progress"
                        ]
                        or 0
                    ),

                "completed":
                    int(
                        summary_row[
                            "completed"
                        ]
                        or 0
                    ),

                "cancelled":
                    int(
                        summary_row[
                            "cancelled"
                        ]
                        or 0
                    ),

                "rejected":
                    int(
                        summary_row[
                            "rejected"
                        ]
                        or 0
                    ),

                "no_show":
                    int(
                        summary_row[
                            "no_show"
                        ]
                        or 0
                    ),

                "today":
                    int(
                        summary_row[
                            "today"
                        ]
                        or 0
                    ),

                "reserved_value":
                    float(
                        summary_row[
                            "reserved_value"
                        ]
                        or 0
                    )

            },

            "total":
                int(
                    total
                    or 0
                ),

            "limit":
                limit,

            "offset":
                offset,

            "items":
                items

        }

    # =====================================================
    # ADMIN - CANCELAR RESERVA
    # =====================================================

    @staticmethod
    def cancel_booking_admin(
        db: Session,
        booking_id: int
    ) -> dict | None:

        try:

            # -------------------------------------------------
            # BLOQUEAR Y CONSULTAR RESERVA
            # -------------------------------------------------

            booking = (
                db.execute(
                    text(
                        """
                        SELECT
                            b.id,
                            b.status_id,
                            bs.code AS status_code,
                            bs.name AS status_name

                        FROM bookings b

                        INNER JOIN booking_statuses bs
                            ON bs.id = b.status_id

                        WHERE
                            b.id = :booking_id

                        LIMIT 1

                        FOR UPDATE
                        """
                    ),
                    {
                        "booking_id":
                            booking_id
                    }
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # RESERVA NO EXISTE
            # -------------------------------------------------

            if not booking:

                db.rollback()

                return None

            current_status = (
                booking[
                    "status_code"
                ]
            )

            # -------------------------------------------------
            # ESTADOS QUE PUEDEN SER CANCELADOS
            # -------------------------------------------------

            allowed_statuses = {
                "PENDING",
                "CONFIRMED"
            }

            # -------------------------------------------------
            # ESTADO NO CANCELABLE
            # -------------------------------------------------

            if (
                current_status
                not in
                allowed_statuses
            ):

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "cancelled":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "INVALID_STATUS"

                }

            # -------------------------------------------------
            # BUSCAR ESTADO CANCELLED_BY_ADMIN
            # -------------------------------------------------

            cancelled_status = (
                db.execute(
                    text(
                        """
                        SELECT
                            id,
                            code,
                            name

                        FROM booking_statuses

                        WHERE
                            code =
                                'CANCELLED_BY_ADMIN'

                        LIMIT 1
                        """
                    )
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # ESTADO NO CONFIGURADO
            # -------------------------------------------------

            if not cancelled_status:

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "cancelled":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "ADMIN_STATUS_NOT_CONFIGURED"

                }

            # -------------------------------------------------
            # ACTUALIZAR RESERVA
            # -------------------------------------------------

            db.execute(
                text(
                    """
                    UPDATE bookings

                    SET
                        status_id =
                            :status_id,

                        updated_at =
                            CURRENT_TIMESTAMP

                    WHERE
                        id =
                            :booking_id
                    """
                ),
                {

                    "status_id":
                        int(
                            cancelled_status[
                                "id"
                            ]
                        ),

                    "booking_id":
                        booking_id

                }
            )

            # -------------------------------------------------
            # CONFIRMAR CAMBIO
            # -------------------------------------------------

            db.commit()

            # -------------------------------------------------
            # RESPUESTA
            # -------------------------------------------------

            return {

                "id":
                    int(
                        booking[
                            "id"
                        ]
                    ),

                "cancelled":
                    True,

                "status_id":
                    int(
                        cancelled_status[
                            "id"
                        ]
                    ),

                "status_code":
                    cancelled_status[
                        "code"
                    ],

                "status_name":
                    cancelled_status[
                        "name"
                    ]

            }

        except Exception:

            db.rollback()

            raise

    # =====================================================
    # ADMIN - CONFIRMAR RESERVA
    # =====================================================

    @staticmethod
    def confirm_booking_admin(
        db: Session,
        booking_id: int
    ) -> dict | None:

        try:

            # -------------------------------------------------
            # BLOQUEAR Y CONSULTAR RESERVA
            # -------------------------------------------------

            booking = (
                db.execute(
                    text(
                        """
                        SELECT
                            b.id,
                            b.status_id,
                            bs.code AS status_code,
                            bs.name AS status_name

                        FROM bookings b

                        INNER JOIN booking_statuses bs
                            ON bs.id = b.status_id

                        WHERE
                            b.id = :booking_id

                        LIMIT 1

                        FOR UPDATE
                        """
                    ),
                    {
                        "booking_id":
                            booking_id
                    }
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # RESERVA NO EXISTE
            # -------------------------------------------------

            if not booking:

                db.rollback()

                return None

            current_status = (
                booking[
                    "status_code"
                ]
            )

            # -------------------------------------------------
            # SOLO PENDING PUEDE SER CONFIRMADA
            # -------------------------------------------------

            if (
                current_status !=
                "PENDING"
            ):

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "confirmed":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "INVALID_STATUS"

                }

            # -------------------------------------------------
            # BUSCAR ESTADO CONFIRMED
            # -------------------------------------------------

            confirmed_status = (
                db.execute(
                    text(
                        """
                        SELECT
                            id,
                            code,
                            name

                        FROM booking_statuses

                        WHERE
                            code =
                                'CONFIRMED'

                        LIMIT 1
                        """
                    )
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # ESTADO NO CONFIGURADO
            # -------------------------------------------------

            if not confirmed_status:

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "confirmed":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "CONFIRMED_STATUS_NOT_CONFIGURED"

                }

            # -------------------------------------------------
            # ACTUALIZAR RESERVA
            # -------------------------------------------------

            db.execute(
                text(
                    """
                    UPDATE bookings

                    SET
                        status_id =
                            :status_id,

                        updated_at =
                            CURRENT_TIMESTAMP

                    WHERE
                        id =
                            :booking_id
                    """
                ),
                {

                    "status_id":
                        int(
                            confirmed_status[
                                "id"
                            ]
                        ),

                    "booking_id":
                        booking_id

                }
            )

            # -------------------------------------------------
            # CONFIRMAR TRANSACCIÓN
            # -------------------------------------------------

            db.commit()

            # -------------------------------------------------
            # RESPUESTA
            # -------------------------------------------------

            return {

                "id":
                    int(
                        booking[
                            "id"
                        ]
                    ),

                "confirmed":
                    True,

                "status_id":
                    int(
                        confirmed_status[
                            "id"
                        ]
                    ),

                "status_code":
                    confirmed_status[
                        "code"
                    ],

                "status_name":
                    confirmed_status[
                        "name"
                    ]

            }

        except Exception:

            db.rollback()

            raise

    # =====================================================
    # ADMIN - COMPLETAR RESERVA
    # =====================================================

    @staticmethod
    def complete_booking_admin(
        db: Session,
        booking_id: int
    ) -> dict | None:

        try:

            # -------------------------------------------------
            # CONSULTAR Y BLOQUEAR RESERVA
            # -------------------------------------------------

            booking = (
                db.execute(
                    text(
                        """
                        SELECT
                            b.id,
                            b.status_id,
                            bs.code AS status_code,
                            bs.name AS status_name

                        FROM bookings b

                        INNER JOIN booking_statuses bs
                            ON bs.id = b.status_id

                        WHERE
                            b.id = :booking_id

                        LIMIT 1

                        FOR UPDATE
                        """
                    ),
                    {
                        "booking_id":
                            booking_id
                    }
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # RESERVA NO ENCONTRADA
            # -------------------------------------------------

            if not booking:

                db.rollback()

                return None

            current_status = (
                booking[
                    "status_code"
                ]
            )

            # -------------------------------------------------
            # ESTADOS QUE PUEDEN PASAR A COMPLETED
            # -------------------------------------------------

            allowed_statuses = {
                "CONFIRMED",
                "IN_PROGRESS"
            }

            if (
                current_status
                not in
                allowed_statuses
            ):

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "completed":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "INVALID_STATUS"

                }

            # -------------------------------------------------
            # BUSCAR ESTADO COMPLETED
            # -------------------------------------------------

            completed_status = (
                db.execute(
                    text(
                        """
                        SELECT
                            id,
                            code,
                            name

                        FROM booking_statuses

                        WHERE
                            code = 'COMPLETED'

                        LIMIT 1
                        """
                    )
                )
                .mappings()
                .first()
            )

            # -------------------------------------------------
            # COMPLETED NO CONFIGURADO
            # -------------------------------------------------

            if not completed_status:

                db.rollback()

                return {

                    "id":
                        int(
                            booking[
                                "id"
                            ]
                        ),

                    "completed":
                        False,

                    "status_code":
                        booking[
                            "status_code"
                        ],

                    "status_name":
                        booking[
                            "status_name"
                        ],

                    "reason":
                        "COMPLETED_STATUS_NOT_CONFIGURED"

                }

            # -------------------------------------------------
            # ACTUALIZAR ESTADO
            # -------------------------------------------------

            db.execute(
                text(
                    """
                    UPDATE bookings

                    SET
                        status_id =
                            :status_id,

                        updated_at =
                            CURRENT_TIMESTAMP

                    WHERE
                        id =
                            :booking_id
                    """
                ),
                {

                    "status_id":
                        int(
                            completed_status[
                                "id"
                            ]
                        ),

                    "booking_id":
                        booking_id

                }
            )

            # -------------------------------------------------
            # CONFIRMAR TRANSACCIÓN
            # -------------------------------------------------

            db.commit()

            # -------------------------------------------------
            # RESPUESTA
            # -------------------------------------------------

            return {

                "id":
                    int(
                        booking[
                            "id"
                        ]
                    ),

                "completed":
                    True,

                "status_id":
                    int(
                        completed_status[
                            "id"
                        ]
                    ),

                "status_code":
                    completed_status[
                        "code"
                    ],

                "status_name":
                    completed_status[
                        "name"
                    ]

            }

        except Exception:

            db.rollback()

            raise