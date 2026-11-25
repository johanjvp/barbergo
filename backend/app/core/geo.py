from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Distancia en km entre dos coordenadas (línea recta)."""
    lat1, lon1, lat2, lon2 = (radians(float(v)) for v in (lat1, lon1, lat2, lon2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(a))
