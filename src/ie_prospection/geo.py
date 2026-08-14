"""Calculs géographiques.

La distance renvoyée est une distance ORTHODROMIQUE (à vol d'oiseau) en
kilomètres. Elle ne doit JAMAIS être présentée comme un temps de transport.
"""
from __future__ import annotations

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance à vol d'oiseau (km) entre deux points WGS84."""
    r = 6371.0088  # rayon moyen de la Terre en km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def parse_coordinate(value) -> float | None:
    """Convertit une coordonnée en float, en conservant les valeurs vides
    comme None (on ne fabrique jamais de coordonnée)."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
